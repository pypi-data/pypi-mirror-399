import numpy as np
import json
from typing import List, Dict, Any
from .core import Point4D, Point3D, Tesseract

class ExportManager:
    @staticmethod
    def export_obj(tesseract: Tesseract, filename: str, perspective: float = 1.0):
        projected, edges = tesseract.get_3d_projection(perspective)
        
        with open(filename, 'w') as f:
            f.write("# 4DCANAS OBJ Export\n")
            f.write("# 4D Tesseract Projection to 3D\n\n")
            
            for point in projected:
                f.write(f"v {point.x:. 6f} {point.y:.6f} {point.z:.6f}\n")
            
            f.write("\n")
            
            for edge in edges:
                f.write(f"l {edge[0]+1} {edge[1]+1}\n")
    
    @staticmethod
    def export_json(tesseract: Tesseract, filename: str, perspective: float = 1.0):
        projected, edges = tesseract.get_3d_projection(perspective)
        
        data = {
            'format': '4DCANAS-JSON',
            'version': '1.0',
            'metadata': {
                'type': 'tesseract',
                'perspective':  perspective,
            },
            'vertices': [
                {'x': p.x, 'y': p.y, 'z': p.z} for p in projected
            ],
            'edges': [
                {'from': e[0], 'to': e[1]} for e in edges
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def export_gltf(tesseract: Tesseract, filename: str, perspective: float = 1.0):
        projected, edges = tesseract.get_3d_projection(perspective)
        
        vertices = []
        indices = []
        
        for point in projected:
            vertices.extend([point.x, point.y, point.z])
        
        for edge in edges: 
            indices.append(edge[0])
            indices.append(edge[1])
        
        gltf_data = {
            'asset': {'version': '2.0'},
            'scenes': [{'nodes': [0]}],
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
                    'count': len(projected),
                    'type': 'VEC3'
                },
                {
                    'bufferView': 1,
                    'componentType': 5125,
                    'count': len(indices),
                    'type': 'SCALAR'
                }
            ],
            'bufferViews': [
                {
                    'buffer': 0,
                    'byteOffset':  0,
                    'byteStride': 12,
                    'target': 34962
                },
                {
                    'buffer': 0,
                    'byteOffset': len(vertices) * 4,
                    'target': 34963
                }
            ],
            'buffers': [
                {
                    'byteLength': (len(vertices) + len(indices)) * 4,
                    'uri': 'data:application/octet-stream;base64,' + 'AAAA'
                }
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(gltf_data, f, indent=2)