from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="4DCANAS",
    version="1.0.0",
    author="MERO",
    author_email="mero@ps.com",
    description="Advanced 4D Visualization and Simulation Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/6x-u/4DCANAS",
    project_urls={
        "Bug Tracker": "https://github.com/6x-u/4DCANAS/issues",
        "Documentation": "https://github.com/6x-u/4DCANAS/wiki",
        "Telegram": "https://t.me/QP4RM",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language ::  Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic ::  Multimedia :: Graphics ::  3D Graphics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "PyOpenGL>=3.1.5",
        "PyQt5>=5.15.0",
        "pillow>=8.3.0",
        "torch>=1.9.0",
        "tensorflow>=2.6.0",
        "scikit-learn>=0.24.0",
        "psutil>=5.8.0",
        "sympy>=1.9",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "viz": [
            "pythreejs>=2.3.0",
            "jupyter>=1.0.0",
            "ipywidgets>=7.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "4dcanas=4DCANAS.cli:main",
        ],
    },
)