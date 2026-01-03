import numpy as np

class AdvancedVisualizer4D:
    """Advanced 4D visualization"""
    
    def __init__(self, figsize=(14, 10), high_quality=True):
        self.figsize = figsize
        self. high_quality = high_quality
    
    def visualize_with_lighting(self, vertices_4d, edges):
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            
            fig = plt. figure(figsize=self.figsize)
            ax = fig. add_subplot(111, projection='3d')
            
            vertices_3d = np.array([v[: 3] if len(v) >= 3 else v for v in vertices_4d])
            
            ax.scatter(vertices_3d[: , 0], vertices_3d[:, 1], vertices_3d[:, 2],
                      c='red', s=100, alpha=0.8)
            
            for edge in edges:
                if edge[0] < len(vertices_3d) and edge[1] < len(vertices_3d):
                    p1, p2 = vertices_3d[edge[0]], vertices_3d[edge[1]]
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                           'b-', alpha=0.4)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('4D Object Visualization')
            
            return fig
        except ImportError: 
            print("Matplotlib not available")
            return None