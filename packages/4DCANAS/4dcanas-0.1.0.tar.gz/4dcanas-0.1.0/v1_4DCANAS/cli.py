import argparse
import sys
import numpy as np
from . core import Tesseract, Point4D
from .visualization import MatplotlibVisualizer, OpenGLVisualizer
from . export import ExportManager

def main():
    parser = argparse.ArgumentParser(description='4DCANAS - 4D Visualization Suite')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    visualize_parser = subparsers.add_parser('visualize', help='Visualize a tesseract')
    visualize_parser.add_argument('--renderer', choices=['matplotlib', 'opengl'], 
                                  default='matplotlib', help='Visualization renderer')
    visualize_parser.add_argument('--rx', type=float, default=0, help='Rotation around X axis')
    visualize_parser.add_argument('--ry', type=float, default=0, help='Rotation around Y axis')
    visualize_parser. add_argument('--rz', type=float, default=0, help='Rotation around Z axis')
    visualize_parser.add_argument('--rw', type=float, default=0, help='Rotation around W axis')
    visualize_parser.add_argument('--size', type=float, default=1.0, help='Tesseract size')
    
    animate_parser = subparsers.add_parser('animate', help='Animate a rotating tesseract')
    animate_parser.add_argument('--frames', type=int, default=100, help='Number of frames')
    animate_parser.add_argument('--speed', type=float, default=0.05, help='Rotation speed')
    animate_parser.add_argument('--size', type=float, default=1.0, help='Tesseract size')
    
    export_parser = subparsers. add_parser('export', help='Export tesseract to file')
    export_parser.add_argument('--format', choices=['obj', 'json', 'gltf'], 
                               default='obj', help='Export format')
    export_parser.add_argument('--output', required=True, help='Output filename')
    export_parser.add_argument('--size', type=float, default=1.0, help='Tesseract size')
    
    gui_parser = subparsers. add_parser('gui', help='Launch GUI application')
    
    args = parser.parse_args()
    
    if args.command == 'visualize': 
        tesseract = Tesseract(size=args.size)
        angles = np.array([args.rx, args.ry, args.rz, args.rw])
        if np.any(angles != 0):
            tesseract.rotate(angles)
        
        if args.renderer == 'matplotlib': 
            visualizer = MatplotlibVisualizer()
            visualizer.visualize(tesseract)
            import matplotlib.pyplot as plt
            plt.show()
        else:
            visualizer = OpenGLVisualizer()
            visualizer.visualize(tesseract)
    
    elif args.command == 'animate':
        tesseract = Tesseract(size=args.size)
        visualizer = MatplotlibVisualizer()
        visualizer.animate(tesseract, frames=args.frames, rotation_speed=args.speed)
        import matplotlib.pyplot as plt
        plt.show()
    
    elif args.command == 'export':
        tesseract = Tesseract(size=args.size)
        
        if args.format == 'obj':
            ExportManager. export_obj(tesseract, args.output)
        elif args.format == 'json': 
            ExportManager.export_json(tesseract, args.output)
        elif args.format == 'gltf':
            ExportManager.export_gltf(tesseract, args. output)
        
        print(f"Exported to {args.output}")
    
    elif args.command == 'gui':
        from .gui import launch_gui
        launch_gui()
    
    else:
        parser.print_help()

if __name__ == '__main__': 
    main()