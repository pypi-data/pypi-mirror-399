"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     4DCANAS - Advanced 4D Visualization Suite               ║
║                              Version 1.0.0                                  ║
║                                                                              ║
║  Developer:  MERO                                                             ║
║  Telegram: @QP4RM                                                            ║
║  Email: contact@4dcanas.dev                                                 ║
║  GitHub: https://github.com/6x-u/4DCANAS                                    ║
║                                                                              ║
║  © 2025 MERO. All rights reserved.                                          ║
║  Licensed under MIT License                                                 ║
║                                                                              ║
║  Advanced 4D Mathematics | Physics Simulation | AI Integration              ║
║  VR/AR Support | Real-time Visualization | Professional Export              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

__version__ = "1.0.0"
__author__ = "MERO"
__email__ = "contact@4dcanas.dev"
__telegram__ = "https://t.me/QP4RM"
__github__ = "https://github.com/6x-u/4DCANAS"
__copyright__ = "© 2025 MERO. All rights reserved."
__license__ = "MIT"

from .core import Point4D, Vector4D, Rotation4D, Tesseract
from .advanced_math import AdvancedMath4D, TensorMath4D, SymbolicMath4D
from . physics_4d import Physics4DEngine, RelativityEngine4D, QuantumMechanics4D, Particle4D
from .advanced_visualization import AdvancedVisualizer4D, ProjectionEngine, InteractiveVisualizer4D
from .ai_engine import PredictiveAI4D, TimeWarpVisualizer, PatternRecognition4D
from .mero_algorithms import MEROGeometricAlgorithms, MEROOptimizationEngine, MEROFluidDynamics4D, MERONeuralField
from .export_advanced import AdvancedExporter
from .plugin_system import PluginSystem
from .educational_mode import EducationalMode
from . hyperinteractive import HyperInteractive4D
from .autogenerate import AutoGenerator4D, GenerationConfig
from .deep_analysis import DeepAnalyzer4D
from .advanced_export_tools import AdvancedExportTools
from .time_manipulation import TimeManipulation4D
from .vr_ar_engine import VRTrackingSystem, AROverlaySystem, Advanced4DPhysicsEngine
from .vr_interaction import VRInteractionManager, AILearningAssistant, GrabbableObject4D
from .vr_rendering import VRRenderingEngine, ARRenderingEngine, TelepresenceEngine4D

try:
    from .advanced_gui import AdvancedApplication4D, launch_advanced_gui
    from .vr_integration import VRApplication, launch_vr_application
except ImportError:
    AdvancedApplication4D = None
    launch_advanced_gui = None
    VRApplication = None
    launch_vr_application = None

__all__ = [
    'Point4D',
    'Vector4D',
    'Rotation4D',
    'Tesseract',
    'AdvancedMath4D',
    'TensorMath4D',
    'SymbolicMath4D',
    'Physics4DEngine',
    'RelativityEngine4D',
    'QuantumMechanics4D',
    'Particle4D',
    'AdvancedVisualizer4D',
    'ProjectionEngine',
    'InteractiveVisualizer4D',
    'PredictiveAI4D',
    'TimeWarpVisualizer',
    'PatternRecognition4D',
    'MEROGeometricAlgorithms',
    'MEROOptimizationEngine',
    'MEROFluidDynamics4D',
    'MERONeuralField',
    'AdvancedExporter',
    'PluginSystem',
    'EducationalMode',
    'AdvancedApplication4D',
    'launch_advanced_gui',
    'HyperInteractive4D',
    'AutoGenerator4D',
    'GenerationConfig',
    'DeepAnalyzer4D',
    'AdvancedExportTools',
    'TimeManipulation4D',
    'VRTrackingSystem',
    'AROverlaySystem',
    'Advanced4DPhysicsEngine',
    'VRInteractionManager',
    'AILearningAssistant',
    'GrabbableObject4D',
    'VRRenderingEngine',
    'ARRenderingEngine',
    'TelepresenceEngine4D',
    'VRApplication',
    'launch_vr_application',
]

def get_version():
    return __version__

def get_developer_info():
    return {
        'name': __author__,
        'email':  __email__,
        'telegram': __telegram__,
        'github': __github__,
        'copyright': __copyright__
    }

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                     🎨 4DCANAS v1.0.0 - Loaded Successfully                 ║
    ║                                                                              ║
    ║  Advanced 4D Visualization Suite with AI Integration                        ║
    ║                                                                              ║
    ║  Developer: MERO (@QP4RM)                                                   ║
    ║  License: MIT | GitHub: 6x-u/4DCANAS                                        ║
    ║                                                                              ║
    ║  Features:                                                                  ║
    ║  ✓ Advanced 4D Mathematics & Physics                                        ║
    ║  ✓ AI-Powered Shape Generation & Analysis                                  ║
    ║  ✓ VR/AR Integration with Hand Tracking                                     ║
    ║  ✓ Professional Export (Unity, Unreal, Blender)                             ║
    ║  ✓ Educational Mode with Interactive Lessons                               ║
    ║  ✓ Real-time 3D/4D Visualization                                            ║
    ║                                                                              ║
    ║  Quick Start:                                                               ║
    ║  >>> from 4DCANAS import *                                                 ║
    ║  >>> hi = HyperInteractive4D()                                              ║
    ║  >>> gen = AutoGenerator4D()                                                ║
    ║  >>> shape = gen.generate_shape("tesseract", seed=42)                       ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)