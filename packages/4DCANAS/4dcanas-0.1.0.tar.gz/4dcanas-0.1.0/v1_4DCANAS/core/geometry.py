import numpy as np
from typing import Union, Tuple

class Point4D:
    """4-dimensional point in Euclidean space"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0):
        self. coords = np.array([x, y, z, w], dtype=np.float64)
    
    @property
    def x(self) -> float:
        return self.coords[0]
    
    @property
    def y(self) -> float:
        return self.coords[1]
    
    @property
    def z(self) -> float:
        return self.coords[2]
    
    @property
    def w(self) -> float:
        return self.coords[3]
    
    def project_3d(self, perspective:  float = 1.0) -> 'Point3D':
        scale = perspective / (1.0 + self.w / 100.0) if self.w != -perspective else 1.0
        return Point3D(self.x * scale, self.y * scale, self.z * scale)
    
    def rotate_4d(self, rotation_matrix: np.ndarray) -> 'Point4D':
        rotated = rotation_matrix @ self.coords
        return Point4D(*rotated)
    
    def distance_to(self, other:  'Point4D') -> float:
        return float(np.linalg.norm(self.coords - other.coords))
    
    def __add__(self, other: 'Point4D') -> 'Point4D':
        return Point4D(*(self.coords + other.coords))
    
    def __sub__(self, other: 'Point4D') -> 'Point4D':
        return Point4D(*(self.coords - other.coords))
    
    def __mul__(self, scalar: float) -> 'Point4D':
        return Point4D(*(self. coords * scalar))
    
    def __repr__(self) -> str:
        return f"Point4D(x={self.x:. 3f}, y={self.y:.3f}, z={self. z:.3f}, w={self.w:.3f})"


class Point3D:
    """3-dimensional point (projection from 4D)"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.coords = np.array([x, y, z], dtype=np.float64)
    
    @property
    def x(self) -> float:
        return self.coords[0]
    
    @property
    def y(self) -> float:
        return self.coords[1]
    
    @property
    def z(self) -> float:
        return self.coords[2]
    
    def __repr__(self) -> str:
        return f"Point3D(x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f})"