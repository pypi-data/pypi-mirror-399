import numpy as np
from typing import Union

class Vector4D:
    """4-dimensional vector"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0):
        self.components = np.array([x, y, z, w], dtype=np.float64)
    
    def magnitude(self) -> float:
        return float(np.linalg.norm(self.components))
    
    def normalize(self) -> 'Vector4D':
        mag = self.magnitude()
        if mag == 0:
            return Vector4D()
        return Vector4D(*(self.components / mag))
    
    def dot(self, other: 'Vector4D') -> float:
        return float(np.dot(self.components, other.components))
    
    def __add__(self, other: 'Vector4D') -> 'Vector4D':
        return Vector4D(*(self.components + other. components))
    
    def __sub__(self, other: 'Vector4D') -> 'Vector4D':
        return Vector4D(*(self.components - other.components))
    
    def __mul__(self, scalar: float) -> 'Vector4D':
        return Vector4D(*(self.components * scalar))
    
    def __repr__(self) -> str:
        return f"Vector4D({self.components})"