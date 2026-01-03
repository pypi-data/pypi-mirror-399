from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="4DCANAS",
    version="1.0.0",
    author="MERO",
    author_email="mero@ps.com",
    description="Advanced 4D Visualization and Simulation Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/6x-u/4DCANAS",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8+",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
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
        "ipywidgets>=7.6.0",
    ],
)