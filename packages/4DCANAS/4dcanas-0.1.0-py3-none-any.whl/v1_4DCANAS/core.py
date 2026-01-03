import numpy as np
from typing import Tuple, List, Union
from scipy.spatial.transform import Rotation as ScipyRotation

class Point4D:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0):
        self.coords = np.array([x, y, z, w], dtype=np.float64)
    
    @property
    def x(self) -> float:
        return self. coords[0]
    
    @property
    def y(self) -> float:
        return self.coords[1]
    
    @property
    def z(self) -> float:
        return self.coords[2]
    
    @property
    def w(self) -> float:
        return self.coords[3]
    
    def project_3d(self, perspective: float = 1.0) -> 'Point3D':
        scale = perspective / (1.0 + self.w / 100.0) if self.w != -perspective else 1.0
        return Point3D(
            self. x * scale,
            self. y * scale,
            self. z * scale
        )
    
    def rotate_4d(self, rotation_matrix: np.ndarray) -> 'Point4D':
        rotated = rotation_matrix @ self.coords
        return Point4D(*rotated)
    
    def distance_to(self, other: 'Point4D') -> float:
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
        return f"Point3D(x={self.x:.3f}, y={self.y:.3f}, z={self.z:. 3f})"


class Vector4D:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0):
        self.components = np.array([x, y, z, w], dtype=np.float64)
    
    def magnitude(self) -> float:
        return float(np.linalg.norm(self.components))
    
    def normalize(self) -> 'Vector4D':
        mag = self. magnitude()
        if mag == 0:
            return Vector4D()
        normalized = self.components / mag
        return Vector4D(*normalized)
    
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


class Rotation4D: 
    def __init__(self, angles: Union[Tuple[float, ... ], np.ndarray]):
        self.angles = np.array(angles, dtype=np.float64)
        self.matrix = self._compute_rotation_matrix()
    
    def _compute_rotation_matrix(self) -> np.ndarray:
        matrix = np.eye(4, dtype=np.float64)
        
        if len(self.angles) >= 1:
            c, s = np.cos(self. angles[0]), np.sin(self.angles[0])
            rx = np.array([
                [1, 0, 0, 0],
                [0, c, -s, 0],
                [0, s, c, 0],
                [0, 0, 0, 1]
            ])
            matrix = matrix @ rx
        
        if len(self.angles) >= 2:
            c, s = np.cos(self.angles[1]), np.sin(self.angles[1])
            ry = np.array([
                [c, 0, s, 0],
                [0, 1, 0, 0],
                [-s, 0, c, 0],
                [0, 0, 0, 1]
            ])
            matrix = matrix @ ry
        
        if len(self. angles) >= 3:
            c, s = np.cos(self.angles[2]), np.sin(self.angles[2])
            rz = np.array([
                [c, -s, 0, 0],
                [s, c, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
            matrix = matrix @ rz
        
        if len(self.angles) >= 4:
            c, s = np.cos(self.angles[3]), np.sin(self.angles[3])
            rw = np.array([
                [c, 0, 0, s],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [-s, 0, 0, c]
            ])
            matrix = matrix @ rw
        
        return matrix
    
    def apply(self, point: Point4D) -> Point4D:
        return point.rotate_4d(self.matrix)


class Tesseract: 
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
            for j in range(i + 1, len(self.vertices)):
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