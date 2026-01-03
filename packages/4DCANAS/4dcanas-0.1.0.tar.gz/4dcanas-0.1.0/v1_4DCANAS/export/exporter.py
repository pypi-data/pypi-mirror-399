import numpy as np
import json
import os
from typing import List, Tuple, Dict, Any, Optional

class AdvancedExportTools:
    """Professional export tools for 4D shapes"""
    
    @staticmethod
    def quick_export(
        shape: Dict[str, Any],
        format: str = "obj",
        filename: Optional[str] = None,
        auto_open: bool = False,
    ) -> str:
        """Quick export to any format"""
        
        if filename is None:
            filename = f"4d_shape_{len(os.listdir('. '))}.{format}"
        
        vertices = np.array(shape["vertices"])
        edges = shape.get("edges", [])
        
        if format == "obj":
            AdvancedExportTools._export_obj(vertices, edges, filename)
        elif format == "json": 
            AdvancedExportTools._export_json(shape, filename)
        elif format == "gltf":
            AdvancedExportTools._export_gltf(vertices, edges, filename)
        
        return filename
    
    @staticmethod
    def _export_obj(vertices: np.ndarray, edges: List[Tuple[int, int]], filename: str) -> None:
        with open(filename, "w") as f:
            f.write("# 4DCANAS v1.0.0 Auto-Generated OBJ\n")
            f.write(f"# {len(vertices)} vertices, {len(edges)} edges\n\n")
            
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:. 6f} {v[2]:.6f}\n")
            
            f.write("\n")
            
            for edge in edges:
                f.write(f"l {edge[0]+1} {edge[1]+1}\n")
    
    @staticmethod
    def _export_json(shape: Dict[str, Any], filename: str) -> None:
        serializable = {
            "type":  shape.get("type", "unknown"),
            "vertices": [
                v.tolist() if isinstance(v, np.ndarray) else v
                for v in shape["vertices"]
            ],
            "edges": shape.get("edges", []),
        }
        
        with open(filename, "w") as f:
            json.dump(serializable, f, indent=2)
    
    @staticmethod
    def _export_gltf(
        vertices: np.ndarray, edges: List[Tuple[int, int]], filename: str
    ) -> None:
        gltf = {
            "asset": {"version": "2.0"},
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [
                {
                    "primitives": [
                        {
                            "attributes": {"POSITION": 0},
                            "indices": 1,
                            "mode": 1,
                        }
                    ]
                }
            ],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,
                    "count": len(vertices),
                    "type": "VEC3",
                },
                {
                    "bufferView": 1,
                    "componentType": 5125,
                    "count": len(edges) * 2,
                    "type": "SCALAR",
                },
            ],
            "bufferViews": [
                {"buffer": 0, "byteOffset": 0, "byteStride": 12},
                {"buffer": 0, "byteOffset": len(vertices) * 12},
            ],
            "buffers": [
                {"byteLength": len(vertices) * 12 + len(edges) * 8}
            ],
        }
        
        with open(filename, "w") as f:
            json.dump(gltf, f, indent=2)
    
    @staticmethod
    def batch_export(
        shapes: List[Dict[str, Any]],
        formats: List[str],
        output_dir: str = "./exports",
    ) -> Dict[str, Dict[str, str]]:
        """Batch export multiple shapes"""
        
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        
        for shape_idx, shape in enumerate(shapes):
            shape_dir = os.path.join(output_dir, f"shape_{shape_idx}")
            os.makedirs(shape_dir, exist_ok=True)
            
            results[f"shape_{shape_idx}"] = {}
            
            for fmt in formats:
                filename = os.path.join(shape_dir, f"export. {fmt}")
                AdvancedExportTools.quick_export(shape, format=fmt, filename=filename)
                results[f"shape_{shape_idx}"][fmt] = filename
        
        return results