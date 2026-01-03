import numpy as np
from typing import Tuple
from . import Trajectory


class Lissajous(Trajectory):
    @classmethod
    def declare_arguments(cls, parser):
        parser.add_argument("--A", type=float, help="Lissajous: X amplitude in meters (default: 1.0)")
        parser.add_argument("--B", type=float, help="Lissajous: Y amplitude in meters (default: 0.5)")
        parser.add_argument("--z", type=float, help="Height/Z coordinate in meters (default: 1.0)") if "--z" not in parser._option_string_actions else None
        parser.add_argument("--duration", type=float, help="Trajectory duration per iteration in seconds (lissajous default: 10.0, circle default: 6.5)") if "--duration" not in parser._option_string_actions else None
        parser.add_argument("--ramp-duration", type=float, dest="ramp_duration", help="Ramp up/down time in seconds (lissajous default: 3.0, circle default: 1.0)") if "--ramp-duration" not in parser._option_string_actions else None
        
    
    def __init__(self, A: float = 1.0, B: float = 0.5, z: float = 0.0, duration: float = 10.0, ramp_duration: float = 3.0, **kwargs):
        self.A = A
        self.B = B
        self.z = z
        self.duration = duration
        self.ramp_duration = ramp_duration
        self.a = 1
        self.b = 2
    
    def get_state(self, t: float) -> Tuple[np.ndarray, np.ndarray, int]:
        time_velocity = min(t, self.ramp_duration) / self.ramp_duration if self.ramp_duration > 0 else 1
        ramp_time = time_velocity * min(t, self.ramp_duration) / 2
        progress = (ramp_time + max(0, t - self.ramp_duration)) * 2 * np.pi / self.duration
        d_progress = 2 * np.pi * time_velocity / self.duration
        
        x = self.A * np.sin(self.a * progress)
        y = self.B * np.sin(self.b * progress)
        vx = self.A * np.cos(self.a * progress) * self.a * d_progress
        vy = self.B * np.cos(self.b * progress) * self.b * d_progress
        
        iteration = int(progress / (2 * np.pi))
        
        position = np.array([x, y, self.z])
        # yaw = 45/180 * np.pi
        yaw = 0
        orientation = np.array([np.cos(yaw/2), 0.0, 0.0, np.sin(yaw/2)])
        velocity = np.array([vx, vy, 0.0])
        
        return position, orientation, velocity, iteration