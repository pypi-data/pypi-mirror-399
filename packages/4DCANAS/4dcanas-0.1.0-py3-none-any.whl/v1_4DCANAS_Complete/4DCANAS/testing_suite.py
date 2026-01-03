import unittest
import numpy as np

class Test4DCoreGeometry(unittest.TestCase):
    def setUp(self):
        from . core import Point4D, Vector4D, Tesseract, Rotation4D
        self.Point4D = Point4D
        self.Vector4D = Vector4D
        self.Tesseract = Tesseract
        self.Rotation4D = Rotation4D
    
    def test_point4d_creation(self):
        p = self.Point4D(1. 0, 2.0, 3.0, 4.0)
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p. y, 2.0)
        self.assertEqual(p.z, 3.0)
        self.assertEqual(p.w, 4.0)
    
    def test_point4d_distance(self):
        p1 = self.Point4D(0, 0, 0, 0)
        p2 = self.Point4D(3, 4, 0, 0)
        distance = p1.distance_to(p2)
        self.assertAlmostEqual(distance, 5.0, places=5)
    
    def test_vector4d_magnitude(self):
        v = self.Vector4D(1, 1, 1, 1)
        magnitude = v.magnitude()
        expected = np.sqrt(4)
        self.assertAlmostEqual(magnitude, expected, places=5)
    
    def test_tesseract_vertices(self):
        t = self.Tesseract(size=1.0)
        self.assertEqual(len(t.vertices), 16)
    
    def test_tesseract_edges(self):
        t = self.Tesseract(size=1.0)
        self.assertEqual(len(t. edges), 32)

class Test4DAnalysis(unittest.TestCase):
    def setUp(self):
        from .deep_analysis import DeepAnalyzer4D
        from .core import Tesseract
        self.DeepAnalyzer4D = DeepAnalyzer4D
        self.Tesseract = Tesseract
    
    def test_shape_analysis(self):
        analyzer = self.DeepAnalyzer4D()
        t = self.Tesseract(size=1.0)
        vertices = np.array([v.coords for v in t.vertices])
        
        analysis = analyzer.analyze_shape(vertices, t.edges)
        
        self.assertIn('geometric_properties', analysis)
        self.assertIn('topological_properties', analysis)
        self.assertIn('aesthetic_score', analysis)

def run_all_tests(verbosity=2):
    loader = unittest. TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(Test4DCoreGeometry))
    suite.addTests(loader.loadTestsFromTestCase(Test4DAnalysis))
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)

if __name__ == '__main__':
    run_all_tests()