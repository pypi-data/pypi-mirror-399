"""
تكامل جوبيتر التفاعلي
Jupyter Interactive Integration

الإصدار:  1.0.0
Version: 1.0.0

المطور:  MERO
Developer:  MERO

جميع الحقوق محفوظة © 2025 MERO
All Rights Reserved © 2025 MERO
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
import json

class JupyterInteractive4D:
    
    def __init__(self):
        self.current_shape = None
        self. current_analysis = None
        self.visualization_data = {}
        self.version = "1.0.0"
        self.developer = "MERO"
    
    def enable_interactive_plot(self):
        try:
            import ipywidgets as widgets
            from IPython.display import display, clear_output
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            
            self.widgets = widgets
            self.display = display
            self.clear_output = clear_output
            self.plt = plt
            
            return True
        except ImportError: 
            print("تثبيت ipywidgets و matplotlib مطلوب | ipywidgets and matplotlib required")
            return False
    
    def interactive_3d_plot(self, shape: Dict[str, Any]):
        if not self.enable_interactive_plot():
            return
        
        vertices = np.array(shape['vertices'])
        edges = shape. get('edges', [])
        
        rotation_x = self.widgets.FloatSlider(
            value=0, min=-np.pi, max=np. pi, step=0.01,
            description='تدوير X | Rotate X:'
        )
        
        rotation_y = self.widgets.FloatSlider(
            value=0, min=-np.pi, max=np.pi, step=0.01,
            description='تدوير Y | Rotate Y:'
        )
        
        rotation_z = self.widgets.FloatSlider(
            value=0, min=-np. pi, max=np.pi, step=0.01,
            description='تدوير Z | Rotate Z:'
        )
        
        rotation_w = self.widgets.FloatSlider(
            value=0, min=-np.pi, max=np.pi, step=0.01,
            description='تدوير W | Rotate W:'
        )
        
        projection_type = self.widgets. Dropdown(
            options=['متعامد | Orthogonal', 'منظوري | Perspective', 'ستيريوغرافي | Stereographic'],
            value='متعامد | Orthogonal',
            description='الإسقاط | Projection:'
        )
        
        scale_slider = self.widgets.FloatSlider(
            value=1.0, min=0.1, max=5.0, step=0.1,
            description='الحجم | Scale:'
        )
        
        def update_plot(rx, ry, rz, rw, proj, scale):
            self.clear_output(wait=True)
            
            from 4DCANAS import Rotation4D, ProjectionEngine
            
            angles = np.array([rx, ry, rz, rw])
            rotation = Rotation4D(angles)
            
            from 4DCANAS import Point4D
            rotated_vertices = []
            for v in vertices:
                p4d = Point4D(*v) if len(v) == 4 else Point4D(v[0], v[1], v[2], 0)
                rotated = rotation.apply(p4d)
                rotated_vertices.append(rotated. coords)
            
            rotated_vertices = np.array(rotated_vertices) * scale
            
            proj_engine = ProjectionEngine()
            if 'Orthogonal' in proj or 'متعامد' in proj:
                proj_func = proj_engine.orthogonal_projection_4d_to_3d
            elif 'Perspective' in proj or 'منظوري' in proj:
                proj_func = proj_engine.perspective_projection_4d_to_3d
            else:
                proj_func = proj_engine.stereographic_projection
            
            projected = [proj_func(v) for v in rotated_vertices]
            projected = np.array(projected)
            
            fig = self.plt.figure(figsize=(10, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            ax.scatter(projected[:, 0], projected[:, 1], projected[:, 2],
                      c='red', s=100, alpha=0.8)
            
            for edge in edges:
                if edge[0] < len(projected) and edge[1] < len(projected):
                    p1, p2 = projected[edge[0]], projected[edge[1]]
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                           'b-', alpha=0.6)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('4DCANAS | Interactive 4D Visualization')
            
            self.display(fig)
            self.plt.close()
        
        self.display(self.widgets.interactive(
            update_plot,
            rx=rotation_x,
            ry=rotation_y,
            rz=rotation_z,
            rw=rotation_w,
            proj=projection_type,
            scale=scale_slider
        ))
    
    def interactive_analysis_dashboard(self, shape: Dict[str, Any]):
        if not self.enable_interactive_plot():
            return
        
        from 4DCANAS import DeepAnalyzer4D
        
        analyzer = DeepAnalyzer4D()
        vertices = np.array(shape['vertices'])
        
        analysis = analyzer.analyze_shape(vertices, shape. get('edges'))
        
        analysis_type = self.widgets.Dropdown(
            options=[
                'الخصائص الهندسية | Geometric Properties',
                'الخصائص الطوبولوجية | Topological Properties',
                'تحليل التماثل | Symmetry Analysis',
                'تحليل الاستقرار | Stability Analysis',
                'النتائج الجبرية | Algebraic Properties'
            ],
            description='الفئة | Category:'
        )
        
        def display_analysis(category):
            self.clear_output(wait=True)
            
            if 'Geometric' in category or 'الخصائص الهندسية' in category:
                data = analysis['geometric_properties']
            elif 'Topological' in category or 'الخصائص الطوبولوجية' in category:
                data = analysis['topological_properties']
            elif 'Symmetry' in category or 'التماثل' in category: 
                data = analysis['symmetry_analysis']
            elif 'Stability' in category or 'الاستقرار' in category:
                data = analysis['stability_analysis']
            else: 
                data = analysis['algebraic_properties']
            
            self.display(self.widgets.HTML(f"<pre>{json.dumps(data, indent=2)}</pre>"))
        
        self.display(self.widgets.interactive(display_analysis, category=analysis_type))
    
    def export_to_notebook(self, shape: Dict[str, Any], format_type: str = 'json'):
        from 4DCANAS import AdvancedExportTools
        
        filename = f"4d_shape_{id(shape)}.{format_type}"
        AdvancedExportTools.quick_export(shape, format=format_type, filename=filename)
        
        self.display(self.widgets.HTML(f"تم التصدير إلى | Exported to: <b>{filename}</b>"))
    
    def create_animation_slider(self, timeline: List[np.ndarray]):
        if not self.enable_interactive_plot():
            return
        
        frame_slider = self.widgets.IntSlider(
            value=0,
            min=0,
            max=len(timeline) - 1,
            step=1,
            description='الإطار | Frame:'
        )
        
        def display_frame(frame_idx):
            self.clear_output(wait=True)
            
            vertices = timeline[frame_idx]
            
            fig = self.plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            ax. scatter(vertices[:, 0], vertices[:, 1], vertices[: , 2],
                      c='blue', s=100)
            
            ax.set_title(f'Frame {frame_idx + 1} / {len(timeline)}')
            self.display(fig)
            self.plt.close()
        
        self.display(self.widgets.interactive(display_frame, frame_idx=frame_slider))