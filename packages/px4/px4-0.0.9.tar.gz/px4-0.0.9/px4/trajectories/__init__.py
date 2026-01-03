from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple


class Trajectory(ABC):
    
    @abstractmethod
    def get_state(self, t: float) -> Tuple[np.ndarray, np.ndarray, int]:
        pass

