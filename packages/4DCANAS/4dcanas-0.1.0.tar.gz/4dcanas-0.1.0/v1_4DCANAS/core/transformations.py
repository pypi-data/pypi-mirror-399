import numpy as np
from typing import List, Tuple
from .geometry import Point4D, Point3D
from .vectors import Vector4D
from .rotations import Rotation4D

class Tesseract: 
    """4-dimensional hypercube"""
    
    def __init__(self, center: Point4D = None, size: float = 1.0):
        self.center = center or Point4D(0, 0, 0, 0)
        self.size = size
        self.vertices = self._generate_vertices()
        self.edges = self._generate_edges()
    
    def _generate_vertices(self) -> List[Point4D]:
        vertices = []
        for x in [-1, 1]:
            for y in [-1, 1]: 
                for z in [-1, 1]:
                    for w in [-1, 1]:
                        point = Point4D(x, y, z, w) * (self.size / 2)
                        vertices.append(point + self.center)
        return vertices
    
    def _generate_edges(self) -> List[Tuple[int, int]]: 
        edges = []
        for i in range(len(self.vertices)):
            for j in range(i + 1, len(self. vertices)):
                diff = self.vertices[i] - self.vertices[j]
                distance = diff.distance_to(Point4D())
                if abs(distance - self.size) < 1e-6:
                    edges.append((i, j))
        return edges
    
    def rotate(self, angles: Union[Tuple[float, ...], np.ndarray]) -> None:
        rotation = Rotation4D(angles)
        self.vertices = [rotation.apply(v) for v in self.vertices]
    
    def translate(self, offset: Vector4D) -> None:
        self.center = self.center + Point4D(*offset. components)
        self.vertices = [v + Point4D(*offset.components) for v in self.vertices]
    
    def get_3d_projection(self, perspective: float = 1.0) -> Tuple[List[Point3D], List[Tuple[int, int]]]: 
        projected = [v.project_3d(perspective) for v in self.vertices]
        return projected, self.edges