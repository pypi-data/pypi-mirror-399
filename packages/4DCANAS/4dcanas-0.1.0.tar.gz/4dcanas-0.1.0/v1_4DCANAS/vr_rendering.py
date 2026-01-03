import numpy as np
from typing import Dict, List, Tuple, Optional
import torch

class VRRenderingEngine:
    
    def __init__(self, eye_separation: float = 0.064, focal_length: float = 0.5):
        self.eye_separation = eye_separation
        self.focal_length = focal_length
        self.left_eye_matrix = self._create_eye_matrix(-eye_separation / 2)
        self.right_eye_matrix = self._create_eye_matrix(eye_separation / 2)
    
    def _create_eye_matrix(self, eye_offset: float) -> np.ndarray:
        matrix = np.eye(4)
        matrix[0, 3] = eye_offset
        return matrix
    
    def generate_stereoscopic_pair(self, vertices_4d: List[np.ndarray],
                                  edges:  List[Tuple[int, int]]) -> Tuple[Dict, Dict]:
        
        projected_left = self._project_to_eye(vertices_4d, self.left_eye_matrix)
        projected_right = self._project_to_eye(vertices_4d, self.right_eye_matrix)
        
        left_view = {
            'vertices': projected_left,
            'edges':  edges,
            'resolution': (1280, 1440)
        }
        
        right_view = {
            'vertices': projected_right,
            'edges': edges,
            'resolution': (1280, 1440)
        }
        
        return left_view, right_view
    
    def _project_to_eye(self, vertices_4d: List[np.ndarray],
                       eye_matrix: np.ndarray) -> List[np.ndarray]: 
        
        projected = []
        
        for vertex in vertices_4d:
            vertex_homo = np.concatenate([vertex, [1.0]])
            eye_vertex = eye_matrix @ vertex_homo
            
            w = eye_vertex[3]
            scale = self.focal_length / (self.focal_length + w + 1e-10)
            projected_vertex = eye_vertex[: 3] * scale
            
            projected.append(projected_vertex)
        
        return projected
    
    def apply_vr_distortion(self, vertex_2d: np.ndarray,
                           barrel_distortion: float = 0.2) -> np.ndarray:
        
        center = np.array([0.5, 0.5])
        normalized = vertex_2d / np.array([1920, 1080])
        
        displacement = normalized - center
        radius = np.linalg.norm(displacement)
        
        distorted_radius = radius + barrel_distortion * radius ** 3
        
        if radius > 0:
            distorted = center + (displacement / radius) * distorted_radius
        else:
            distorted = center
        
        return distorted * np.array([1920, 1080])
    
    def calculate_depth_cue(self, vertex_4d: np.ndarray) -> float:
        
        distance = np.linalg.norm(vertex_4d)
        
        depth_cue = np.exp(-distance / 10.0)
        
        return np.clip(depth_cue, 0. 0, 1.0)
    
    def apply_motion_blur(self, vertex_4d: np.ndarray,
                         velocity_4d: np.ndarray,
                         blur_amount: float = 0.01) -> np.ndarray:
        
        blur_offset = velocity_4d * blur_amount
        
        return vertex_4d + blur_offset


class ARRenderingEngine:
    
    def __init__(self, camera_resolution: Tuple[int, int] = (1920, 1080)):
        self.camera_resolution = camera_resolution
        self.camera_intrinsics = self._estimate_camera_intrinsics()
    
    def _estimate_camera_intrinsics(self) -> np.ndarray:
        
        fx = self.camera_resolution[0] / 2
        fy = self.camera_resolution[1] / 2
        cx = self.camera_resolution[0] / 2
        cy = self.camera_resolution[1] / 2
        
        return np.array([
            [fx,  0, cx],
            [ 0, fy, cy],
            [ 0,  0,  1]
        ])
    
    def project_4d_onto_camera_frame(self, point_4d: np.ndarray,
                                    camera_pose: np.ndarray) -> np.ndarray:
        
        point_3d = point_4d[: 3]
        
        point_camera = camera_pose[: 3, :3] @ point_3d + camera_pose[:3, 3]
        
        if point_camera[2] > 0:
            point_normalized = point_camera[: 2] / point_camera[2]
            point_pixel = self.camera_intrinsics @ np.array([point_normalized[0], point_normalized[1], 1])
            return point_pixel[: 2]
        
        return np.array([-9999, -9999])
    
    def render_occlusion_aware(self, foreground_depth: np.ndarray,
                              virtual_object_depth: float) -> np.ndarray:
        
        occluded = foreground_depth < virtual_object_depth
        
        return occluded
    
    def apply_shadow_mapping(self, vertex_3d: np.ndarray,
                           light_position: np.ndarray,
                           shadow_map: np.ndarray) -> float:
        
        light_space_pos = (vertex_3d - light_position) / np.linalg.norm(vertex_3d - light_position)
        
        shadow_uv = ((light_space_pos[: 2] + 1) / 2 * np.array(shadow_map.shape)).astype(int)
        shadow_uv = np.clip(shadow_uv, 0, np.array(shadow_map.shape) - 1)
        
        shadow_depth = shadow_map[shadow_uv[0], shadow_uv[1]]
        vertex_depth = np.linalg.norm(vertex_3d - light_position)
        
        return 1.0 if vertex_depth <= shadow_depth + 0.1 else 0.3


class TelepresenceEngine4D:
    
    def __init__(self):
        self.avatar_position_4d = np.array([0. 0, 0.0, 0.0, 0.0])
        self.avatar_orientation = np.eye(4)
        self.network_latency = 0.016
        self.compression_ratio = 0.95
    
    def encode_4d_state(self, state_dict: Dict) -> bytes:
        
        encoded = b''
        
        for key, value in state_dict.items():
            if isinstance(value, np.ndarray):
                quantized = (value * 1000).astype(np.int16)
                encoded += quantized.tobytes()
        
        return encoded
    
    def decode_4d_state(self, encoded:  bytes, expected_shape: Tuple) -> Dict:
        
        decoded_array = np.frombuffer(encoded, dtype=np.int16)
        decoded_array = decoded_array.astype(np.float32) / 1000.0
        
        return {'state': decoded_array. reshape(expected_shape)}
    
    def predict_remote_avatar_position(self, last_position:  np.ndarray,
                                       last_velocity: np.ndarray,
                                       time_since_update: float) -> np.ndarray:
        
        predicted = last_position + last_velocity * time_since_update
        
        return predicted
    
    def apply_network_interpolation(self, old_state: np.ndarray,
                                   new_state: np.ndarray,
                                   interpolation_factor: float) -> np.ndarray:
        
        return (1 - interpolation_factor) * old_state + interpolation_factor * new_state