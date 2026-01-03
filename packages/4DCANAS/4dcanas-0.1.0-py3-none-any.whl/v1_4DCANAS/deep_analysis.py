import numpy as np
import torch
from typing import Dict, List, Tuple, Optional, Any, Callable
from sklearn.preprocessing import StandardScaler
from scipy.stats import entropy, kurtosis, skew
from scipy.spatial import distance
import json

class DeepAnalyzer4D:
    
    def __init__(self):
        self.analysis_cache = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def analyze_shape(self, vertices: np.ndarray,
                     edges: Optional[List[Tuple[int, int]]] = None) -> Dict[str, Any]: 
        
        vertices_array = np.array([v if isinstance(v, np.ndarray) else v for v in vertices])
        
        analysis = {
            'geometric_properties': self._analyze_geometric_properties(vertices_array),
            'topological_properties': self._analyze_topological_properties(vertices_array, edges),
            'symmetry_analysis': self._analyze_symmetry(vertices_array),
            'stability_analysis': self._analyze_stability(vertices_array),
            'dimensional_characteristics': self._analyze_dimensional_characteristics(vertices_array),
            'algebraic_properties': self._analyze_algebraic_properties(vertices_array),
            'aesthetic_score': self._calculate_aesthetic_score(vertices_array)
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
            'center': center. tolist(),
            'perimeter_4d': float(perimeter),
            'volume_estimate': float(volume_estimate),
            'radius_min': float(radius_min),
            'radius_max': float(radius_max),
            'radius_mean':  float(radius_mean),
            'radius_variance': float(np.var(distances_from_center)),
            'compactness': float(radius_mean / (radius_max + 1e-10))
        }
    
    def _analyze_topological_properties(self, vertices: np.ndarray,
                                       edges: Optional[List[Tuple[int, int]]]) -> Dict[str, Any]:
        
        if edges is None:
            distances = distance.cdist(vertices, vertices)
            edges = []
            for i in range(len(vertices)):
                for j in range(i+1, len(vertices)):
                    if distances[i, j] < np.mean(distances) * 1.5:
                        edges. append((i, j))
        
        vertex_degrees = [0] * len(vertices)
        for edge in edges:
            vertex_degrees[edge[0]] += 1
            vertex_degrees[edge[1]] += 1
        
        euler_characteristic = len(vertices) - len(edges)
        
        return {
            'num_vertices': len(vertices),
            'num_edges': len(edges),
            'vertex_degrees': vertex_degrees,
            'avg_degree': float(np.mean(vertex_degrees)),
            'degree_variance': float(np.var(vertex_degrees)),
            'euler_characteristic': int(euler_characteristic),
            'connectivity':  float(np.mean(vertex_degrees) / len(vertices))
        }
    
    def _analyze_symmetry(self, vertices: np.ndarray) -> Dict[str, Any]:
        
        center = np.mean(vertices, axis=0)
        centered = vertices - center
        
        symmetry_scores = {
            'reflection_xy': self._check_reflection_symmetry(centered, axes=[0, 1]),
            'reflection_xz': self._check_reflection_symmetry(centered, axes=[0, 2]),
            'reflection_xw': self._check_reflection_symmetry(centered, axes=[0, 3]),
            'reflection_yz': self._check_reflection_symmetry(centered, axes=[1, 2]),
            'reflection_yw': self._check_reflection_symmetry(centered, axes=[1, 3]),
            'reflection_zw': self._check_reflection_symmetry(centered, axes=[2, 3]),
            'rotational_90': self._check_rotational_symmetry(centered, angle=np.pi/2),
            'rotational_120': self._check_rotational_symmetry(centered, angle=2*np.pi/3)
        }
        
        overall_symmetry = np.mean(list(symmetry_scores.values()))
        
        return {
            **symmetry_scores,
            'overall_symmetry': float(overall_symmetry),
            'is_highly_symmetric': overall_symmetry > 0.7
        }
    
    def _check_reflection_symmetry(self, vertices: np.ndarray,
                                   axes: List[int]) -> float:
        
        reflected = vertices.copy()
        for axis in axes:
            reflected[: , axis] = -reflected[:, axis]
        
        distances = np.min(np.linalg.norm(vertices[: , np.newaxis] - reflected[np.newaxis, :], axis=2), axis=1)
        
        return float(1. 0 - (np.mean(distances) / (np.max(np.linalg.norm(vertices, axis=1)) + 1e-10)))
    
    def _check_rotational_symmetry(self, vertices: np.ndarray,
                                   angle: float) -> float:
        
        c = np.cos(angle)
        s = np.sin(angle)
        
        rotation_matrix = np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, c, -s],
            [0, 0, s, c]
        ])
        
        rotated = vertices @ rotation_matrix. T
        
        distances = np.min(np.linalg.norm(vertices[:, np. newaxis] - rotated[np.newaxis, :], axis=2), axis=1)
        
        return float(1.0 - (np.mean(distances) / (np.max(np.linalg.norm(vertices, axis=1)) + 1e-10)))
    
    def _analyze_stability(self, vertices: np.ndarray) -> Dict[str, Any]:
        
        center = np.mean(vertices, axis=0)
        centered = vertices - center
        
        eigenvalues, eigenvectors = np.linalg.eigh(centered. T @ centered)
        eigenvalues = np.sort(eigenvalues)[::-1]
        
        stability_score = eigenvalues[0] / (np.sum(eigenvalues) + 1e-10)
        
        condition_number = eigenvalues[0] / (eigenvalues[-1] + 1e-10)
        
        angular_momentum = np.linalg.norm(np.cross(centered[0, :3], centered[1, :3]))
        
        return {
            'eigenvalues': eigenvalues. tolist(),
            'stability_score': float(stability_score),
            'condition_number':  float(condition_number),
            'angular_momentum': float(angular_momentum),
            'is_stable': stability_score > 0.6,
            'dominant_axis': eigenvectors[:, 0].tolist()
        }
    
    def _analyze_dimensional_characteristics(self, vertices: np.ndarray) -> Dict[str, Any]:
        
        if vertices.shape[1] == 4:
            x_range = np.max(vertices[:, 0]) - np.min(vertices[:, 0])
            y_range = np.max(vertices[:, 1]) - np.min(vertices[:, 1])
            z_range = np.max(vertices[:, 2]) - np.min(vertices[: , 2])
            w_range = np.max(vertices[: , 3]) - np.min(vertices[:, 3])
            
            return {
                'x_extent': float(x_range),
                'y_extent': float(y_range),
                'z_extent': float(z_range),
                'w_extent':  float(w_range),
                'aspect_ratios': {
                    'xy': float(x_range / (y_range + 1e-10)),
                    'xz': float(x_range / (z_range + 1e-10)),
                    'xw': float(x_range / (w_range + 1e-10)),
                    'yz': float(y_range / (z_range + 1e-10)),
                    'yw': float(y_range / (w_range + 1e-10)),
                    'zw': float(z_range / (w_range + 1e-10))
                }
            }
        
        return {}
    
    def _analyze_algebraic_properties(self, vertices: np.ndarray) -> Dict[str, Any]:
        
        scaler = StandardScaler()
        normalized = scaler.fit_transform(vertices)
        
        distances_all = distance.pdist(vertices)
        
        return {
            'mean':  vertices.mean(axis=0).tolist(),
            'std':  vertices.std(axis=0).tolist(),
            'skewness': skew(vertices. flatten()),
            'kurtosis': float(kurtosis(vertices.flatten())),
            'distance_mean': float(np.mean(distances_all)),
            'distance_std': float(np.std(distances_all)),
            'distance_min': float(np.min(distances_all)),
            'distance_max': float(np.max(distances_all))
        }
    
    def _calculate_aesthetic_score(self, vertices: np.ndarray) -> float:
        
        properties = self._analyze_geometric_properties(vertices)
        topology = self._analyze_topological_properties(vertices, None)
        symmetry = self._analyze_symmetry(vertices)
        stability = self._analyze_stability(vertices)
        
        compactness = properties['compactness']
        symmetry_score = symmetry['overall_symmetry']
        stability_score = stability['stability_score']
        connectivity = topology['connectivity']
        
        aesthetic = (compactness * 0.2 +
                    symmetry_score * 0.4 +
                    stability_score * 0.2 +
                    connectivity * 0.2)
        
        return float(np.clip(aesthetic, 0, 1))
    
    def compare_shapes(self, shape1: Dict[str, Any],
                      shape2: Dict[str, Any]) -> Dict[str, float]:
        
        vertices1 = np.array(shape1['vertices'])
        vertices2 = np.array(shape2['vertices'])
        
        analysis1 = self.analyze_shape(vertices1, shape1.get('edges'))
        analysis2 = self. analyze_shape(vertices2, shape2.get('edges'))
        
        comparisons = {}
        
        geo1 = analysis1['geometric_properties']
        geo2 = analysis2['geometric_properties']
        
        comparisons['volume_ratio'] = geo1['volume_estimate'] / (geo2['volume_estimate'] + 1e-10)
        comparisons['size_ratio'] = geo1['radius_mean'] / (geo2['radius_mean'] + 1e-10)
        comparisons['compactness_ratio'] = geo1['compactness'] / (geo2['compactness'] + 1e-10)
        
        sym1 = analysis1['symmetry_analysis']['overall_symmetry']
        sym2 = analysis2['symmetry_analysis']['overall_symmetry']
        comparisons['symmetry_difference'] = abs(sym1 - sym2)
        
        stab1 = analysis1['stability_analysis']['stability_score']
        stab2 = analysis2['stability_analysis']['stability_score']
        comparisons['stability_difference'] = abs(stab1 - stab2)
        
        ae1 = analysis1['aesthetic_score']
        ae2 = analysis2['aesthetic_score']
        comparisons['aesthetic_difference'] = abs(ae1 - ae2)
        
        return comparisons
    
    def suggest_improvements(self, shape:  Dict[str, Any],
                            target_metrics: Optional[Dict[str, float]] = None) -> List[str]:
        
        vertices = np.array(shape['vertices'])
        analysis = self.analyze_shape(vertices, shape.get('edges'))
        
        suggestions = []
        
        if analysis['symmetry_analysis']['overall_symmetry'] < 0.5:
            suggestions.append('💡 Consider making the shape more symmetric for aesthetic appeal')
        
        if analysis['stability_analysis']['stability_score'] < 0.5:
            suggestions.append('⚠️ The shape may be unstable. Try concentrating vertices more towards center')
        
        if analysis['geometric_properties']['radius_variance'] > 0.5:
            suggestions.append('📐 High radius variance detected. Shape could be more uniform')
        
        if analysis['topological_properties']['degree_variance'] > 2:
            suggestions.append('🔗 Irregular vertex connectivity.  Consider rewiring edges')
        
        if analysis['aesthetic_score'] > 0.85:
            suggestions.append('🌟 Excellent aesthetic properties!')
        
        geo = analysis['geometric_properties']
        aspect_ratios = [
            geo. get('radius_max', 1) / (geo.get('radius_min', 1) + 1e-10)
        ]
        
        if aspect_ratios[0] > 3:
            suggestions.append('📏 Shape is highly elongated. Consider adjusting proportions')
        
        return suggestions
    
    def extract_patterns(self, vertices: np.ndarray,
                        pattern_type: str = 'all') -> Dict[str, Any]:
        
        patterns = {}
        
        if pattern_type in ['all', 'spatial']:
            from scipy.cluster.hierarchy import dendrogram, linkage
            
            Z = linkage(vertices, method='ward')
            patterns['clustering'] = {
                'linkage_matrix': Z. tolist(),
                'num_clusters': len(np.unique(Z[: , 2]))
            }
        
        if pattern_type in ['all', 'spectral']:
            distances = distance.squareform(distance.pdist(vertices))
            eigenvalues = np.linalg.eigvals(distances)
            patterns['spectral_signature'] = np.sort(eigenvalues)[::-1]. tolist()[:10]
        
        if pattern_type in ['all', 'frequency']:
            from scipy.fft import fft
            
            fft_result = fft(vertices. flatten())
            patterns['frequency_components'] = np.abs(fft_result)[:20]. tolist()
        
        return patterns