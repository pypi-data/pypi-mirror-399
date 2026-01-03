#!/usr/bin/env python3
"""
4DCANAS v1.0.0 - Quick Start Example
Developer: MERO (mero@ps.com)
"""

from 4DCANAS import (
    HyperInteractive4D,
    AutoGenerator4D,
    DeepAnalyzer4D,
    AdvancedExportTools,
    TimeManipulation4D,
    ShapeMorphing4D,
    profile_function,
    profiler,
)
import numpy as np

def main():
    print("\n" + "="*80)
    print("4DCANAS v1.0.0 - Quick Start Demo")
    print("="*80 + "\n")
    
    hi = HyperInteractive4D()
    gen = AutoGenerator4D()
    analyzer = DeepAnalyzer4D()
    exporter = AdvancedExportTools()
    
    @hi.shape('tesseract', size=1.0)
    @hi.rotate([0.1, 0.2, 0.15, 0.05])
    def create_shape(shape):
        return shape
    
    print("[1] Creating Tesseract Shape...")
    shape = create_shape()
    print(f"✓ Tesseract created with {len(shape. vertices)} vertices")
    print(f"✓ Edges: {len(shape.edges)}")
    
    print("\n[2] Generating AI Shape...")
    ai_shape = gen.generate_shape("complex rotating polytope", seed=42)
    print(f"✓ Generated:  {ai_shape['type']}")
    print(f"✓ Vertices: {len(ai_shape['vertices'])}")
    
    print("\n[3] Analyzing Shape...")
    analysis = analyzer.analyze_shape(
        np.array(ai_shape['vertices']),
        ai_shape. get('edges', [])
    )
    print(f"✓ Aesthetic Score: {analysis['aesthetic_score']:.3f}")
    print(f"✓ Symmetry:  {analysis['symmetry_analysis']['overall_symmetry']:.3f}")
    print(f"✓ Stability: {analysis['stability_analysis']['stability_score']:.3f}")
    
    print("\n[4] Morphing Shapes...")
    morpher = ShapeMorphing4D(use_gpu=False)
    morphed = morpher.morph(
        np.array(ai_shape['vertices']),
        np.random.randn(len(ai_shape['vertices']), 4),
        num_frames=10
    )
    print(f"✓ Generated {len(morphed)} morphing frames")
    
    print("\n[5] Exporting Shapes...")
    exporter.quick_export(ai_shape, format='obj', filename='tesseract_output.obj')
    exporter.quick_export(ai_shape, format='json', filename='tesseract_output.json')
    print("✓ Exported to OBJ and JSON formats")
    
    print("\n[6] Time Manipulation...")
    time_sys = TimeManipulation4D()
    timeline = time_sys.evolve_shape(
        np.array(ai_shape['vertices']),
        lambda v, t: v * np.cos(t),
        time_steps=50
    )
    print(f"✓ Generated timeline with {len(timeline)} frames")
    
    print("\n" + "="*80)
    print("✓ 4DCANAS is working perfectly!")
    print("✓ All systems operational")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()