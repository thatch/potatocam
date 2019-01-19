import unittest

from potatocam.polyline import Polyline, Segment


class PolylineTest(unittest.TestCase):
    def test_repr(self):
        p = Polyline()
        p.add_segment(Segment((1, 0)))
        p.add_segment(Segment((1, 1)))
        p.add_segment(Segment((0, 0)))
        self.assertEqual(
            "Polyline(segments=[S((1, 0)), S((1, 1)), S((0, 0))])", repr(p)
        )

    def test_normals(self):
        p = Polyline()
        p.add_segment(Segment((10, 0)))
        p.add_segment(Segment((0, 0)))
        # This presumes CCW ordering has normals outside
        expected = (0.0, -1.0, 0.0, -1.0)
        actual = sum(p._normals(0), ())
        print(expected, actual)
        for i, j in zip(expected, actual):
            self.assertAlmostEqual(i, j)

    def test_curve_normals(self):
        p = Polyline()
        p.add_segment(Segment((0, 0)))
        p.add_segment(Segment((10, 0), curve=45))
        # This presumes CCW ordering has normals outside
        expected = (-0.38268343, -0.923879537, 0.38268343, -0.92387953)
        actual = sum(p._normals(1), ())
        print(expected, actual)
        for i, j in zip(expected, actual):
            self.assertAlmostEqual(i, j)

        p = Polyline()
        p.add_segment(Segment((0, 0)))
        p.add_segment(Segment((10, 0), curve=-45))
        expected = (0.38268343, -0.923879537, -0.38268343, -0.92387953)
        actual = sum(p._normals(1), ())
        print(expected, actual)
        for i, j in zip(expected, actual):
            self.assertAlmostEqual(i, j)

    def test_offset(self):
        p = Polyline()
        p.add_segment(Segment((0, 0)))
        p.add_segment(Segment((10, 0)))
        p.add_segment(Segment((10, 10)))
        p.add_segment(Segment((0, 10)))

        n = p.offset(1.5)
        n.roll()
        # This can change ordering, primarily by inserting arcs.
        self.assertEqual((-1.5, -1.5), n.segments[0].pt)
        self.assertEqual((-1.5, -1.5), n.segments[0].pt)
