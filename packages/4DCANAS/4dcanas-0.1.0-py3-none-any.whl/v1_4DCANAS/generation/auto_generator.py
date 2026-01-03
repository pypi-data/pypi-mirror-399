import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple
from .config import GenerationConfig

class AutoGenerator4D:
    """AI-powered 4D shape generator"""
    
    def __init__(self):
        self.generation_history = []
        self.config_presets = self._load_config_presets()
    
    def _load_config_presets(self) -> Dict[str, GenerationConfig]:
        return {
            "minimal": GenerationConfig(num_vertices=8, symmetry_level="low"),
            "balanced": GenerationConfig(num_vertices=16, symmetry_level="high"),
            "complex": GenerationConfig(num_vertices=32, symmetry_level="ultra"),
        }
    
    def generate_shape(
        self,
        description: str,
        config: Optional[GenerationConfig] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate 4D shape from description"""
        
        if seed is not None:
            np. random.seed(seed)
        
        config = config or self.config_presets["balanced"]
        
        if "tesseract" in description. lower():
            return self._generate_tesseract_variant(config)
        elif "sphere" in description.lower():
            return self._generate_hypersphere_variant(config)
        else:
            return self._generate_ai_shape(description, config)
    
    def _generate_tesseract_variant(self, config: GenerationConfig) -> Dict[str, Any]:
        vertices = []
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                for k in range(-1, 2, 2):
                    for l in range(-1, 2, 2):
                        perturbation = (
                            np.random.normal(0, 0.05, 4)
                            if config.symmetry_level == "low"
                            else np.zeros(4)
                        )
                        vertex = (
                            np.array([i, j, k, l], dtype=np.float32) * 0.5
                            + perturbation
                        )
                        vertices.append(vertex)
        
        edges = self._compute_edges_4d(np.array(vertices))
        
        return {
            "type":  "tesseract_variant",
            "vertices": vertices,
            "edges": edges,
            "config": config,
        }
    
    def _generate_hypersphere_variant(self, config: GenerationConfig) -> Dict[str, Any]:
        num_points = config.num_vertices
        golden_angle = np.pi * (3.0 - np.sqrt(5))
        
        points = []
        for i in range(num_points):
            y = 1 - (i / float(num_points - 1)) * 2
            radius_at_y = np.sqrt(max(0, 1 - y * y))
            theta = golden_angle * i
            
            x = np.cos(theta) * radius_at_y
            z = np.sin(theta) * radius_at_y
            w = y
            
            points.append(np.array([x, z, w, y], dtype=np.float32))
        
        edges = self._compute_edges_4d(np. array(points), max_distance=2.0)
        
        return {
            "type": "hypersphere_variant",
            "vertices": points,
            "edges": edges,
            "config":  config,
            "radius": 1.0,
        }
    
    def _generate_ai_shape(
        self, description: str, config: GenerationConfig
    ) -> Dict[str, Any]:
        num_vertices = config.num_vertices
        
        if "large" in description.lower():
            num_vertices = int(num_vertices * 1.5)
        elif "small" in description.lower():
            num_vertices = int(num_vertices * 0.7)
        
        if "spiral" in description.lower():
            t = np.linspace(0, 4 * np.pi, num_vertices)
            vertices = np.column_stack([
                np.cos(t),
                np.sin(t),
                t / (4 * np.pi),
                np.sin(2 * t) / 2,
            ]).astype(np.float32)
        else:
            vertices = np.random.uniform(-1, 1, (num_vertices, 4)).astype(
                np.float32
            )
        
        edges = self._compute_edges_4d(vertices)
        
        return {
            "type": "ai_generated",
            "description": description,
            "vertices":  vertices,
            "edges": edges,
            "config": config,
        }
    
    def _compute_edges_4d(
        self, vertices: np.ndarray, max_distance: float = 1.5
    ) -> List[Tuple[int, int]]:
        edges = []
        num_vertices = len(vertices)
        
        for i in range(num_vertices):
            distances = np.linalg.norm(vertices - vertices[i], axis=1)
            neighbors = np.where((distances > 0.01) & (distances < max_distance))[0]
            
            for j in neighbors:
                if i < j:
                    edges.append((i, j))
        
        return edges
    
    def generate_motion_path(
        self,
        shape:  Dict[str, Any],
        path_type: str = "spiral",
        duration: float = 10.0,
        num_frames: int = 300,
    ) -> List[np.ndarray]:
        """Generate motion path for shape"""
        
        paths = []
        
        if path_type == "spiral":
            t = np.linspace(0, duration, num_frames)
            for time_val in t:
                angle = 2 * np.pi * time_val / duration
                displacement = np.array([
                    0.5 * np.cos(angle),
                    0.5 * np.sin(angle),
                    time_val / duration,
                    0.2 * np.sin(2 * angle),
                ])
                paths.append(displacement)
        elif path_type == "linear":
            for i in range(num_frames):
                t = i / num_frames
                displacement = np. array([t, 0, 0, 0])
                paths.append(displacement)
        elif path_type == "wave":
            t = np.linspace(0, duration, num_frames)
            for time_val in t: 
                displacement = np.array([
                    time_val / duration,
                    0.3 * np.sin(2 * np.pi * time_val / duration),
                    0.2 * np.cos(4 * np.pi * time_val / duration),
                    0.1 * np.sin(6 * np.pi * time_val / duration),
                ])
                paths.append(displacement)
        
        return paths
    
    def save_generation(self, shape:  Dict[str, Any], filename: str) -> None:
        """Save generated shape to file"""
        
        serializable = {
            "type": shape. get("type", "unknown"),
            "vertices": [
                v.tolist() if isinstance(v, np.ndarray) else v
                for v in shape["vertices"]
            ],
            "edges": shape.get("edges", []),
        }
        
        with open(filename, "w") as f:
            json.dump(serializable, f, indent=2)
    
    def load_generation(self, filename: str) -> Dict[str, Any]:
        """Load generated shape from file"""
        
        with open(filename, "r") as f:
            data = json.load(f)
        
        data["vertices"] = [
            np.array(v, dtype=np.float32) for v in data["vertices"]
        ]
        
        return data