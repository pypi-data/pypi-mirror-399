import numpy as np
import torch
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass

@dataclass
class GrabbableObject4D:
    object_id: str
    position_4d: np.ndarray
    rotation_4d: np.ndarray
    scale:  float
    mass: float
    is_grabbed: bool = False
    grabbing_hand: Optional[str] = None
    grab_offset: Optional[np.ndarray] = None
    physics_enabled: bool = True
    
    def grab(self, hand: str, hand_position: np.ndarray):
        self.is_grabbed = True
        self.grabbing_hand = hand
        self.grab_offset = self.position_4d - hand_position


class VRInteractionManager:
    
    def __init__(self):
        self.grabbable_objects: Dict[str, GrabbableObject4D] = {}
        self.selected_object: Optional[str] = None
        self.gesture_history = []
        self.gesture_recognition_enabled = True
    
    def add_grabbable_object(self, obj: GrabbableObject4D):
        self.grabbable_objects[obj.object_id] = obj
    
    def grab_object(self, object_id: str, hand: str, hand_position:  np.ndarray) -> bool:
        if object_id in self.grabbable_objects:
            obj = self.grabbable_objects[object_id]
            obj.grab(hand, hand_position)
            self.selected_object = object_id
            return True
        return False
    
    def release_object(self, object_id: str) -> bool:
        if object_id in self.grabbable_objects:
            obj = self. grabbable_objects[object_id]
            obj.is_grabbed = False
            obj.grabbing_hand = None
            obj.grab_offset = None
            return True
        return False
    
    def update_grabbed_object_position(self, object_id:  str, hand_position: np.ndarray) -> bool:
        if object_id in self.grabbable_objects:
            obj = self.grabbable_objects[object_id]
            if obj.is_grabbed and obj.grab_offset is not None:
                obj.position_4d = hand_position + obj.grab_offset
                return True
        return False
    
    def rotate_grabbed_object(self, object_id: str, rotation_delta: np.ndarray) -> bool:
        if object_id in self.grabbable_objects:
            obj = self.grabbable_objects[object_id]
            if obj.is_grabbed:
                obj.rotation_4d += rotation_delta
                return True
        return False
    
    def scale_grabbed_object(self, object_id: str, scale_factor: float) -> bool:
        if object_id in self.grabbable_objects:
            obj = self.grabbable_objects[object_id]
            if obj. is_grabbed:
                obj. scale *= np.clip(scale_factor, 0.1, 10.0)
                return True
        return False
    
    def detect_gesture(self, hand_tracking_data: List[np.ndarray]) -> str:
        
        if len(hand_tracking_data) < 10:
            return 'unknown'
        
        recent_positions = np.array(hand_tracking_data[-10:])
        
        velocity = np.linalg.norm(np.diff(recent_positions, axis=0), axis=1).mean()
        
        if velocity > 2.0:
            return 'fast_movement'
        elif velocity > 0.5:
            return 'moderate_movement'
        elif velocity < 0.1:
            return 'pinch'
        
        return 'idle'
    
    def record_gesture(self, hand:  str, position: np.ndarray):
        self.gesture_history. append({
            'hand': hand,
            'position': position. copy(),
            'timestamp': len(self.gesture_history)
        })
        
        if len(self.gesture_history) > 1000:
            self.gesture_history = self.gesture_history[-500:]
    
    def get_object_interaction_suggestions(self, object_id: str) -> List[str]:
        
        suggestions = [
            'Rotate in XY plane',
            'Rotate in XW plane (4D! )',
            'Scale uniformly',
            'Move in 4D space',
            'Apply force',
            'Examine from different angle'
        ]
        
        return suggestions


class AILearningAssistant:
    
    def __init__(self):
        self.user_interactions = []
        self.learning_progress = {
            'basic_concepts': 0,
            'rotation_understanding': 0,
            'projection_understanding': 0,
            'physics_understanding': 0
        }
        self.suggestions = []
        self.difficulty_level = 'beginner'
    
    def record_user_action(self, action: str, object_id: str, success: bool):
        self.user_interactions.append({
            'action': action,
            'object_id': object_id,
            'success': success,
            'timestamp': len(self.user_interactions)
        })
    
    def analyze_user_behavior(self) -> Dict[str, float]: 
        
        if not self.user_interactions:
            return {}
        
        recent_actions = self.user_interactions[-50:]
        successful_actions = sum(1 for a in recent_actions if a['success'])
        success_rate = successful_actions / len(recent_actions) if recent_actions else 0
        
        action_counts = {}
        for action in recent_actions:
            action_counts[action['action']] = action_counts.get(action['action'], 0) + 1
        
        return {
            'success_rate': success_rate,
            'most_used_action': max(action_counts, key=action_counts.get) if action_counts else 'none',
            'total_actions': len(self.user_interactions)
        }
    
    def generate_recommendations(self) -> List[str]:
        
        analysis = self.analyze_user_behavior()
        recommendations = []
        
        success_rate = analysis. get('success_rate', 0)
        
        if success_rate > 0.8:
            recommendations.append('🎓 You\'re doing great! Try rotating in the XW plane (4D rotation).')
            recommendations.append('🚀 Next: Learn about Minkowski spacetime!')
            self.difficulty_level = 'intermediate'
        elif success_rate > 0.5:
            recommendations.append('📚 Keep practicing! Remember: XW plane is perpendicular to 3D space.')
            recommendations.append('💡 Tip: Use stereographic projection to see 4D objects more clearly.')
        else:
            recommendations.append('🤔 Let\'s start with the basics! Try rotating in just one plane.')
            recommendations.append('📖 Review:  What does the W dimension represent? ')
            self.difficulty_level = 'beginner'
        
        return recommendations
    
    def adaptive_difficulty_adjustment(self):
        
        analysis = self.analyze_user_behavior()
        success_rate = analysis.get('success_rate', 0)
        total_actions = analysis.get('total_actions', 0)
        
        if success_rate > 0.85 and total_actions > 30:
            self.difficulty_level = 'advanced'
        elif success_rate > 0.7 and total_actions > 20:
            self.difficulty_level = 'intermediate'
        else:
            self.difficulty_level = 'beginner'
    
    def generate_personalized_lesson(self) -> Dict[str, str]:
        
        if self.difficulty_level == 'beginner':
            return {
                'title': 'Understanding 4D Coordinates',
                'content': 'A 4D point is (x, y, z, w) where w is perpendicular to all 3D axes.',
                'exercise': 'Try moving an object along the W axis only.',
                'estimated_duration': '5 minutes'
            }
        elif self.difficulty_level == 'intermediate':
            return {
                'title': '4D Rotations and Planes',
                'content': 'In 4D, there are 6 rotation planes:  XY, XZ, XW, YZ, YW, ZW.',
                'exercise': 'Rotate a tesseract in the XW plane and observe the projection changes.',
                'estimated_duration':  '10 minutes'
            }
        else:
            return {
                'title': 'Relativity and Spacetime',
                'content':  'Minkowski spacetime:  (-ct)² + x² + y² + z² = interval',
                'exercise': 'Simulate a particle moving through spacetime with relativistic effects.',
                'estimated_duration':  '20 minutes'
            }