import sys
import argparse
import asyncio
import numpy as np
from typing import Optional, Dict, Any
import time

import multirobot.registry
from multirobot.mocap import Vicon

from .trajectories import Trajectory
from .trajectories.lissajous import Lissajous
from .trajectories.circle import Circle
from .trajectories.position import Position

DISTANCE_THRESHOLD = 0.25
YAW_THRESHOLD = 20/180*np.pi


class PX4Commander:
    
    def __init__(self, url: str, mocap_url: Optional[str] = None, use_global: bool = False):
        self.url = url
        self.mocap_url = mocap_url
        self.client = None
        self.mocap = None
        
    async def initialize(self):
        if self.mocap_url:
            mocap_type, mocap_address = self._parse_mocap_url(self.mocap_url)
            if mocap_type == "vicon":
                self.mocap = Vicon(
                    mocap_address,
                    VELOCITY_CLIP=10,
                    ACCELERATION_FILTER=20,
                    ORIENTATION_FILTER=10,
                    EXPECTED_FRAMERATE=100
                )
            else:
                raise ValueError(f"Unsupported mocap type: {mocap_type}")
        
        config = self._create_config()
        
        if self.mocap:
            clients = multirobot.registry.make_clients(self.mocap, {"px4": config})
        else:
            clients = multirobot.registry.make_clients(None, {"px4": config})
        
        self.client = clients["px4"]
        
        print("Waiting for position and orientation...")
        while self.client.position is None or self.client.orientation is None:
            await asyncio.sleep(0.01)
    
    def _parse_mocap_url(self, url: str) -> tuple:
        parts = url.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid mocap URL format: {url}. Expected format: 'type:address'")
        return parts[0], parts[1]
    
    def _create_config(self) -> Dict[str, Any]:
        config = {
            "type": "px4",
            "kwargs": {
                "uri": self.url,
                "log_fields_state_additional": ["in_trajectory"],
                "odometry_source": "feedback",
                "setpoint_interval": 0.01
            },
            "mocap": "feedback"
        }
        return config
    
    async def track_trajectory(
        self,
        trajectory: Trajectory,
        takeoff_height: Optional[float] = None,
        n_iterations: int = 5,
        min_height_threshold: float = 0.5,
        use_global: bool = False,
    ):
        initial_position = self.client.position.copy()
        w, x, y, z = self.client.orientation
        initial_yaw = np.arctan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2))
        print(f"Initial position: {initial_position}, yaw: {initial_yaw}")
        
        if use_global:
            position_offset = np.array([0, 0, 0])
            yaw_offset = 0
        else:
            if takeoff_height is not None:
                print(f"Takeoff mode: will takeoff to {takeoff_height}m")
                takeoff_position = initial_position + np.array([0, 0, takeoff_height])
                position_offset = takeoff_position
                yaw_offset = initial_yaw
                await self.client.arm()
                print("Armed. Taking off...")
                await self.client.goto(takeoff_position, distance_threshold=DISTANCE_THRESHOLD, target_yaw=initial_yaw, yaw_threshold=YAW_THRESHOLD)
                print("Takeoff complete.")
            else:
                if initial_position[2] < min_height_threshold:
                    raise ValueError(
                        f"Current height ({initial_position[2]:.2f}m) is below minimum threshold "
                        f"({min_height_threshold}m). Either use --takeoff or manually fly higher."
                    )
                
                print(f"No takeoff specified. Using current position (height: {initial_position[2]:.2f}m)")
                position_offset = initial_position.copy()
                yaw_offset = initial_yaw
                
                await self.client.arm()
                print("Armed.")
        
        final_position, final_yaw = await self._execute_trajectory(trajectory, position_offset, yaw_offset, n_iterations)
        
        hover_time = time.time()
        # final_position = self.client.position.copy()
        # w, x, y, z = self.client.orientation
        # final_yaw = np.arctan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2))
        print(f"Trajectory complete. Hovering at {final_position} with yaw {final_yaw}")
        while time.time() - hover_time < 10:
            await self.client.goto(final_position, distance_threshold=DISTANCE_THRESHOLD, target_yaw=final_yaw, yaw_threshold=YAW_THRESHOLD, verbose=False)
            await asyncio.sleep(0.01)
        
        print("Landing...")
        landing_target = final_position.copy()
        # landing_target[2] = min(landing_target[2], 1.5)
        while True:
            await self.client.goto(landing_target, distance_threshold=DISTANCE_THRESHOLD, target_yaw=final_yaw, yaw_threshold=YAW_THRESHOLD, verbose=False)
            landing_target[2] -= 0.01
            landing_target[2] = max(landing_target[2], 0)
            await asyncio.sleep(0.01)
    
    async def _execute_trajectory(
        self, 
        trajectory: Trajectory, 
        position_offset: np.ndarray, 
        yaw_offset: float,
        n_iterations: int,
        ease_out_duration = 10
    ):
        start_pos, start_orientation, _, _ = trajectory.get_state(0.0)
        w, x, y, z = start_orientation
        target_yaw = yaw_offset + np.arctan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2))
        c, s = np.cos(yaw_offset), np.sin(yaw_offset)
        rotate_global_to_target = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        local_position = rotate_global_to_target @ start_pos + position_offset
        print(f"Moving to start position: {local_position} with yaw {target_yaw}")
        await self.client.goto(local_position, distance_threshold=DISTANCE_THRESHOLD, target_yaw=target_yaw, yaw_threshold=YAW_THRESHOLD)
        
        start_time = time.time()
        iteration = 0
        self.client.log_state_additional = {"in_trajectory": 1}
        
        while iteration < n_iterations:
            t = time.time() - start_time
            target_position, target_orientation, target_velocity, iteration = trajectory.get_state(t)

            local_position = rotate_global_to_target @ target_position
            local_velocity = rotate_global_to_target @ target_velocity

            w, x, y, z = target_orientation
            target_yaw = yaw_offset + np.arctan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2))

            
            if iteration != getattr(self, '_last_iteration', -1):
                print(f"Iteration: {iteration}/{n_iterations}")
                self._last_iteration = iteration
            
            local_position += position_offset
            self.client.command(local_position, local_velocity, yaw=target_yaw)
            await asyncio.sleep(0.01)
        self.client.log_state_additional = {"in_trajectory": 0}
        return target_position, target_yaw
        


def create_trajectory(trajectory_type: str, params) -> Trajectory:
    if trajectory_type == "lissajous":
        return Lissajous(**params)
    elif trajectory_type == "circle":
        return Circle(**params)
    elif trajectory_type == "position":
        return Position(**params)
    else:
        raise ValueError(f"Unknown trajectory type: {trajectory_type}")


async def async_main(args):
    commander = PX4Commander(args.url, args.mocap, getattr(args, "use_global", False))
    
    print("Initializing PX4 connection...")
    await commander.initialize()
    print("Connected successfully.")
    
    if args.command == "track":
        trajectory = create_trajectory(args.trajectory, vars(args))
        
        await commander.track_trajectory(trajectory=trajectory, takeoff_height=args.takeoff, n_iterations=args.iterations)


def main():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    
    parser.add_argument("url", help="PX4 connection URL (e.g., udp:localhost:14540, tcp:192.168.1.5:5760)")
    parser.add_argument("command", choices=["track"], help="Command to execute")
    parser.add_argument("trajectory", choices=["lissajous", "circle", "position"], help="Trajectory type")
    
    parser.add_argument("--mocap", type=str, default=None, help="Motion capture system (e.g., vicon:192.168.1.3)")
    parser.add_argument("--takeoff", type=float, default=None, help="Takeoff to specified height before executing trajectory")
    parser.add_argument("--iterations", type=int, default=5, help="Number of trajectory iterations (default: 5)")
    parser.add_argument("--global", dest="use_global", action="store_true", help="Use global coordinates (position and yaw) (default: local)")

    Lissajous.declare_arguments(parser)
    Circle.declare_arguments(parser)
    Position.declare_arguments(parser)
    
    
    args = parser.parse_args()
    
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
