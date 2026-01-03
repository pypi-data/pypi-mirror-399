"""
معايير الاختبار الشاملة لمكتبة 4DCANAS
Comprehensive Testing Framework for 4DCANAS Library

الإصدار:  1.0.0
Version: 1.0.0

المطور:  MERO
Developer: MERO

البريد الإلكتروني: contact@4dcanas.dev
Email: contact@4dcanas.dev

تليجرام: @QP4RM
Telegram: @QP4RM

جميع الحقوق محفوظة © 2025 MERO
All Rights Reserved © 2025 MERO
"""

import unittest
import numpy as np
import torch
from typing import Dict, List, Tuple, Optional, Any
import time
import sys

class Test4DCoreGeometry(unittest.TestCase):
    
    def setUp(self):
        from 4DCANAS import Point4D, Vector4D, Tesseract, Rotation4D
        self.Point4D = Point4D
        self.Vector4D = Vector4D
        self.Tesseract = Tesseract
        self.Rotation4D = Rotation4D
    
    def test_point4d_creation_and_properties(self):
        p = self.Point4D(1. 0, 2.0, 3.0, 4.0)
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p. y, 2.0)
        self.assertEqual(p. z, 3.0)
        self.assertEqual(p.w, 4.0)
    
    def test_point4d_distance_calculation(self):
        p1 = self.Point4D(0, 0, 0, 0)
        p2 = self.Point4D(3, 4, 0, 0)
        distance = p1.distance_to(p2)
        self.assertAlmostEqual(distance, 5.0, places=5)
    
    def test_point4d_arithmetic_operations(self):
        p1 = self.Point4D(1, 2, 3, 4)
        p2 = self.Point4D(1, 2, 3, 4)
        p3 = p1 + p2
        self.assertAlmostEqual(p3.x, 2.0)
        self.assertAlmostEqual(p3.y, 4.0)
    
    def test_vector4d_magnitude(self):
        v = self.Vector4D(1, 1, 1, 1)
        magnitude = v.magnitude()
        expected = np.sqrt(4)
        self.assertAlmostEqual(magnitude, expected, places=5)
    
    def test_vector4d_normalization(self):
        v = self.Vector4D(3, 4, 0, 0)
        normalized = v.normalize()
        magnitude = normalized.magnitude()
        self.assertAlmostEqual(magnitude, 1.0, places=5)
    
    def test_vector4d_dot_product(self):
        v1 = self.Vector4D(1, 0, 0, 0)
        v2 = self.Vector4D(0, 1, 0, 0)
        dot = v1.dot(v2)
        self.assertAlmostEqual(dot, 0.0, places=5)
    
    def test_rotation4d_application(self):
        p = self.Point4D(1, 0, 0, 0)
        angles = [np.pi/2, 0, 0, 0]
        rotation = self.Rotation4D(angles)
        rotated = rotation.apply(p)
        self.assertAlmostEqual(rotated.x, 1.0, places=4)
    
    def test_tesseract_vertex_count(self):
        t = self.Tesseract(size=1.0)
        self.assertEqual(len(t.vertices), 16)
    
    def test_tesseract_edge_count(self):
        t = self.Tesseract(size=1.0)
        self.assertEqual(len(t.edges), 32)
    
    def test_tesseract_3d_projection(self):
        t = self.Tesseract(size=1.0)
        projected, edges = t.get_3d_projection()
        self.assertEqual(len(projected), 16)


class Test4DPhysicsEngine(unittest.TestCase):
    
    def setUp(self):
        from 4DCANAS import Physics4DEngine
        self.Physics4DEngine = Physics4DEngine
    
    def test_physics_engine_initialization(self):
        engine = self.Physics4DEngine()
        self.assertIsNotNone(engine)
    
    def test_particle_addition(self):
        engine = self.Physics4DEngine()
        engine.add_particle(
            np.array([0, 0, 0, 0]),
            np.array([1, 0, 0, 0]),
            mass=1.0
        )
        self.assertEqual(len(engine.particles), 1)
    
    def test_gravitational_force_calculation(self):
        engine = self.Physics4DEngine()
        engine.add_particle(np.array([0, 0, 0, 0]), np.array([0, 0, 0, 0]), mass=1.0)
        engine.add_particle(np.array([1, 0, 0, 0]), np.array([0, 0, 0, 0]), mass=1.0)
        
        engine.apply_gravitational_force_4d()
        self.assertTrue(len(engine.particles[0]['acceleration']) == 4)
    
    def test_momentum_conservation(self):
        engine = self.Physics4DEngine()
        engine.add_particle(np. array([0, 0, 0, 0]), np.array([1, 1, 1, 1]), mass=1.0)
        engine.add_particle(np.array([1, 1, 1, 1]), np.array([-1, -1, -1, -1]), mass=1.0)
        
        initial_momentum = engine.get_total_momentum()
        
        for _ in range(10):
            engine.update(dt=0.01)
        
        final_momentum = engine.get_total_momentum()
        difference = np.linalg.norm(final_momentum - initial_momentum)
        self.assertLess(difference, 0.1)
    
    def test_energy_calculation(self):
        engine = self.Physics4DEngine()
        engine.add_particle(np. array([0, 0, 0, 0]), np.array([1, 0, 0, 0]), mass=2.0)
        
        energy = engine.get_total_kinetic_energy()
        expected_energy = 0.5 * 2.0 * 1.0
        self.assertAlmostEqual(energy, expected_energy, places=5)


class Test4DVisualization(unittest.TestCase):
    
    def setUp(self):
        from 4DCANAS import AdvancedVisualizer4D, Tesseract
        self.AdvancedVisualizer4D = AdvancedVisualizer4D
        self.Tesseract = Tesseract
    
    def test_visualizer_initialization(self):
        viz = self.AdvancedVisualizer4D()
        self.assertIsNotNone(viz)
    
    def test_projection_orthogonal(self):
        from 4DCANAS import ProjectionEngine
        proj_engine = ProjectionEngine()
        point_4d = np.array([1, 2, 3, 4])
        point_3d = proj_engine. orthogonal_projection_4d_to_3d(point_4d)
        self.assertEqual(len(point_3d), 3)
    
    def test_projection_perspective(self):
        from 4DCANAS import ProjectionEngine
        proj_engine = ProjectionEngine()
        point_4d = np.array([1, 2, 3, 4])
        point_3d = proj_engine.perspective_projection_4d_to_3d(point_4d)
        self.assertEqual(len(point_3d), 3)


class Test4DAnalysis(unittest.TestCase):
    
    def setUp(self):
        from 4DCANAS import DeepAnalyzer4D, Tesseract
        self. DeepAnalyzer4D = DeepAnalyzer4D
        self.Tesseract = Tesseract
    
    def test_shape_analysis(self):
        analyzer = self.DeepAnalyzer4D()
        t = self.Tesseract(size=1.0)
        vertices = np.array([v. coords for v in t.vertices])
        
        analysis = analyzer.analyze_shape(vertices, t. edges)
        
        self.assertIn('geometric_properties', analysis)
        self.assertIn('topological_properties', analysis)
        self.assertIn('symmetry_analysis', analysis)
        self.assertIn('stability_analysis', analysis)
        self.assertIn('aesthetic_score', analysis)
    
    def test_geometric_properties_analysis(self):
        analyzer = self.DeepAnalyzer4D()
        vertices = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        
        props = analyzer._analyze_geometric_properties(vertices)
        
        self.assertIn('perimeter_4d', props)
        self.assertIn('volume_estimate', props)
        self.assertIn('compactness', props)
    
    def test_symmetry_detection(self):
        analyzer = self.DeepAnalyzer4D()
        vertices = np.array([
            [1, 0, 0, 0],
            [-1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, -1, 0, 0]
        ])
        
        symmetry = analyzer._analyze_symmetry(vertices)
        
        self.assertGreater(symmetry['overall_symmetry'], 0.5)
    
    def test_stability_analysis(self):
        analyzer = self.DeepAnalyzer4D()
        vertices = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        stability = analyzer._analyze_stability(vertices)
        
        self.assertIn('stability_score', stability)
        self.assertIn('eigenvalues', stability)


class Test4DAutoGeneration(unittest.TestCase):
    
    def setUp(self):
        from 4DCANAS import AutoGenerator4D
        self.AutoGenerator4D = AutoGenerator4D
    
    def test_tesseract_generation(self):
        gen = self.AutoGenerator4D()
        shape = gen.generate_shape("tesseract")
        
        self.assertEqual(shape['type'], 'tesseract_variant')
        self.assertGreater(len(shape['vertices']), 0)
    
    def test_hypersphere_generation(self):
        gen = self.AutoGenerator4D()
        shape = gen.generate_shape("sphere")
        
        self.assertEqual(shape['type'], 'hypersphere_variant')
        self.assertGreater(len(shape['vertices']), 0)
    
    def test_torus_generation(self):
        gen = self.AutoGenerator4D()
        shape = gen.generate_shape("torus")
        
        self.assertEqual(shape['type'], '4d_torus')
        self.assertGreater(len(shape['vertices']), 0)
    
    def test_ai_shape_generation(self):
        gen = self.AutoGenerator4D()
        shape = gen.generate_shape("large random spiral")
        
        self.assertEqual(shape['type'], 'ai_generated')
        self.assertGreater(len(shape['vertices']), 0)
    
    def test_physics_ruleset_generation(self):
        gen = self.AutoGenerator4D()
        shape = gen.generate_shape("tesseract")
        
        physics_rules = gen.generate_physics_ruleset(shape, "rotating with gravity")
        
        self. assertGreater(len(physics_rules), 0)
    
    def test_motion_path_generation(self):
        gen = self.AutoGenerator4D()
        shape = gen.generate_shape("sphere")
        
        path = gen.generate_motion_path(shape, path_type="spiral", num_frames=100)
        
        self.assertEqual(len(path), 100)


class Test4DExport(unittest.TestCase):
    
    def setUp(self):
        from 4DCANAS import AdvancedExportTools, AutoGenerator4D
        self. AdvancedExportTools = AdvancedExportTools
        self.AutoGenerator4D = AutoGenerator4D
        self.gen = AutoGenerator4D()
    
    def test_obj_export(self):
        import os
        import tempfile
        
        shape = self.gen.generate_shape("tesseract")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test. obj")
            result = self. AdvancedExportTools.quick_export(shape, format='obj', filename=filename)
            
            self.assertTrue(os. path.exists(result))
    
    def test_json_export(self):
        import os
        import tempfile
        
        shape = self.gen. generate_shape("sphere")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test.json")
            result = self.AdvancedExportTools.quick_export(shape, format='json', filename=filename)
            
            self.assertTrue(os.path.exists(result))
    
    def test_gltf_export(self):
        import os
        import tempfile
        
        shape = self.gen.generate_shape("torus")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test.gltf")
            result = self.AdvancedExportTools.quick_export(shape, format='gltf', filename=filename)
            
            self.assertTrue(os. path.exists(result))


class Test4DTimeManipulation(unittest.TestCase):
    
    def setUp(self):
        from 4DCANAS import TimeManipulation4D
        self.TimeManipulation4D = TimeManipulation4D
    
    def test_time_scale_setting(self):
        time_sys = self.TimeManipulation4D()
        time_sys.set_time_scale(0.5)
        
        self.assertEqual(time_sys.time_scale, 0.5)
    
    def test_time_direction_forward(self):
        time_sys = self.TimeManipulation4D()
        time_sys.set_time_direction('forward')
        
        self. assertEqual(time_sys.time_direction, 1)
    
    def test_time_direction_backward(self):
        time_sys = self.TimeManipulation4D()
        time_sys.set_time_direction('backward')
        
        self.assertEqual(time_sys. time_direction, -1)
    
    def test_shape_evolution(self):
        time_sys = self.TimeManipulation4D()
        
        vertices = np.random.randn(16, 4)
        
        def evolution_func(v, t):
            return v + np.sin(t) * 0.01
        
        timeline = time_sys.evolve_shape(vertices, evolution_func, 100)
        
        self.assertEqual(len(timeline), 101)
    
    def test_relativistic_time_dilation(self):
        time_sys = self.TimeManipulation4D()
        
        vertices = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
        velocity = np.array([0.5e8, 0, 0, 0])
        
        dilated = time_sys.apply_relativistic_time_dilation(vertices, velocity)
        
        self.assertEqual(dilated.shape, vertices.shape)


class Test4DHyperInteractive(unittest.TestCase):
    
    def setUp(self):
        from 4DCANAS import HyperInteractive4D
        self.HyperInteractive4D = HyperInteractive4D
    
    def test_hyperinteractive_initialization(self):
        hi = self.HyperInteractive4D()
        self.assertIsNotNone(hi)
    
    def test_shape_decorator(self):
        hi = self.HyperInteractive4D()
        
        @hi. shape('tesseract', size=1.0, id='test')
        def test_func(shape):
            return shape
        
        result = test_func()
        self.assertIsNotNone(result)
    
    def test_rotate_decorator(self):
        hi = self.HyperInteractive4D()
        
        @hi. shape('tesseract')
        @hi.rotate([0.1, 0.2, 0.15, 0.05])
        def test_func(shape):
            return shape
        
        result = test_func()
        self.assertIsNotNone(result)
    
    def test_scale_decorator(self):
        hi = self.HyperInteractive4D()
        
        @hi.shape('tesseract')
        @hi.scale(2.0)
        def test_func(shape):
            return shape
        
        result = test_func()
        self.assertIsNotNone(result)


class TestPerformanceBenchmark(unittest.TestCase):
    
    def test_rotation_performance(self):
        from 4DCANAS import Tesseract
        
        t = Tesseract(size=1.0)
        
        start = time.time()
        for _ in range(1000):
            t.rotate([0.01, 0.01, 0.01, 0.01])
        end = time.time()
        
        elapsed = end - start
        self. assertLess(elapsed, 5.0)
    
    def test_distance_calculation_performance(self):
        from 4DCANAS import Point4D
        
        points = [Point4D(np.random.randn(), np.random.randn(), 
                         np.random.randn(), np.random.randn()) for _ in range(100)]
        
        start = time.time()
        for i, p1 in enumerate(points):
            for j, p2 in enumerate(points[i+1:]):
                _ = p1.distance_to(p2)
        end = time.time()
        
        elapsed = end - start
        self. assertLess(elapsed, 2.0)
    
    def test_analysis_performance(self):
        from 4DCANAS import DeepAnalyzer4D
        
        analyzer = DeepAnalyzer4D()
        vertices = np.random.randn(100, 4)
        
        start = time.time()
        analysis = analyzer.analyze_shape(vertices)
        end = time.time()
        
        elapsed = end - start
        self.assertLess(elapsed, 5.0)


class TestExportIntegrity(unittest.TestCase):
    
    def test_export_reimport_consistency(self):
        import os
        import tempfile
        import json
        
        from 4DCANAS import AutoGenerator4D, AdvancedExportTools
        
        gen = AutoGenerator4D()
        shape = gen.generate_shape("sphere", seed=42)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test.json")
            AdvancedExportTools.quick_export(shape, format='json', filename=filename)
            
            with open(filename, 'r') as f:
                imported = json.load(f)
            
            self.assertEqual(len(imported['vertices']), len(shape['vertices']))


class TestRobustness(unittest.TestCase):
    
    def test_empty_shape_handling(self):
        from 4DCANAS import DeepAnalyzer4D
        
        analyzer = DeepAnalyzer4D()
        
        with self.assertRaises((IndexError, ValueError)):
            analyzer. analyze_shape(np.array([]))
    
    def test_invalid_rotation_angles(self):
        from 4DCANAS import Rotation4D
        
        angles = [float('nan'), 0, 0, 0]
        
        with self.assertRaises((ValueError, TypeError)):
            Rotation4D(angles)
    
    def test_extreme_scale_values(self):
        from 4DCANAS import HyperInteractive4D
        
        hi = HyperInteractive4D()
        
        @hi.shape('tesseract')
        @hi.scale(0.0001)
        def test_func(shape):
            return shape
        
        result = test_func()
        self.assertIsNotNone(result)


def run_all_tests(verbosity=2):
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(Test4DCoreGeometry))
    suite.addTests(loader.loadTestsFromTestCase(Test4DPhysicsEngine))
    suite.addTests(loader.loadTestsFromTestCase(Test4DVisualization))
    suite.addTests(loader.loadTestsFromTestCase(Test4DAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(Test4DAutoGeneration))
    suite.addTests(loader.loadTestsFromTestCase(Test4DExport))
    suite.addTests(loader.loadTestsFromTestCase(Test4DTimeManipulation))
    suite.addTests(loader.loadTestsFromTestCase(Test4DHyperInteractive))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceBenchmark))
    suite.addTests(loader.loadTestsFromTestCase(TestExportIntegrity))
    suite.addTests(loader. loadTestsFromTestCase(TestRobustness))
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


if __name__ == '__main__': 
    run_all_tests()