import unittest

from potatocam.features import *


class FeatureExtractorTest(unittest.TestCase):
    def test_cube(self):
        m = load_mesh("tests/stl/cube.stl")
        fe = FeatureExtractor(m)
        self.assertEqual(0, len(fe.features))

        fe.extract()

        self.assertEqual(2, len(fe.features))

        fe.features.sort(key=lambda f: f.height)

        # bottom face
        self.assertEqual(0.0, fe.features[0].height)
        fe.features[0].roll()
        self.assertEqual(
            [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0)], fe.features[0].outline
        )
        self.assertEqual([FoldDirection.UP] * 4, fe.features[0].fold_directions)
        self.assertEqual(PolygonOrientation.OUTSIDE, fe.features[0].direction)
        self.assertEqual(SpecialFeatureType.BOT, fe.features[0].flags)

        # top face
        self.assertEqual(10.0, fe.features[1].height)
        fe.features[1].roll()
        self.assertEqual(
            [(0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0)], fe.features[1].outline
        )
        self.assertEqual([FoldDirection.DOWN] * 4, fe.features[1].fold_directions)
        self.assertEqual(PolygonOrientation.INSIDE, fe.features[1].direction)
        self.assertEqual(SpecialFeatureType.TOP, fe.features[1].flags)

    test_cube.simple = True

    def test_step_cube(self):
        m = load_mesh("tests/stl/step_cube.stl")
        fe = FeatureExtractor(m)
        self.assertEqual(0, len(fe.features))

        fe.extract()

        self.assertEqual(3, len(fe.features))

        fe.features.sort(key=lambda f: f.height)

        # bottom face
        self.assertEqual(0.0, fe.features[0].height)
        fe.features[0].roll()
        self.assertEqual(
            [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)], fe.features[0].outline
        )
        self.assertEqual([FoldDirection.UP] * 4, fe.features[0].fold_directions)
        self.assertEqual(PolygonOrientation.OUTSIDE, fe.features[0].direction)
        self.assertEqual(SpecialFeatureType.BOT, fe.features[0].flags)

        # half shelf
        self.assertEqual(4.0, fe.features[1].height)
        fe.features[1].roll()
        self.assertEqual(
            [(0.0, 0.0), (0.0, 5.0), (5.0, 5.0), (5.0, 0.0)], fe.features[1].outline
        )
        print(fe.features[1].fold_directions)

        self.assertEqual(
            [
                FoldDirection.DOWN,
                FoldDirection.UP,
                FoldDirection.UP,
                FoldDirection.DOWN,
            ],
            fe.features[1].fold_directions,
        )

        self.assertEqual(PolygonOrientation.INSIDE, fe.features[1].direction)
        self.assertEqual(SpecialFeatureType.NORMAL, fe.features[1].flags)

        # top face
        self.assertEqual(10.0, fe.features[2].height)
        fe.features[2].roll()
        self.assertEqual(
            [
                (0.0, 5.0),
                (0.0, 10.0),
                (10.0, 10.0),
                (10.0, 0.0),
                (5.0, 0.0),
                (5.0, 5.0),
            ],
            fe.features[2].outline,
        )
        self.assertEqual([FoldDirection.DOWN] * 6, fe.features[2].fold_directions)
        self.assertEqual(PolygonOrientation.INSIDE, fe.features[2].direction)
        self.assertEqual(SpecialFeatureType.TOP, fe.features[2].flags)

    test_step_cube.simple = True

    def test_stone_wheel(self):
        m = load_mesh("tests/stl/stone_wheel.stl")
        fe = FeatureExtractor(m)
        self.assertEqual(0, len(fe.features))

        fe.extract()

        # top and bottom
        self.assertEqual(2, len(fe.features))
        self.assertEqual(1, len(fe.features[0].holes))
        self.assertNotEqual(fe.features[0].direction, fe.features[0].holes[0].direction)

    def test_circles(self):
        m = load_mesh("tests/stl/circles.stl")
        fe = FeatureExtractor(m)
        self.assertEqual(0, len(fe.features))

        fe.extract()
        for f in fe.features:
            print(f.flags, repr(f)[:100])

        # top and bottom
        self.assertEqual(2, len(fe.features))
        self.assertEqual(37, len(fe.features[0].holes))

        self.assertNotEqual(fe.features[0].direction, fe.features[0].holes[0].direction)
