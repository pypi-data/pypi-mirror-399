import numpy as np
from typing import Tuple
from . import Trajectory


class Circle(Trajectory):

    @classmethod
    def declare_arguments(cls, parser):
        parser.add_argument("--radius", type=float, help="Circle: radius in meters (default: 1.0)")
        parser.add_argument("--z", type=float, help="Height/Z coordinate in meters (default: 1.0)") if "--z" not in parser._option_string_actions else None
        parser.add_argument("--duration", type=float, help="Trajectory duration per iteration in seconds (lissajous default: 10.0, circle default: 6.5)") if "--duration" not in parser._option_string_actions else None
        parser.add_argument("--ramp-duration", type=float, dest="ramp_duration", help="Ramp up/down time in seconds (lissajous default: 3.0, circle default: 1.0)") if "--ramp-duration" not in parser._option_string_actions else None
    
    def __init__(self, radius: float = 1.0, z: float = 2.0, duration: float = 6.5, ramp_duration: float = 1.0):
        self.radius = radius
        self.z = z
        self.duration = duration
        self.ramp_duration = ramp_duration
    
    def get_state(self, t: float) -> Tuple[np.ndarray, np.ndarray, int]:
        time_velocity = min(t, self.ramp_duration) / self.ramp_duration if self.ramp_duration > 0 else 1
        ramp_time = time_velocity * min(t, self.ramp_duration) / 2
        progress = (ramp_time + max(0, t - self.ramp_duration)) * 2 * np.pi / self.duration
        d_progress = 2 * np.pi * time_velocity / self.duration
        
        x = self.radius * np.cos(progress)
        y = self.radius * np.sin(progress)
        vx = -self.radius * np.sin(progress) * d_progress
        vy = self.radius * np.cos(progress) * d_progress
        
        iteration = int(progress / (2 * np.pi))
        
        position = np.array([x, y, self.z])
        orientation = np.array([1.0, 0.0, 0.0, 0.0])
        velocity = np.array([vx, vy, 0.0])
        
        return position, orientation, velocity, iteration
    