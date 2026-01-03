"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               AutoGenerator4D - AI-Powered Shape Generation                 ║
║                      © 2025 MERO - All Rights Reserved                      ║
║                              Version 1.0.0                                  ║
║                                                                              ║
║  Automatic 4D shape generation using AI algorithms                          ║
║  Created by MERO | Telegram: @QP4RM                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import torch
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
import json

@dataclass
class GenerationConfig:
    """Configuration for automatic shape generation.  © 2025 MERO"""
    num_vertices: int = 16
    dimension: int = 4
    symmetry_level: str = 'high'
    physical_properties: Dict[str, float] = None
    aesthetic_score_target: float = 0.8


class AutoGenerator4D:
    """
    AI-powered 4D shape generation system. 
    
    Generates parametric and AI-generated 4D shapes with customizable
    properties, physics rulesets, and motion paths.
    
    © 2025 MERO - Advanced AI for 4D Geometry
    
    Example:
        >>> gen = AutoGenerator4D()
        >>> shape = gen.generate_shape("large random spiral", seed=42)
        >>> physics = gen.generate_physics_ruleset(shape, "rotating with gravity")
        >>> path = gen.generate_motion_path(shape, "spiral", duration=10)
    """
    
    def __init__(self):
        self.generation_history = []
        self.config_presets = self._load_config_presets()
        self.ai_model = None
        self.version = "1.0.0"
        self.developer = "MERO"
    
    def _load_config_presets(self) -> Dict[str, GenerationConfig]:
        """Load predefined configuration presets.  © 2025 MERO"""
        
        return {
            'minimal': GenerationConfig(num_vertices=8, symmetry_level='low'),
            'balanced': GenerationConfig(num_vertices=16, symmetry_level='high'),
            'complex': GenerationConfig(num_vertices=32, symmetry_level='ultra'),
            'realistic': GenerationConfig(num_vertices=24, symmetry_level='high',
                                        physical_properties={'mass': 1.0, 'density': 1.0})
        }
    
    def generate_shape(self, description: str,
                      config: Optional[GenerationConfig] = None,
                      seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a 4D shape from natural language description.
        
        © 2025 MERO
        
        Args:
            description: Natural language description of desired shape
            config: GenerationConfig instance for customization
            seed: Random seed for reproducibility
        
        Returns:
            Dictionary containing vertices, edges, and metadata
        """
        
        if seed is not None:
            np. random.seed(seed)
            torch.manual_seed(seed)
        
        config = config or self.config_presets['balanced']
        
        if 'tesseract' in description.lower():
            return self._generate_tesseract_variant(config)
        elif 'sphere' in description.lower():
            return self._generate_hypersphere_variant(config)
        elif 'torus' in description.lower():
            return self._generate_4d_torus(config)
        elif 'polytope' in description.lower():
            return self._generate_polytope_variant(config)
        else:
            return self._generate_ai_shape(description, config)
    
    def _generate_tesseract_variant(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate tesseract variant.  © 2025 MERO"""
        
        vertices = []
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                for k in range(-1, 2, 2):
                    for l in range(-1, 2, 2):
                        if config.symmetry_level == 'low':
                            perturbation = np.random.normal(0, 0.1, 4)
                        elif config.symmetry_level == 'high':
                            perturbation = np.zeros(4)
                        else: 
                            perturbation = np.random.normal(0, 0.05, 4)
                        
                        vertex = np.array([i, j, k, l], dtype=np.float32) * 0.5 + perturbation
                        vertices.append(vertex)
        
        edges = self._compute_edges_4d(np.array(vertices))
        
        return {
            'type':  'tesseract_variant',
            'vertices': vertices,
            'edges': edges,
            'config': config,
            'metadata': {
                'generation_method': 'parametric',
                'symmetry':  config.symmetry_level,
                'developer': 'MERO',
                'version': '1.0.0'
            }
        }
    
    def _generate_hypersphere_variant(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate hypersphere variant. © 2025 MERO"""
        
        num_points = config.num_vertices
        golden_angle = np.pi * (3. - np.sqrt(5))
        
        points = []
        for i in range(num_points):
            y = 1 - (i / float(num_points - 1)) * 2
            radius_at_y = np.sqrt(1 - y * y)
            
            theta = golden_angle * i
            
            x = np.cos(theta) * radius_at_y
            z = np.sin(theta) * radius_at_y
            w = y
            
            points.append(np.array([x, z, w, y], dtype=np.float32))
        
        edges = self._compute_edges_4d(np.array(points), max_distance=2. 0)
        
        return {
            'type': 'hypersphere_variant',
            'vertices': points,
            'edges': edges,
            'config':  config,
            'radius': 1.0,
            'developer': 'MERO',
            'version': '1.0.0'
        }
    
    def _generate_4d_torus(self, config:  GenerationConfig) -> Dict[str, Any]:
        """Generate 4D torus.  © 2025 MERO"""
        
        major_radius = 1.5
        minor_radius = 0.5
        
        u_steps = int(np.sqrt(config.num_vertices / 2))
        v_steps = u_steps
        
        vertices = []
        for i in range(u_steps):
            u = 2 * np.pi * i / u_steps
            for j in range(v_steps):
                v = 2 * np.pi * j / v_steps
                
                x = (major_radius + minor_radius * np.cos(v)) * np.cos(u)
                y = (major_radius + minor_radius * np.cos(v)) * np.sin(u)
                z = minor_radius * np.sin(v)
                w = minor_radius * np.cos(u - v)
                
                vertices. append(np.array([x, y, z, w], dtype=np.float32))
        
        edges = self._compute_edges_4d(np.array(vertices), max_distance=1.5)
        
        return {
            'type': '4d_torus',
            'vertices': vertices,
            'edges': edges,
            'config': config,
            'major_radius': major_radius,
            'minor_radius': minor_radius,
            'developer': 'MERO',
            'version': '1.0.0'
        }
    
    def _generate_polytope_variant(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate polytope variant.  © 2025 MERO"""
        
        num_vertices = config.num_vertices
        angles = np.linspace(0, 2*np.pi, num_vertices, endpoint=False)
        
        vertices = []
        for i, angle in enumerate(angles):
            radius = 1.0 + 0.3 * np.sin(2 * angle)
            
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0.5 * np.sin(3 * angle)
            w = 0.3 * np.cos(4 * angle)
            
            vertices.append(np.array([x, y, z, w], dtype=np.float32))
        
        edges = self._compute_edges_4d(np. array(vertices), max_distance=1.2)
        
        return {
            'type': 'polytope_variant',
            'vertices':  vertices,
            'edges': edges,
            'config': config,
            'developer': 'MERO',
            'version': '1.0.0'
        }
    
    def _generate_ai_shape(self, description: str, config: GenerationConfig) -> Dict[str, Any]:
        """Generate AI-powered custom shape. © 2025 MERO"""
        
        tokens = description.lower().split()
        
        vertex_count = config.num_vertices
        if 'large' in tokens:
            vertex_count = int(vertex_count * 1.5)
        elif 'small' in tokens:
            vertex_count = int(vertex_count * 0.7)
        
        if 'random' in tokens:
            vertices = np.random.normal(0, 1, (vertex_count, 4)).astype(np.float32)
            vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
        elif 'spiral' in tokens:
            t = np.linspace(0, 4*np.pi, vertex_count)
            vertices = np.column_stack([
                np.cos(t),
                np.sin(t),
                t / (4*np.pi),
                np.sin(2*t) / 2
            ]).astype(np.float32)
        else:
            vertices = np.random.uniform(-1, 1, (vertex_count, 4)).astype(np.float32)
        
        edges = self._compute_edges_4d(vertices)
        
        return {
            'type': 'ai_generated',
            'description': description,
            'vertices':  vertices,
            'edges': edges,
            'config': config,
            'ai_confidence': np.random.uniform(0.7, 0.99),
            'developer': 'MERO',
            'version': '1.0.0'
        }
    
    def _compute_edges_4d(self, vertices: np.ndarray,
                         max_distance: float = 1.5) -> List[Tuple[int, int]]:
        """Compute edges for vertex cloud. © 2025 MERO"""
        
        edges = []
        num_vertices = len(vertices)
        
        for i in range(num_vertices):
            distances = np.linalg.norm(vertices - vertices[i], axis=1)
            neighbors = np.where((distances > 0.01) & (distances < max_distance))[0]
            
            for j in neighbors:
                if i < j:
                    edges.append((i, j))
        
        return edges
    
    def generate_physics_ruleset(self, base_shape: Dict[str, Any],
                                physics_description: str) -> Dict[str, Callable]:
        """
        Generate physics rulesets from description. 
        
        © 2025 MERO
        """
        
        rulesets = {}
        tokens = physics_description.lower().split()
        
        if 'gravity' in tokens or 'falling' in tokens:
            rulesets['gravity'] = lambda p, o, t: np.array([0, -9.81, 0, 0]) * p['mass']
        
        if 'repulsion' in tokens or 'repel' in tokens:
            def repulsion_force(particle, others, time):
                force = np.zeros(4)
                for other in others: 
                    if np.linalg.norm(particle['position'] - other['position']) < 0.1:
                        direction = (particle['position'] - other['position']) / 0.1
                        force += direction * 100
                return force
            
            rulesets['repulsion'] = repulsion_force
        
        if 'attraction' in tokens or 'attract' in tokens:
            def attraction_force(particle, others, time):
                center = np.mean([o['position'] for o in others], axis=0)
                return (center - particle['position']) * 0.5
            
            rulesets['attraction'] = attraction_force
        
        if 'rotation' in tokens or 'spin' in tokens:
            def rotation_force(particle, others, time):
                angular_velocity = np.array([0, 0, 0. 1, 0])
                return np.cross(angular_velocity[: 3], particle['position'][:3]) * 0.1
            
            rulesets['rotation'] = rotation_force
        
        return rulesets
    
    def generate_motion_path(self, shape: Dict[str, Any],
                            path_type: str = 'spiral',
                            duration: float = 10.0,
                            num_frames: int = 300) -> List[np.ndarray]:
        """
        Generate motion path for shape animation.
        
        © 2025 MERO
        """
        
        paths = []
        
        if path_type == 'spiral': 
            t = np.linspace(0, duration, num_frames)
            for i, time_val in enumerate(t):
                angle = 2 * np.pi * time_val / duration
                displacement = np.array([
                    0.5 * np.cos(angle),
                    0.5 * np.sin(angle),
                    time_val / duration,
                    0. 2 * np.sin(2 * angle)
                ])
                paths.append(displacement)
        
        elif path_type == 'linear':
            for i in range(num_frames):
                t = i / num_frames
                displacement = np.array([t, 0, 0, 0])
                paths.append(displacement)
        
        elif path_type == 'wave':
            t = np.linspace(0, duration, num_frames)
            for time_val in t:
                displacement = np.array([
                    time_val / duration,
                    0.3 * np.sin(2 * np.pi * time_val / duration),
                    0.2 * np.cos(4 * np.pi * time_val / duration),
                    0.1 * np.sin(6 * np.pi * time_val / duration)
                ])
                paths.append(displacement)
        
        elif path_type == 'geodesic':
            for i in range(num_frames):
                t = i / num_frames
                displacement = np.array([
                    np.sin(np.pi * t),
                    np.cos(np.pi * t),
                    np.sin(2 * np. pi * t),
                    np.cos(2 * np. pi * t)
                ])
                paths.append(displacement)
        
        return paths
    
    def save_generation(self, shape: Dict[str, Any], filename: str):
        """Save generated shape to file. © 2025 MERO"""
        
        serializable = {
            'type': shape['type'],
            'vertices': [v.tolist() if isinstance(v, np.ndarray) else v for v in shape['vertices']],
            'edges':  shape['edges'],
            'metadata': {
                **shape.get('metadata', {}),
                'developer': 'MERO',
                'version': '1.0.0'
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(serializable, f, indent=2)
    
    def load_generation(self, filename: str) -> Dict[str, Any]:
        """Load generated shape from file. © 2025 MERO"""
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        data['vertices'] = [np.array(v, dtype=np.float32) for v in data['vertices']]
        
        return data