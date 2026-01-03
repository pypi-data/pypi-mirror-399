import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent. parent
PACKAGE_ROOT = Path(__file__).parent

DEFAULT_CONFIG = {
    "gpu_enabled": True,
    "default_precision": "float64",
    "cache_enabled": True,
    "visualization_quality": "high",
    "export_format": "obj",
    "verbosity": 1,
}

PATHS = {
    "root": PROJECT_ROOT,
    "package": PACKAGE_ROOT,
    "tests": PROJECT_ROOT / "tests",
    "examples": PROJECT_ROOT / "examples",
    "docs": PROJECT_ROOT / "docs",
    "assets": PROJECT_ROOT / "assets",
}

ENVIRONMENT = os.getenv("4DCANAS_ENV", "production")

DEBUG = ENVIRONMENT == "development"
TESTING = ENVIRONMENT == "testing"
PRODUCTION = ENVIRONMENT == "production"