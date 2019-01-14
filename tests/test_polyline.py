import unittest

from potatocam import polyline

class PolylineTest(unittest.TestCase):
    def test_repr(self):
        p = polyline.Polyline()
        p.add_segment((0, 0), (1, 0))
        p.add_segment((1, 0), (1, 1))
        p.add_segment((1, 1), (0, 0))
        self.assertEqual(
            "Polyline(lines=[((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), "
            "(0, 0))], curves=[0, 0, 0])", repr(p))

    def test_normals(self):
        p = polyline.Polyline()
        p.add_segment((0, 0), (10, 0), 0)
        # This presumes CCW ordering has normals outside
        expected = (0.0, -1.0, 0.0, -1.0)
        actual = sum(p._normals(0), ())
        print(expected, actual)
        for i, j in zip(expected, actual):
            self.assertAlmostEqual(i, j)

    def test_curve_normals(self):
        p = polyline.Polyline()
        p.add_segment((0, 0), (10, 0), 45)
        # This presumes CCW ordering has normals outside
        expected = (-0.38268343, -0.923879537, 0.38268343, -0.92387953)
        actual = sum(p._normals(0), ())
        print(expected, actual)
        for i, j in zip(expected, actual):
            self.assertAlmostEqual(i, j)

        p.curves[0] *= -1
        expected = (0.38268343, -0.923879537, -0.38268343, -0.92387953)
        actual = sum(p._normals(0), ())
        print(expected, actual)
        for i, j in zip(expected, actual):
            self.assertAlmostEqual(i, j)
