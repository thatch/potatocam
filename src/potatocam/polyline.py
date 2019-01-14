"""
Represents a closed shape consisting of straight lines and circular rcs.

Each segment has an 'curve' parameter which is probably more similar to the
EAGLE representation of lines than it is autocad (which calls it bulge).  This
is the number of degrees, and is 0 for straight segments.
"""

import math

from ezdxf.algebra import bulge, vector

__all__ = ["Polyline"]

class Polyline:
    def __init__(self):
        # we duplicate the points to make the calculation that much easier.
        self.lines = []
        self.curves = []

    def add_segment(self, p1, p2, curve=0):
        if self.lines:
            if self.lines[-1][-1] != p1:
                raise ValueError("Non-connected line")
        self.lines.append((p1, p2))
        self.curves.append(curve)

    def is_closed(self):
        return self.lines[0][0] == self.lines[-1][1]

    def offset_custom(self, values):
        """
        Args:
          values: The positive or negative amount to offset, corresponding to
          the same index into self.lines.
        """
        new_lines = []
        for line, bulge, value in zip(self.lines, self.bulges, values):
            if bulge == 0:
                pass

    def _normals(self, idx):
        p1, p2 = self.lines[idx]
        basic_normal = (
            vector.Vector(p1) - vector.Vector(p2)
        ).orthogonal().normalize()
        if self.curves[idx] == 0:
            return basic_normal[:2], basic_normal[:2]
        else:
            assert abs(self.curves[idx]) <= 90.0, (
                "Large curve values not supported yet")
            return (
                basic_normal.rot_z_deg(-self.curves[idx]/2)[:2],
                basic_normal.rot_z_deg(+self.curves[idx]/2)[:2],
            )

    def _is_smooth(self, idx):
        """Returns whether the vertex between idx and idx+1 is smooth."""
        _, n1 = self._normals(idx)
        n2, _ = self._normals(idx % len(self.lines))
        # TODO epsilon or tolerance constant, and consider keeping these as a
        # class instead of tuple (I'm just going to turn them back into vectors
        # or rays)
        return abs(n1[0]-n2[0]) < 0.0001 and abs(n1[1]-n2[1]) < 0.0001

    def offset(self, value):
        """Offset the polyline by a constant.

        As this is intended for CAM processing, only round join type is
        supported.  The basic algorithm is:
        * Offset points in a direction defined by the line's normal at the
          points.  (Arcs, this is a direction that passes through the center.)
        * Smooth (when the normals match) joins do not create new segments or
          alter bulge.
        * Convex joins are arcs.
        * Concave joins are at the intersection, which may never enlarge bulge,
          only reduce it (because less of the arc remains).

        Args:
          value: The positive or negative amount to offset, which will be the
          same for every line.
        """
        self.offset_custom(itertools.repeat(value))

    def __repr__(self):
        return f"Polyline(lines={self.lines}, curves={self.curves})"
