import numpy as np
from typing import Tuple
from . import Trajectory


class Position(Trajectory):
    @classmethod
    def declare_arguments(cls, parser):
        parser.add_argument("--x", type=float, help="Position: X coordinate in meters (default: 0.0)")
        parser.add_argument("--y", type=float, help="Position: Y coordinate in meters (default: 0.0)")
        parser.add_argument("--z", type=float, help="Height/Z coordinate in meters (default: 1.0)") if "--z" not in parser._option_string_actions else None

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 2.0):
        self.x = x
        self.y = y
        self.z = z
    
    def get_state(self, t: float) -> Tuple[np.ndarray, np.ndarray, int]:
        position = np.array([self.x, self.y, self.z])
        orientation = np.array([1.0, 0.0, 0.0, 0.0])
        velocity = np.array([0.0, 0.0, 0.0])
        return position, orientation, velocity, 0