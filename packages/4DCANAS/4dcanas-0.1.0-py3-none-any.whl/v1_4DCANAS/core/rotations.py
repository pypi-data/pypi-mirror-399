import numpy as np
from typing import Union, Tuple
from .geometry import Point4D

class Rotation4D:
    """4-dimensional rotation"""
    
    def __init__(self, angles: Union[Tuple[float, ... ], np.ndarray]):
        self.angles = np.array(angles, dtype=np.float64)
        self.matrix = self._compute_rotation_matrix()
    
    def _compute_rotation_matrix(self) -> np.ndarray:
        matrix = np.eye(4, dtype=np.float64)
        
        if len(self.angles) >= 1:
            c, s = np.cos(self. angles[0]), np.sin(self.angles[0])
            rx = np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])
            matrix = matrix @ rx
        
        if len(self.angles) >= 2:
            c, s = np.cos(self.angles[1]), np.sin(self.angles[1])
            ry = np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])
            matrix = matrix @ ry
        
        if len(self. angles) >= 3:
            c, s = np.cos(self.angles[2]), np.sin(self.angles[2])
            rz = np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
            matrix = matrix @ rz
        
        if len(self.angles) >= 4:
            c, s = np.cos(self.angles[3]), np.sin(self.angles[3])
            rw = np.array([[c, 0, 0, s], [0, 1, 0, 0], [0, 0, 1, 0], [-s, 0, 0, c]])
            matrix = matrix @ rw
        
        return matrix
    
    def apply(self, point: Point4D) -> Point4D:
        return point.rotate_4d(self.matrix)