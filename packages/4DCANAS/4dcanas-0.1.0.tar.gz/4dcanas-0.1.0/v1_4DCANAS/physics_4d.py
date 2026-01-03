import numpy as np
import torch
from typing import List, Callable, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ForceType(Enum):
    GRAVITY = "gravity"
    ELECTROMAGNETIC = "electromagnetic"
    WEAK_NUCLEAR = "weak_nuclear"
    STRONG_NUCLEAR = "strong_nuclear"
    CUSTOM = "custom"

@dataclass
class Particle4D:
    position: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray
    mass: float
    charge: float = 0.0
    spin: float = 0.0
    energy: float = 0.0


class Physics4DEngine:
    
    def __init__(self, gravity_vector: Optional[np.ndarray] = None, 
                 damping:  float = 0.99, use_gpu: bool = False):
        self.gravity = gravity_vector or np.array([0, -9.81, 0, 0])
        self.damping = damping
        self. particles:  List[Particle4D] = []
        self.forces: Dict[str, Callable] = {}
        self.time = 0.0
        self. use_gpu = use_gpu
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
    
    def add_particle(self, position: np.ndarray, velocity: np.ndarray, 
                    mass: float, charge: float = 0.0, spin: float = 0.0):
        particle = Particle4D(
            position=position. astype(np.float64),
            velocity=velocity.astype(np.float64),
            acceleration=np.zeros(4, dtype=np.float64),
            mass=mass,
            charge=charge,
            spin=spin,
            energy=0.5 * mass * np.dot(velocity, velocity)
        )
        self.particles.append(particle)
    
    def add_force(self, name: str, force_function: Callable[[Particle4D, List[Particle4D], float], np.ndarray]):
        self.forces[name] = force_function
    
    def gravitational_force(self, particle:  Particle4D, others: List[Particle4D], 
                           G: float = 6.674e-11) -> np.ndarray:
        force = np.zeros(4)
        for other in others: 
            if other is particle:
                continue
            
            diff = other.position - particle.position
            distance = np.linalg. norm(diff) + 1e-10
            
            f_magnitude = G * particle.mass * other.mass / (distance ** 2)
            force += f_magnitude * (diff / distance)
        
        return force
    
    def electromagnetic_force(self, particle:  Particle4D, others: List[Particle4D],
                             k: float = 8.988e9) -> np.ndarray:
        if particle.charge == 0:
            return np.zeros(4)
        
        force = np. zeros(4)
        for other in others:
            if other is particle or other.charge == 0:
                continue
            
            diff = other.position - particle.position
            distance = np.linalg.norm(diff) + 1e-10
            
            f_magnitude = k * particle.charge * other.charge / (distance ** 2)
            force += f_magnitude * (diff / distance)
        
        return force
    
    def viscous_drag(self, particle: Particle4D, drag_coefficient: float = 0.1) -> np.ndarray:
        return -drag_coefficient * particle.velocity
    
    def pressure_gradient_force(self, particle: Particle4D, pressure_field:  Callable[[np.ndarray], float],
                               epsilon: float = 1e-6) -> np.ndarray:
        grad = np.zeros(4)
        for i in range(4):
            pos_plus = particle.position. copy()
            pos_minus = particle.position.copy()
            pos_plus[i] += epsilon
            pos_minus[i] -= epsilon
            
            grad[i] = (pressure_field(pos_plus) - pressure_field(pos_minus)) / (2 * epsilon)
        
        return -grad * particle.mass
    
    def lorentz_force(self, particle: Particle4D, electric_field: np.ndarray,
                     magnetic_field: np.ndarray) -> np.ndarray:
        if particle.charge == 0:
            return np.zeros(4)
        
        electric_force = particle.charge * electric_field
        
        magnetic_force_3d = particle.charge * np.cross(particle.velocity[: 3], magnetic_field[: 3])
        magnetic_force = np.concatenate([magnetic_force_3d, np.array([0])])
        
        return electric_force + magnetic_force
    
    def update(self, dt: float = 0.016):
        for particle in self.particles:
            particle.acceleration = self.gravity.copy()
            
            for force_name, force_func in self.forces.items():
                try:
                    force = force_func(particle, self.particles, self.time)
                    particle.acceleration += force / particle.mass
                except: 
                    pass
            
            particle.velocity += particle.acceleration * dt
            particle.velocity *= self.damping
            
            particle.position += particle.velocity * dt
            
            particle.energy = 0.5 * particle. mass * np.dot(particle. velocity, particle.velocity)
        
        self.time += dt
    
    def get_total_kinetic_energy(self) -> float:
        total = 0.0
        for particle in self. particles:
            total += 0.5 * particle.mass * np.dot(particle.velocity, particle.velocity)
        return total
    
    def get_total_momentum(self) -> np.ndarray:
        total = np.zeros(4)
        for particle in self.particles:
            total += particle.mass * particle.velocity
        return total
    
    def get_center_of_mass(self) -> np.ndarray:
        total_mass = sum(p.mass for p in self.particles)
        if total_mass == 0:
            return np. zeros(4)
        
        com = np.zeros(4)
        for particle in self.particles:
            com += particle.mass * particle.position
        
        return com / total_mass


class RelativityEngine4D:
    
    def __init__(self, c: float = 3e8):
        self.c = c
    
    def lorentz_factor(self, velocity: np.ndarray) -> float:
        v_squared = np.dot(velocity, velocity)
        if v_squared >= self.c ** 2:
            return float('inf')
        return 1.0 / np.sqrt(1.0 - v_squared / (self.c ** 2))
    
    def relativistic_energy(self, mass: float, velocity: np.ndarray) -> float:
        gamma = self.lorentz_factor(velocity)
        return gamma * mass * (self.c ** 2)
    
    def relativistic_momentum(self, mass: float, velocity: np.ndarray) -> np.ndarray:
        gamma = self.lorentz_factor(velocity)
        return gamma * mass * velocity
    
    def four_momentum(self, mass: float, velocity: np.ndarray) -> np.ndarray:
        gamma = self.lorentz_factor(velocity)
        energy = gamma * mass * (self.c ** 2)
        momentum = gamma * mass * velocity
        return np.concatenate([[energy / self.c], momentum])
    
    def spacetime_interval(self, event1: np.ndarray, event2: np.ndarray) -> float:
        dt = event2[0] - event1[0]
        dx = event2[1] - event1[1]
        dy = event2[2] - event1[2]
        dz = event2[3] - event1[3]
        
        interval_squared = (self.c * dt) ** 2 - (dx ** 2 + dy ** 2 + dz ** 2)
        return np.sqrt(abs(interval_squared)) if interval_squared >= 0 else -np.sqrt(abs(interval_squared))


class QuantumMechanics4D:
    
    def __init__(self):
        self.hbar = 1.054571817e-34
        self.m_e = 9.1093837015e-31
    
    def schrodinger_equation_solver(self, potential: Callable[[np.ndarray], float],
                                   initial_state:  np.ndarray,
                                   dt: float = 1e-6,
                                   steps: int = 100) -> List[np.ndarray]:
        
        states = [initial_state. copy()]
        current_state = initial_state.copy()
        
        for _ in range(steps):
            kinetic_energy = np.abs(np.fft.fft(current_state)) ** 2
            
            potential_energy = np.array([potential(np.array([i, 0, 0, 0])) 
                                        for i in range(len(current_state))])
            
            total_energy = kinetic_energy[: len(potential_energy)] + potential_energy
            
            phase = np.exp(-1j * total_energy * dt / self.hbar)
            current_state = current_state * phase
            
            current_state = current_state / np.linalg.norm(current_state)
            states.append(current_state.copy())
        
        return states
    
    def probability_density(self, wavefunction: np.ndarray) -> np.ndarray:
        return np.abs(wavefunction) ** 2
    
    def expectation_value(self, wavefunction: np.ndarray, observable: np.ndarray) -> float:
        psi_conj = np.conj(wavefunction)
        return float(np.real(np.dot(psi_conj, observable @ wavefunction)))