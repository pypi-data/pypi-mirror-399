import sys
from .  import print_banner
from .core.geometry import Point4D
from .generation.auto_generator import AutoGenerator4D
from .analysis.analyzer import DeepAnalyzer4D
import numpy as np

def main():
    print_banner()
    
    print("\n[1] Testing Core Geometry...")
    p1 = Point4D(1, 2, 3, 4)
    p2 = Point4D(5, 6, 7, 8)
    distance = p1.distance_to(p2)
    print(f"✓ Point4D:  {p1}")
    print(f"✓ Distance: {distance:. 3f}")
    
    print("\n[2] Testing AutoGenerator...")
    gen = AutoGenerator4D()
    shape = gen.generate_shape("tesseract", seed=42)
    print(f"✓ Generated:  {shape['type']}")
    print(f"✓ Vertices: {len(shape['vertices'])}")
    print(f"✓ Edges: {len(shape['edges'])}")
    
    print("\n[3] Testing DeepAnalyzer...")
    analyzer = DeepAnalyzer4D()
    analysis = analyzer.analyze_shape(np.array(shape['vertices']), shape['edges'])
    print(f"✓ Aesthetic Score: {analysis['aesthetic_score']:.3f}")
    print(f"✓ Symmetry:  {analysis['symmetry_analysis']['overall_symmetry']:.3f}")
    
    print("\n✓ All systems operational!")
    print("✓ 4DCANAS is ready to use!\n")

if __name__ == "__main__":
    main()