import unittest
import numpy as np
from 4DCANAS import (
    Point4D, Vector4D, Rotation4D, Tesseract,
    AdvancedMath4D, Physics4DEngine, AdvancedVisualizer4D,
    MEROGeometricAlgorithms, EducationalMode
)

class Test4DCanas(unittest.TestCase):
    
    def test_point4d_creation(self):
        p = Point4D(1, 2, 3, 4)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)
        self.assertEqual(p.z, 3)
        self.assertEqual(p.w, 4)
    
    def test_point4d_distance(self):
        p1 = Point4D(0, 0, 0, 0)
        p2 = Point4D(3, 4, 0, 0)
        distance = p1.distance_to(p2)
        self.assertAlmostEqual(distance, 5.0)
    
    def test_vector4d_magnitude(self):
        v = Vector4D(1, 1, 1, 1)
        magnitude = v.magnitude()
        self.assertAlmostEqual(magnitude, 2.0, places=5)
    
    def test_advanced_math_4d_distance(self):
        p1 = np.array([0, 0, 0, 0])
        p2 = np.array([1, 1, 1, 1])
        distance = AdvancedMath4D.calculate_4d_distance(p1, p2)
        self.assertAlmostEqual(distance, 2.0, places=5)
    
    def test_advanced_math_4d_angle(self):
        v1 = np.array([1, 0, 0, 0])
        v2 = np.array([0, 1, 0, 0])
        angle = AdvancedMath4D.calculate_4d_angle(v1, v2)
        self.assertAlmostEqual(angle, np.pi / 2, places=5)
    
    def test_tesseract_creation(self):
        t = Tesseract(size=1.0)
        self.assertEqual(len(t.vertices), 16)
        self.assertEqual(len(t.edges), 32)
    
    def test_physics_4d_particle_addition(self):
        physics = Physics4DEngine()
        physics.add_particle(
            np.array([0, 0, 0, 0]),
            np.array([1, 0, 0, 0]),
            mass=1.0
        )
        self.assertEqual(len(physics.particles), 1)
    
    def test_mero_hypersphere_sampling(self):
        points = MEROGeometricAlgorithms.hypersphere_sampling_4d(100, radius=1.0)
        self.assertEqual(points.shape, (100, 4))
        
        distances = np.linalg.norm(points, axis=1)
        self.assertTrue(np.all(distances <= 1.01))
    
    def test_educational_mode_lessons(self):
        edu = EducationalMode('beginner')
        lessons = edu.lessons['beginner']
        self.assertGreater(len(lessons), 0)
    
    def test_educational_mode_quiz(self):
        edu = EducationalMode('beginner')
        quiz = edu.get_interactive_quiz('4D Basics:  Understanding the Fourth Dimension')
        self.assertGreater(len(quiz), 0)

if __name__ == '__main__':
    unittest.main()