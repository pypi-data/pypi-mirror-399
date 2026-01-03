import numpy as np
from typing import Dict, List, Tuple, Optional, Callable, Any
import torch

class TimeManipulation4D:
    
    def __init__(self):
        self.time_parameter = 0.0
        self.time_scale = 1.0
        self.time_direction = 1  # 1 for forward, -1 for backward
        self. timeline_cache = []
    
    def set_time_scale(self, scale: float):
        
        self.time_scale = max(0.001, min(100. 0, scale))
    
    def set_time_direction(self, direction: str):
        
        if direction. lower() in ['forward', 'forward']: 
            self.time_direction = 1
        elif direction.lower() in ['backward', 'reverse', 'back']:
            self.time_direction = -1
    
    def evolve_shape(self, vertices: np.ndarray,
                    evolution_function: Callable[[np.ndarray, float], np.ndarray],
                    time_steps: int = 100) -> List[np.ndarray]:
        
        timeline = [vertices.copy()]
        current = vertices.copy()
        
        for step in range(time_steps):
            dt = (1.0 / time_steps) * self.time_scale * self.time_direction
            self.time_parameter += dt
            
            current = evolution_function(current, self.time_parameter)
            timeline.append(current.copy())
        
        self.timeline_cache = timeline
        return timeline
    
    def apply_4d_time_dilation(self, vertices: np. ndarray,
                              time_value: float,
                              w_factor: float = 1.0) -> np.ndarray:
        
        dilation_effect = 1.0 + w_factor * time_value
        
        dilated = vertices.copy()
        dilated[:, 3] *= dilation_effect
        
        return dilated
    
    def apply_time_warp_effect(self, vertices: np. ndarray,
                              warp_intensity: float = 0.5) -> np.ndarray:
        
        center = np.mean(vertices, axis=0)
        centered = vertices - center
        
        time_warp = centered. copy()
        for i in range(len(centered)):
            distance = np.linalg.norm(centered[i])
            warp_factor = np.exp(-distance * warp_intensity)
            time_warp[i] *= warp_factor
        
        return time_warp + center
    
    def time_reverse_animation(self) -> List[np.ndarray]:
        
        return self.timeline_cache[::-1]
    
    def time_loop_animation(self, loop_count: int = 3) -> List[np.ndarray]:
        
        looped = []
        for _ in range(loop_count):
            looped.extend(self. timeline_cache)
        
        return looped
    
    def time_interpolate_shapes(self, shape1: np.ndarray,
                               shape2: np.ndarray,
                               num_frames: int = 60) -> List[np.ndarray]:
        
        frames = []
        for i in range(num_frames):
            t = i / (num_frames - 1)
            
            interpolated = (1 - t) * shape1 + t * shape2
            
            if shape1.shape[1] == 4:
                time_value = t * 2 * np.pi
                interpolated[: , 3] += 0.2 * np.sin(time_value)
            
            frames. append(interpolated)
        
        return frames
    
    def apply_relativistic_time_dilation(self, vertices:  np.ndarray,
                                         velocity: np.ndarray,
                                         c:  float = 3e8) -> np.ndarray:
        
        v_magnitude = np.linalg.norm(velocity)
        
        if v_magnitude >= c:
            return vertices
        
        gamma = 1.0 / np.sqrt(1. 0 - (v_magnitude / c) ** 2)
        
        time_dilated = vertices.copy()
        time_dilated[:, 3] *= gamma
        
        return time_dilated
    
    def apply_gravitational_time_dilation(self, vertices: np.ndarray,
                                         mass: float,
                                         G: float = 6.674e-11,
                                         c: float = 3e8) -> np.ndarray:
        
        schwarzschild_radius = 2 * G * mass / (c ** 2)
        
        distances = np.linalg.norm(vertices, axis=1)
        
        time_dilated = vertices.copy()
        for i in range(len(vertices)):
            r = distances[i] + 1e-10
            dilation_factor = np.sqrt(1.0 - schwarzschild_radius / r)
            time_dilated[i, 3] *= dilation_factor
        
        return time_dilated
    
    def record_timeline_moment(self, moment_label: str, data: Any):
        
        self.timeline_cache.append({
            'label': moment_label,
            'time': self.time_parameter,
            'data': data
        })
    
    def export_timeline_as_sequence(self, output_dir: str, format: str = 'obj'):
        
        from .advanced_export_tools import AdvancedExportTools
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        for frame_idx, frame_data in enumerate(self.timeline_cache):
            if isinstance(frame_data, dict) and 'vertices' not in frame_data:
                continue
            
            vertices = frame_data if isinstance(frame_data, np. ndarray) else frame_data. get('vertices', [])
            
            shape_dict = {'vertices': vertices, 'edges': []}
            filename = os.path.join(output_dir, f'timeline_{frame_idx:06d}. {format}')
            
            AdvancedExportTools.quick_export(shape_dict, format=format, filename=filename)