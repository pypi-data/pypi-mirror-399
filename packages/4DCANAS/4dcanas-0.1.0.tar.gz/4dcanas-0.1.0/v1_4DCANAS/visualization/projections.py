import numpy as np

class ProjectionEngine:
    """4D projection engine"""
    
    @staticmethod
    def orthogonal_projection_4d_to_3d(point_4d: np.ndarray) -> np.ndarray:
        return point_4d[: 3]
    
    @staticmethod
    def perspective_projection_4d_to_3d(point_4d: np.ndarray, distance: float = 2.0) -> np.ndarray:
        w = point_4d[3]
        scale = distance / (distance + w)
        return point_4d[: 3] * scale
    
    @staticmethod
    def stereographic_projection(point_4d: np.ndarray, pole:  float = 1.0) -> np.ndarray:
        if abs(point_4d[3] - pole) < 1e-10:
            return point_4d[: 3] * 1e6
        
        scale = 2 / (pole - point_4d[3])
        return point_4d[: 3] * scale