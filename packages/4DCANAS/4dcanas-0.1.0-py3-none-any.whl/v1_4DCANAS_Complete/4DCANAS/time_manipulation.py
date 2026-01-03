import numpy as np
from typing import List, Callable, Optional

class TimeManipulation4D:
    def __init__(self):
        self.time_parameter = 0.0
        self.time_scale = 1.0
        self.time_direction = 1
        self.timeline_cache = []
    
    def set_time_scale(self, scale: float):
        self.time_scale = max(0.001, min(100. 0, scale))
    
    def set_time_direction(self, direction: str):
        if direction. lower() in ['forward', 'fw']:
            self.time_direction = 1
        elif direction. lower() in ['backward', 'bw', 'reverse']: 
            self.time_direction = -1
    
    def evolve_shape(self, vertices: np.ndarray, evolution_function: Callable[[np.ndarray, float], np.ndarray], time_steps: int = 100) -> List[np.ndarray]:
        timeline = [vertices.copy()]
        current = vertices.copy()
        
        for step in range(time_steps):
            dt = (1.0 / time_steps) * self.time_scale * self.time_direction
            self.time_parameter += dt
            
            current = evolution_function(current, self.time_parameter)
            timeline.append(current.copy())
        
        self.timeline_cache = timeline
        return timeline
    
    def apply_4d_time_dilation(self, vertices: np. ndarray, time_value: float, w_factor: float = 1.0) -> np.ndarray:
        dilation_effect = 1.0 + w_factor * time_value
        dilated = vertices. copy()
        dilated[:, 3] *= dilation_effect
        return dilated
    
    def apply_relativistic_time_dilation(self, vertices: np.ndarray, velocity: np.ndarray, c:  float = 3e8) -> np.ndarray:
        v_magnitude = np.linalg.norm(velocity)
        
        if v_magnitude >= c:
            return vertices
        
        gamma = 1.0 / np.sqrt(1.0 - (v_magnitude / c) ** 2)
        
        time_dilated = vertices.copy()
        time_dilated[:, 3] *= gamma
        
        return time_dilated
    
    def time_reverse_animation(self) -> List[np.ndarray]:
        return self.timeline_cache[::-1]
    
    def time_loop_animation(self, loop_count: int = 3) -> List[np.ndarray]:
        looped = []
        for _ in range(loop_count):
            looped.extend(self.timeline_cache)
        return looped
    
    def export_timeline_as_sequence(self, output_dir: str, format: str = 'obj'):
        from .advanced_export_tools import AdvancedExportTools
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        for frame_idx, frame_data in enumerate(self.timeline_cache):
            if isinstance(frame_data, np.ndarray):
                shape_dict = {'vertices': frame_data, 'edges': []}
                filename = os.path.join(output_dir, f'timeline_{frame_idx: 06d}.{format}')
                AdvancedExportTools.quick_export(shape_dict, format=format, filename=filename)