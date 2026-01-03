from 4DCANAS import HyperInteractive4D, AutoGenerator4D, DeepAnalyzer4D, AdvancedExportTools
import numpy as np

print("4DCANAS v1.0.0 - Quick Start Example\n")

hi = HyperInteractive4D()
gen = AutoGenerator4D()
analyzer = DeepAnalyzer4D()
exporter = AdvancedExportTools()

@hi.shape('tesseract', size=1.0)
@hi.rotate([0.1, 0.2, 0.15, 0.05])
def create_shape(shape):
    return shape

print("Creating tesseract shape...")
shape = create_shape()

print("Generating AI shape...")
ai_shape = gen.generate_shape("complex rotating polytope", seed=42)

print("Analyzing shape...")
analysis = analyzer.analyze_shape(np.array(ai_shape['vertices']), ai_shape['edges'])

print(f"Aesthetic Score: {analysis['aesthetic_score']:.3f}")
print(f"Symmetry:  {analysis['symmetry_analysis']['overall_symmetry']:.3f}")
print(f"Stability: {analysis['stability_analysis']['stability_score']:.3f}")

print("\nExporting shape...")
exporter.quick_export(ai_shape, format='obj', filename='tesseract_output.obj')
exporter.quick_export(ai_shape, format='json', filename='tesseract_output.json')

print("Done!  4DCANAS is working perfectly!")