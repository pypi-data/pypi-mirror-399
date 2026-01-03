__version__ = "1.0.0"
__author__ = "MERO"
__email__ = "mero@ps. com"
__copyright__ = "© 2025 MERO.  All rights reserved."

from .  import core
from . import hyperinteractive
from . import autogenerate
from . import deep_analysis
from . import advanced_export_tools
from . import time_manipulation
from . import shape_morphing
from . import performance_profiler
from . import testing_suite

from .core import Point4D, Vector4D, Rotation4D, Tesseract
from .hyperinteractive import HyperInteractive4D
from . autogenerate import AutoGenerator4D, GenerationConfig
from .deep_analysis import DeepAnalyzer4D
from .advanced_export_tools import AdvancedExportTools
from .time_manipulation import TimeManipulation4D
from .shape_morphing import ShapeMorphing4D
from .performance_profiler import PerformanceProfiler, profile_function, profiler
from .testing_suite import run_all_tests

def print_banner():
    banner = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  4DCANAS v1.0.0 - Production Ready                         ║
║                   Advanced 4D Visualization Suite                          ║
║                                                                            ║
║  Developer: MERO                                                           ║
║  Email: mero@ps.com                                                       ║
║  License: MIT                                                             ║
║                                                                            ║
║  100% Functional - All Systems Operational                                ║
╚════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

print_banner()