import numpy as np
import json
from typing import List, Tuple, Dict, Any, Optional
import subprocess
import os

class AdvancedExportTools:
    
    @staticmethod
    def quick_export(shape: Dict[str, Any],
                    format: str = 'obj',
                    filename: Optional[str] = None,
                    auto_open: bool = False) -> str:
        
        if filename is None:
            filename = f"4d_shape_{len(os.listdir('. '))}.{format}"
        
        vertices = np.array(shape['vertices'])
        edges = shape.get('edges', [])
        
        if format == 'obj':
            AdvancedExportTools.export_obj_fast(vertices, edges, filename)
        elif format == 'json': 
            AdvancedExportTools.export_json_fast(shape, filename)
        elif format == 'gltf':
            AdvancedExportTools. export_gltf_fast(vertices, edges, filename)
        elif format == 'blend':
            AdvancedExportTools.export_blender_fast(vertices, edges, filename)
        elif format == 'ply':
            AdvancedExportTools.export_ply_fast(vertices, edges, filename)
        
        if auto_open:
            try:
                if format == 'obj':
                    os.system(f'start "{filename}"' if os.name == 'nt' else f'open "{filename}"')
            except:
                pass
        
        return filename
    
    @staticmethod
    def export_obj_fast(vertices: np.ndarray, edges: List[Tuple[int, int]], filename: str):
        
        with open(filename, 'w') as f:
            f.write('# 4DCANAS Auto-Generated OBJ\n')
            f.write(f'# {len(vertices)} vertices, {len(edges)} edges\n\n')
            
            for v in vertices:
                f.write(f'v {v[0]:.6f} {v[1]:. 6f} {v[2]:.6f}\n')
            
            f.write('\n')
            
            for edge in edges:
                f.write(f'l {edge[0]+1} {edge[1]+1}\n')
    
    @staticmethod
    def export_json_fast(shape:  Dict[str, Any], filename:  str):
        
        serializable = {
            'type': shape. get('type', 'unknown'),
            'vertices': [v.tolist() if isinstance(v, np.ndarray) else v for v in shape['vertices']],
            'edges': shape.get('edges', []),
            'metadata': shape.get('metadata', {})
        }
        
        with open(filename, 'w') as f:
            json.dump(serializable, f, indent=2)
    
    @staticmethod
    def export_gltf_fast(vertices: np.ndarray, edges: List[Tuple[int, int]], filename: str):
        
        gltf = {
            'asset': {'version': '2.0'},
            'scenes':  [{'nodes': [0]}],
            'nodes': [{'mesh': 0}],
            'meshes': [{
                'primitives': [{
                    'attributes': {'POSITION': 0},
                    'indices': 1,
                    'mode': 1
                }]
            }],
            'accessors': [
                {
                    'bufferView': 0,
                    'componentType': 5126,
                    'count': len(vertices),
                    'type': 'VEC3'
                },
                {
                    'bufferView': 1,
                    'componentType': 5125,
                    'count': len(edges) * 2,
                    'type': 'SCALAR'
                }
            ],
            'bufferViews': [
                {'buffer': 0, 'byteOffset': 0, 'byteStride': 12},
                {'buffer': 0, 'byteOffset': len(vertices) * 12}
            ],
            'buffers': [{'byteLength': len(vertices) * 12 + len(edges) * 8}]
        }
        
        with open(filename, 'w') as f:
            json.dump(gltf, f, indent=2)
    
    @staticmethod
    def export_blender_fast(vertices: np. ndarray, edges: List[Tuple[int, int]], filename:  str):
        
        script = '''import bpy

mesh = bpy.data.meshes.new('Tesseract4D')
obj = bpy.data.objects.new('Tesseract4D', mesh)
bpy.context.collection.objects.link(obj)

verts = [
'''
        
        for v in vertices:
            script += f'    ({v[0]:.6f}, {v[1]:.6f}, {v[2]:.6f}),\n'
        
        script += '''
]

edges = [
'''
        
        for edge in edges:
            script += f'    ({edge[0]}, {edge[1]}),\n'
        
        script += '''
]

mesh.from_pydata(verts, edges, [])
mesh.update()

bpy.context.view_layer.objects.active = obj
obj.select_set(True)
'''
        
        with open(filename, 'w') as f:
            f.write(script)
    
    @staticmethod
    def export_ply_fast(vertices: np.ndarray, edges: List[Tuple[int, int]], filename: str):
        
        with open(filename, 'w') as f:
            f.write('ply\n')
            f.write('format ascii 1.0\n')
            f.write(f'element vertex {len(vertices)}\n')
            f.write('property float x\n')
            f.write('property float y\n')
            f.write('property float z\n')
            f.write(f'element edge {len(edges)}\n')
            f.write('property uchar vertex1\n')
            f.write('property uchar vertex2\n')
            f.write('end_header\n')
            
            for v in vertices:
                f.write(f'{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
            
            for edge in edges:
                f.write(f'{edge[0]} {edge[1]}\n')
    
    @staticmethod
    def export_animation_sequence(frames: List[Dict[str, Any]],
                                 output_dir: str,
                                 format: str = 'obj') -> str:
        
        os.makedirs(output_dir, exist_ok=True)
        
        for frame_idx, frame in enumerate(frames):
            filename = os.path.join(output_dir, f'frame_{frame_idx: 06d}.{format}')
            AdvancedExportTools.quick_export(frame, format=format, filename=filename)
        
        return output_dir
    
    @staticmethod
    def batch_export(shapes: List[Dict[str, Any]],
                    formats: List[str],
                    output_dir: str = './exports'):
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = {}
        
        for shape_idx, shape in enumerate(shapes):
            shape_dir = os.path.join(output_dir, f'shape_{shape_idx}')
            os.makedirs(shape_dir, exist_ok=True)
            
            results[f'shape_{shape_idx}'] = {}
            
            for fmt in formats:
                filename = os.path.join(shape_dir, f'export. {fmt}')
                AdvancedExportTools.quick_export(shape, format=fmt, filename=filename)
                results[f'shape_{shape_idx}'][fmt] = filename
        
        return results