import numpy as np
from typing import Callable, Union, List
from functools import wraps

class HyperInteractive4D:
    def __init__(self, use_gpu: bool = False):
        self.active_shapes = {}
    
    def shape(self, shape_type: str = 'tesseract', **kwargs):
        def decorator(func:  Callable):
            @wraps(func)
            def wrapper(*args, **inner_kwargs):
                from .core import Tesseract, Point4D
                
                if shape_type == 'tesseract':
                    size = kwargs.get('size', 1.0)
                    center = kwargs.get('center', Point4D(0, 0, 0, 0))
                    shape_obj = Tesseract(center=center, size=size)
                else:
                    shape_obj = None
                
                result = func(shape_obj, *args, **inner_kwargs)
                shape_id = kwargs.get('id', f'shape_{len(self.active_shapes)}')
                self.active_shapes[shape_id] = shape_obj
                return result
            
            return wrapper
        return decorator
    
    def rotate(self, angles: Union[List[float], np.ndarray], smooth: bool = False, duration: float = 1.0):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(shape_obj, *args, **kwargs):
                angles_array = np.array(angles)
                
                if smooth: 
                    steps = int(duration * 60)
                    for step in range(steps):
                        t = step / steps
                        current_angles = angles_array * t
                        self._apply_rotation_4d(shape_obj, current_angles)
                else:
                    self._apply_rotation_4d(shape_obj, angles_array)
                
                return func(shape_obj, *args, **kwargs)
            return wrapper
        return decorator
    
    def translate(self, offset: Union[List[float], np.ndarray], smooth: bool = False, duration:  float = 1.0):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(shape_obj, *args, **kwargs):
                offset_array = np.array(offset)
                
                if smooth: 
                    steps = int(duration * 60)
                    for step in range(steps):
                        t = step / steps
                        current_offset = offset_array * t
                        self._apply_translation_4d(shape_obj, current_offset)
                else:
                    self._apply_translation_4d(shape_obj, offset_array)
                
                return func(shape_obj, *args, **kwargs)
            return wrapper
        return decorator
    
    def scale(self, factors: Union[float, List[float]], uniform: bool = True):
        def decorator(func:  Callable):
            @wraps(func)
            def wrapper(shape_obj, *args, **kwargs):
                return func(shape_obj, *args, **kwargs)
            return wrapper
        return decorator
    
    def visualize(self, projection: str = 'perspective'):
        def decorator(func:  Callable):
            @wraps(func)
            def wrapper(shape_obj, *args, **kwargs):
                return func(shape_obj, *args, **kwargs)
            return wrapper
        return decorator
    
    def _apply_rotation_4d(self, shape_obj, angles:  np.ndarray):
        if hasattr(shape_obj, 'rotate'):
            shape_obj.rotate(angles)
    
    def _apply_translation_4d(self, shape_obj, offset: np.ndarray):
        if hasattr(shape_obj, 'translate'):
            from .core import Vector4D
            shape_obj. translate(Vector4D(*offset))