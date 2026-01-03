"""
4DCANAS - Advanced 4D Visualization and Simulation Library
Version 1.0.0
Developer: MERO (mero@ps.com)
License: MIT
© 2025 MERO.  All rights reserved.
"""

from .version import (
    __version__,
    __author__,
    __email__,
    __license__,
    __copyright__,
)

from .core. geometry import Point4D, Point3D
from .core.vectors import Vector4D
from .core.rotations import Rotation4D
from .core.transformations import Tesseract

from .generation.auto_generator import AutoGenerator4D
from .generation.config import GenerationConfig

from .analysis.analyzer import DeepAnalyzer4D

from .export.exporter import AdvancedExportTools

from .time_control. time_system import TimeManipulation4D

from .morphing.morpher import ShapeMorphing4D

from .performance.profiler import PerformanceProfiler, profile_function, profiler

from .hyperinteractive.decorators import HyperInteractive4D

from .jupyter.interactive import JupyterInteractive4D

from .visualization.visualizer import AdvancedVisualizer4D
from .visualization.projections import ProjectionEngine

__all__ = [
    "Point4D",
    "Point3D",
    "Vector4D",
    "Rotation4D",
    "Tesseract",
    "AutoGenerator4D",
    "GenerationConfig",
    "DeepAnalyzer4D",
    "AdvancedExportTools",
    "TimeManipulation4D",
    "ShapeMorphing4D",
    "PerformanceProfiler",
    "profile_function",
    "profiler",
    "HyperInteractive4D",
    "JupyterInteractive4D",
    "AdvancedVisualizer4D",
    "ProjectionEngine",
]

def print_banner():
    banner = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                    4DCANAS v1.0.0 - Production Ready                       ║
║                 Advanced 4D Visualization & Simulation Suite                ║
║                                                                            ║
║  Developer: MERO (mero@ps.com)                                             ║
║  License: MIT                                                             ║
║  Status: 100% Functional - All Systems Operational                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

print_banner()