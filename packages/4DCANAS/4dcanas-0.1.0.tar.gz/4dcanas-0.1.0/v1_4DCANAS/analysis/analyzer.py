import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from scipy.spatial import distance
from scipy.stats import skew, kurtosis

class DeepAnalyzer4D:
    """Deep analysis engine for 4D shapes"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_shape(
        self,
        vertices: np.ndarray,
        edges: Optional[List[Tuple[int, int]]] = None,
    ) -> Dict[str, Any]:
        """Comprehensive shape analysis"""
        
        vertices_array = np.array([
            v if isinstance(v, np.ndarray) else v for v in vertices
        ])
        
        analysis = {
            "geometric_properties": self._analyze_geometric_properties(vertices_array),
            "topological_properties": self._analyze_topological_properties(
                vertices_array, edges
            ),
            "symmetry_analysis": self._analyze_symmetry(vertices_array),
            "stability_analysis": self._analyze_stability(vertices_array),
            "aesthetic_score": self._calculate_aesthetic_score(vertices_array),
        }
        
        return analysis
    
    def _analyze_geometric_properties(self, vertices: np.ndarray) -> Dict[str, float]:
        center = np.mean(vertices, axis=0)
        distances_from_center = np.linalg.norm(vertices - center, axis=1)
        
        perimeter = np.sum(distances_from_center)
        volume_estimate = np.prod(np.max(vertices, axis=0) - np.min(vertices, axis=0))
        
        radius_min = np.min(distances_from_center)
        radius_max = np.max(distances_from_center)
        radius_mean = np.mean(distances_from_center)
        
        return {
            "center": center. tolist(),
            "perimeter_4d": float(perimeter),
            "volume_estimate": float(volume_estimate),
            "radius_min": float(radius_min),
            "radius_max": float(radius_max),
            "radius_mean": float(radius_mean),
            "radius_variance": float(np.var(distances_from_center)),
            "compactness": float(radius_mean / (radius_max + 1e-10)),
        }
    
    def _analyze_topological_properties(
        self,
        vertices: np. ndarray,
        edges: Optional[List[Tuple[int, int]]],
    ) -> Dict[str, Any]:
        if edges is None:
            distances = distance.cdist(vertices, vertices)
            edges = []
            for i in range(len(vertices)):
                for j in range(i + 1, len(vertices)):
                    if distances[i, j] < np.mean(distances) * 1.5:
                        edges. append((i, j))
        
        vertex_degrees = [0] * len(vertices)
        for edge in edges:
            vertex_degrees[edge[0]] += 1
            vertex_degrees[edge[1]] += 1
        
        euler_characteristic = len(vertices) - len(edges)
        
        return {
            "num_vertices": len(vertices),
            "num_edges": len(edges),
            "vertex_degrees": vertex_degrees,
            "avg_degree": float(np.mean(vertex_degrees)),
            "degree_variance": float(np.var(vertex_degrees)),
            "euler_characteristic": int(euler_characteristic),
            "connectivity": float(np.mean(vertex_degrees) / len(vertices)),
        }
    
    def _analyze_symmetry(self, vertices: np.ndarray) -> Dict[str, Any]:
        center = np.mean(vertices, axis=0)
        centered = vertices - center
        
        symmetry_scores = {
            "reflection_xy": self._check_reflection_symmetry(centered, axes=[0, 1]),
            "reflection_xz": self._check_reflection_symmetry(centered, axes=[0, 2]),
            "reflection_xw": self._check_reflection_symmetry(centered, axes=[0, 3]),
            "reflection_yz": self._check_reflection_symmetry(centered, axes=[1, 2]),
            "reflection_yw": self._check_reflection_symmetry(centered, axes=[1, 3]),
            "reflection_zw":  self._check_reflection_symmetry(centered, axes=[2, 3]),
        }
        
        overall_symmetry = np.mean(list(symmetry_scores.values()))
        
        return {
            **symmetry_scores,
            "overall_symmetry": float(overall_symmetry),
            "is_highly_symmetric": overall_symmetry > 0.7,
        }
    
    def _check_reflection_symmetry(
        self, vertices: np.ndarray, axes: List[int]
    ) -> float:
        reflected = vertices.copy()
        for axis in axes:
            reflected[: , axis] = -reflected[:, axis]
        
        distances = np.min(
            np.linalg.norm(
                vertices[: , np.newaxis] - reflected[np.newaxis, :], axis=2
            ),
            axis=1,
        )
        
        return float(
            1. 0
            - (
                np.mean(distances)
                / (np.max(np.linalg.norm(vertices, axis=1)) + 1e-10)
            )
        )
    
    def _analyze_stability(self, vertices: np. ndarray) -> Dict[str, Any]:
        center = np.mean(vertices, axis=0)
        centered = vertices - center
        
        eigenvalues, eigenvectors = np.linalg.eigh(centered. T @ centered)
        eigenvalues = np.sort(eigenvalues)[::-1]
        
        stability_score = eigenvalues[0] / (np.sum(eigenvalues) + 1e-10)
        condition_number = eigenvalues[0] / (eigenvalues[-1] + 1e-10)
        
        return {
            "eigenvalues": eigenvalues. tolist(),
            "stability_score": float(stability_score),
            "condition_number":  float(condition_number),
            "is_stable": stability_score > 0.6,
        }
    
    def _calculate_aesthetic_score(self, vertices: np.ndarray) -> float:
        properties = self._analyze_geometric_properties(vertices)
        topology = self._analyze_topological_properties(vertices, None)
        symmetry = self._analyze_symmetry(vertices)
        stability = self._analyze_stability(vertices)
        
        compactness = properties["compactness"]
        symmetry_score = symmetry["overall_symmetry"]
        stability_score = stability["stability_score"]
        connectivity = topology["connectivity"]
        
        aesthetic = (
            compactness * 0.2
            + symmetry_score * 0.4
            + stability_score * 0.2
            + connectivity * 0.2
        )
        
        return float(np.clip(aesthetic, 0, 1))
    
    def suggest_improvements(self, shape: Dict[str, Any]) -> List[str]:
        """Suggest improvements for shape"""
        
        vertices = np.array(shape["vertices"])
        analysis = self.analyze_shape(vertices, shape. get("edges"))
        
        suggestions = []
        
        if analysis["symmetry_analysis"]["overall_symmetry"] < 0.5:
            suggestions.append(
                "Consider making the shape more symmetric for aesthetic appeal"
            )
        
        if analysis["stability_analysis"]["stability_score"] < 0.5:
            suggestions.append(
                "The shape may be unstable. Try concentrating vertices more towards center"
            )
        
        if analysis["aesthetic_score"] > 0.85:
            suggestions.append("Excellent aesthetic properties!")
        
        return suggestions