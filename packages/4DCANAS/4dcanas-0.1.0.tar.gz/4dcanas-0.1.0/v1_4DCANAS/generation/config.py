from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class GenerationConfig:
    """Configuration for shape generation"""
    num_vertices: int = 16
    symmetry_level: str = "high"
    aesthetic_score_target: float = 0.8
    physical_properties:  Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.physical_properties is None:
            self.physical_properties = {}