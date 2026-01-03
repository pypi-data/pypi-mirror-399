import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Optional
from . core import Point4D, Point3D, Tesseract

class Visualizer4D:
    def __init__(self):
        self.figures = []
    
    def visualize(self, tesseract: Tesseract, perspective: float = 1.0):
        raise NotImplementedError("Subclass must implement visualize method")


class MatplotlibVisualizer(Visualizer4D):
    def __init__(self, figsize: Tuple[int, int] = (10, 10)):
        super().__init__()
        self.figsize = figsize
    
    def visualize(self, tesseract: Tesseract, perspective: float = 1.0):
        fig = plt. figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        projected, edges = tesseract.get_3d_projection(perspective)
        
        vertices_array = np.array([p.coords for p in projected])
        ax.scatter(vertices_array[:, 0], vertices_array[:, 1], vertices_array[:, 2], 
                  c='red', s=100, alpha=0.8)
        
        for edge in edges:
            p1, p2 = projected[edge[0]], projected[edge[1]]
            ax.plot([p1.x, p2.x], [p1.y, p2.y], [p1.z, p2.z], 'b-', alpha=0.6)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('4D Tesseract Projection')
        
        self.figures.append(fig)
        return fig
    
    def animate(self, tesseract: Tesseract, frames: int = 100, 
                rotation_speed: float = 0.05, interval: int = 50):
        fig = plt.figure(figsize=self. figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        def update(frame):
            ax.clear()
            
            angles = np.array([
                frame * rotation_speed,
                frame * rotation_speed * 0.7,
                frame * rotation_speed * 0.5,
                frame * rotation_speed * 0.3
            ])
            
            tesseract_copy = Tesseract(tesseract. center, tesseract.size)
            tesseract_copy. vertices = tesseract.vertices. copy()
            tesseract_copy.rotate(angles)
            
            projected, edges = tesseract_copy.get_3d_projection()
            
            vertices_array = np.array([p.coords for p in projected])
            ax.scatter(vertices_array[:, 0], vertices_array[:, 1], vertices_array[:, 2],
                      c='red', s=100, alpha=0.8)
            
            for edge in edges:
                p1, p2 = projected[edge[0]], projected[edge[1]]
                ax.plot([p1.x, p2.x], [p1.y, p2.y], [p1.z, p2.z], 'b-', alpha=0.6)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'4D Tesseract Animation (Frame {frame}/{frames})')
            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            ax.set_zlim(-2, 2)
        
        anim = FuncAnimation(fig, update, frames=frames, interval=interval, repeat=True)
        self.figures.append(fig)
        return anim


class OpenGLVisualizer(Visualizer4D):
    def __init__(self, width: int = 800, height:  int = 600):
        super().__init__()
        self.width = width
        self. height = height
    
    def visualize(self, tesseract: Tesseract, perspective: float = 1.0):
        try:
            from OpenGL.GL import *
            from OpenGL.GLU import *
            import pygame
            from pygame. locals import *
            
            pygame.init()
            display = (self.width, self. height)
            pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
            pygame.display.set_caption('4DCANAS - OpenGL Visualizer')
            
            gluPerspective(45, (self.width / self.height), 0.1, 50.0)
            glTranslatef(0, 0, -5)
            
            clock = pygame.time.Clock()
            rotation_angles = np.zeros(4)
            
            running = True
            while running: 
                for event in pygame.event. get():
                    if event. type == pygame.QUIT:
                        running = False
                
                rotation_angles += np.array([0. 01, 0.007, 0.005, 0.003])
                
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glClearColor(0.0, 0.0, 0.0, 1.0)
                
                glRotatef(1, 1, 1, 1)
                
                projected, edges = tesseract.get_3d_projection(perspective)
                
                glBegin(GL_POINTS)
                glColor3f(1, 0, 0)
                for point in projected:
                    glVertex3f(point.x, point.y, point.z)
                glEnd()
                
                glBegin(GL_LINES)
                glColor3f(0, 1, 0)
                for edge in edges:
                    p1, p2 = projected[edge[0]], projected[edge[1]]
                    glVertex3f(p1.x, p1.y, p1.z)
                    glVertex3f(p2.x, p2.y, p2.z)
                glEnd()
                
                pygame.display.flip()
                clock.tick(60)
            
            pygame.quit()
        
        except ImportError:
            print("OpenGL dependencies not found. Install pygame and PyOpenGL.")