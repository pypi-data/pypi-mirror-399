import numpy as np
from typing import List, Callable
from .core import Point4D, Vector4D

class ForceField4D:
    def __init__(self, force_function: Callable[[Point4D], Vector4D]):
        self.force_function = force_function
    
    def get_force(self, point: Point4D) -> Vector4D:
        return self.force_function(point)


class Physics4D:
    def __init__(self, gravity: Vector4D = None, damping: float = 0.99):
        self.gravity = gravity or Vector4D(0, -0.01, 0, 0)
        self.damping = damping
        self.particles: List[dict] = []
        self.forces: List[ForceField4D] = []
    
    def add_particle(self, position: Point4D, velocity: Vector4D = None, mass: float = 1.0):
        self.particles.append({
            'position': position,
            'velocity': velocity or Vector4D(),
            'mass': mass,
            'acceleration': Vector4D()
        })
    
    def add_force_field(self, field: ForceField4D):
        self.forces.append(field)
    
    def update(self, dt: float = 0.016):
        for particle in self. particles:
            particle['acceleration'] = self.gravity
            
            for force_field in self.forces:
                force = force_field.get_force(particle['position'])
                acceleration = force * (1.0 / particle['mass'])
                particle['acceleration'] = particle['acceleration'] + acceleration
            
            particle['velocity'] = particle['velocity'] + particle['acceleration'] * dt
            particle['velocity'] = particle['velocity'] * self.damping
            
            offset = particle['velocity'] * dt
            particle['position'] = particle['position'] + Point4D(*offset. components)
    
    def get_positions(self) -> List[Point4D]:
        return [p['position'] for p in self.particles]
    
    def get_velocities(self) -> List[Vector4D]:
        return [p['velocity'] for p in self. particles]