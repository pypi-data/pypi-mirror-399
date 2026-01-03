__version__ = "0.2.0"
__author__ = "MERO"
__email__ = "contact@4dcanas.dev"
__telegram__ = "https://t.me/QP4RM"

from .core import Point4D, Vector4D, Rotation4D, Tesseract
from .advanced_math import AdvancedMath4D, TensorMath4D, SymbolicMath4D
from . physics_4d import Physics4DEngine, RelativityEngine4D, QuantumMechanics4D, Particle4D
from .advanced_visualization import AdvancedVisualizer4D, ProjectionEngine, InteractiveVisualizer4D
from .ai_engine import PredictiveAI4D, TimeWarpVisualizer, PatternRecognition4D
from .mero_algorithms import MEROGeometricAlgorithms, MEROOptimizationEngine, MEROFluidDynamics4D, MERONeuralField
from .export_advanced import AdvancedExporter
from .plugin_system import PluginSystem
from .educational_mode import EducationalMode

try:
    from .advanced_gui import AdvancedApplication4D, launch_advanced_gui
except ImportError:
    AdvancedApplication4D = None
    launch_advanced_gui = None

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
]