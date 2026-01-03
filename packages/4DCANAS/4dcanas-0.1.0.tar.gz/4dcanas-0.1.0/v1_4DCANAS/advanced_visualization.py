import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import matplotlib.cm as cm
from typing import List, Tuple, Optional, Dict, Any
import json
from datetime import datetime

class ProjectionEngine:
    
    @staticmethod
    def orthogonal_projection_4d_to_3d(point_4d: np.ndarray) -> np.ndarray:
        return point_4d[: 3]
    
    @staticmethod
    def perspective_projection_4d_to_3d(point_4d:  np.ndarray, 
                                       distance: float = 2.0) -> np.ndarray:
        w = point_4d[3]
        scale = distance / (distance + w)
        return point_4d[: 3] * scale
    
    @staticmethod
    def stereographic_projection(point_4d: np.ndarray, 
                                pole:  float = 1.0) -> np.ndarray:
        if abs(point_4d[3] - pole) < 1e-10:
            return point_4d[: 3] * 1e6
        
        scale = 2 / (pole - point_4d[3])
        return point_4d[:3] * scale
    
    @staticmethod
    def slicing_projection_4d_to_3d(point_4d: np.ndarray, 
                                    w_slice: float = 0.0) -> Optional[np.ndarray]:
        if abs(point_4d[3] - w_slice) < 0.1:
            return point_4d[:3]
        return None


class AdvancedVisualizer4D:
    
    def __init__(self, figsize: Tuple[int, int] = (14, 10),
                 high_quality: bool = True):
        self.figsize = figsize
        self.high_quality = high_quality
        self. projection_engine = ProjectionEngine()
        self.colormap = cm.viridis
    
    def visualize_with_lighting(self, vertices_4d: List[np.ndarray],
                               edges:  List[Tuple[int, int]],
                               light_position: np.ndarray = None,
                               ambient_light: float = 0.3) -> plt.Figure:
        
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        light_pos = light_position or np.array([2, 2, 2])
        
        vertices_3d = np.array([self.projection_engine.perspective_projection_4d_to_3d(v) 
                               for v in vertices_4d])
        
        vertex_colors = []
        for v in vertices_3d:
            to_light = light_pos - v
            distance = np.linalg. norm(to_light)
            intensity = ambient_light + (1 - ambient_light) / (1 + distance)
            vertex_colors.append(intensity)
        
        vertex_colors = np.array(vertex_colors)
        
        scatter = ax.scatter(vertices_3d[:, 0], vertices_3d[:, 1], vertices_3d[:, 2],
                            c=vertex_colors, cmap=self.colormap, s=100, 
                            alpha=0.8, edgecolors='black', linewidth=1)
        
        for edge in edges:
            p1, p2 = vertices_3d[edge[0]], vertices_3d[edge[1]]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                   'b-', alpha=0.4, linewidth=1.5)
        
        ax. set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('4D Object with Advanced Lighting')
        
        plt.colorbar(scatter, ax=ax, label='Light Intensity')
        
        return fig
    
    def multi_projection_view(self, vertices_4d:  List[np.ndarray],
                             edges: List[Tuple[int, int]]) -> plt.Figure:
        
        fig = plt.figure(figsize=(16, 12))
        
        projections = [
            ('Orthogonal', self.projection_engine.orthogonal_projection_4d_to_3d),
            ('Perspective', self. projection_engine.perspective_projection_4d_to_3d),
            ('Stereographic', self.projection_engine.stereographic_projection),
        ]
        
        for idx, (name, projection_func) in enumerate(projections, 1):
            ax = fig.add_subplot(2, 2, idx, projection='3d')
            
            vertices_proj = np.array([projection_func(v) for v in vertices_4d])
            
            ax.scatter(vertices_proj[:, 0], vertices_proj[:, 1], vertices_proj[:, 2],
                      c='red', s=80, alpha=0.7)
            
            for edge in edges:
                p1, p2 = vertices_proj[edge[0]], vertices_proj[edge[1]]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                       'b-', alpha=0.5)
            
            ax.set_title(f'{name} Projection')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
        
        return fig
    
    def time_evolution_animation(self, shape_generator: callable,
                                time_steps: int = 100,
                                interval: int = 50) -> FuncAnimation:
        
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        def update(frame):
            ax.clear()
            
            t = frame / time_steps
            vertices_4d, edges = shape_generator(t)
            
            vertices_3d = np.array([self.projection_engine.perspective_projection_4d_to_3d(v)
                                   for v in vertices_4d])
            
            w_values = np.array([v[3] for v in vertices_4d])
            normalized_w = (w_values - w_values.min()) / (w_values.max() - w_values.min() + 1e-10)
            
            ax.scatter(vertices_3d[: , 0], vertices_3d[:, 1], vertices_3d[:, 2],
                      c=normalized_w, cmap='plasma', s=100, alpha=0.8)
            
            for edge in edges: 
                p1, p2 = vertices_3d[edge[0]], vertices_3d[edge[1]]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                       'b-', alpha=0.4)
            
            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            ax.set_zlim(-2, 2)
            ax.set_title(f'4D Evolution (t={t:.2f})')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
        
        anim = FuncAnimation(fig, update, frames=time_steps, interval=interval)
        return anim
    
    def heatmap_4d_field(self, field_function: callable,
                        x_range: Tuple[float, float] = (-2, 2),
                        y_range: Tuple[float, float] = (-2, 2),
                        z_range: Tuple[float, float] = (-2, 2),
                        w_slice: float = 0.0,
                        resolution: int = 20) -> plt.Figure:
        
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111)
        
        x = np.linspace(*x_range, resolution)
        y = np.linspace(*y_range, resolution)
        X, Y = np.meshgrid(x, y)
        
        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                point = np.array([X[i, j], Y[i, j], z_range[0], w_slice])
                Z[i, j] = field_function(point)
        
        contour = ax.contourf(X, Y, Z, levels=20, cmap='viridis')
        ax.contour(X, Y, Z, levels=10, colors='black', alpha=0.3, linewidths=0.5)
        
        plt.colorbar(contour, ax=ax, label='Field Value')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'4D Field Heatmap (z={z_range[0]}, w={w_slice})')
        
        return fig


class InteractiveVisualizer4D: 
    
    def __init__(self):
        self.current_vertices = None
        self.current_edges = None
        self.rotation_angles = np.array([0, 0, 0, 0])
        self.translation = np.array([0, 0, 0, 0])
        self.scale = 1.0
        self.projection_engine = ProjectionEngine()
    
    def get_projected_vertices(self) -> np.ndarray:
        if self.current_vertices is None:
            return np.array([])
        
        rotated = np.array([self._rotate_4d(v, self.rotation_angles) 
                           for v in self. current_vertices])
        translated = rotated + self.translation
        scaled = translated * self.scale
        
        return np.array([self.projection_engine.perspective_projection_4d_to_3d(v)
                        for v in scaled])
    
    def _rotate_4d(self, point: np. ndarray, angles: np.ndarray) -> np.ndarray:
        x, y, z, w = point
        
        ax, ay, az, aw = angles
        
        cos_x, sin_x = np.cos(ax), np.sin(ax)
        cos_y, sin_y = np.cos(ay), np.sin(ay)
        cos_z, sin_z = np.cos(az), np.sin(az)
        cos_w, sin_w = np. cos(aw), np.sin(aw)
        
        ry = np.array([y * cos_x - z * sin_x, y * sin_x + z * cos_x])
        y, z = ry
        
        rx = np.array([x * cos_y + z * sin_y, x * (-sin_y) + z * cos_y])
        x, z = rx
        
        rz = np.array([x * cos_z - y * sin_z, x * sin_z + y * cos_z])
        x, y = rz
        
        rw = np.array([x * cos_w - w * sin_w, x * sin_w + w * cos_w])
        x, w = rw
        
        return np. array([x, y, z, w])