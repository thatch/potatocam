"""
See docs on the Polyline class.
"""

import collections
import itertools
import enum
import math

from typing import Tuple, List, Sequence

from ezdxf.algebra.vector import Vector
from ezdxf.algebra.bulge import bulge_center, bulge_to_arc

__all__ = ["Polyline", "Segment", "SegmentFlags"]


class SegmentFlags(enum.IntFlag):
    NONE = 0
    FOLD_UP = 1
    FOLD_DOWN = 2


class Segment:
    def __init__(self, pt: Tuple[float], curve: float=0.0, flags:SegmentFlags=SegmentFlags.NONE):
        self.pt = pt
        self.curve = curve
        self.flags = flags

    def __repr__(self):
        if self.flags == 0:
            flags = ""
        else:
            flags = ", {self.flags}"
        if self.curve == 0:
            return f"S({self.pt}{flags})"
        else:
            return f"Segment(pt={self.pt}, curve={self.curve}{flags})"


class Polyline:
    """
    Represents a closed shape consisting of straight lines and circular arcs.

    Debating the best way to represent arcs is one of the great debates of our
    age.  This choses a method similar to EAGLE (`curve`, in degrees) which is
    probably inspired by AutoCAD's LWPOLYLINE (although the internal
    representation for `bulge` there is `tan(t/4)`.  Straight lines are
    represented as `curve=0`.

    We store `segments` which are annotated points.  Each point is the start of
    a line (thus `_normals(i)` gives the values at `i` and `i+1`).
    """
    def __init__(self, normal: Tuple[float, float, float] = None):
        self.segments: List[Segment] = []
        self.normal = normal

    def __repr__(self):
        return f"Polyline(segments={self.segments})"

    def add_segment(self, seg):
        self.segments.append(seg)

    def offset(self, value):
        """Offset the polyline by a constant.

        As this is intended for CAM processing, only round join type is
        supported.  The basic algorithm is:
        * Offset points in a direction defined by the line's normal at the
          points.  (Arcs, this is a direction that passes through the center.)
        * Smooth (when the normals match) joins do not create new segments or
          alter `curve`.
        * Convex joins are arcs.
        * Concave joins are at the intersection, which may never enlarge an arc,
          only reduce it (because less of the arc remains).

        Args:
          value: The positive or negative amount to offset, which will be the
          same for every line.
        """
        return self.offset_custom([value] * len(self.segments))

    def offset_custom(self, values: Sequence[float]):
        """
        Args:
          values: The positive or negative amount to offset, corresponding to
          the line from idx to idx+1 in self.segments.
        """
        new_polyline = self.__class__(self.normal)
        # TODO handle self-intersections

        prev_normal = Vector(self._normals(-1)[1])

        for idx, seg in enumerate(self.segments):
            n1, n2 = self._normals(idx)
            if n1 != prev_normal:
                c = prev_normal.cross(n1)[2]
                print("OFF", prev_normal, n1, c)
                if abs(c) < 0.0001:
                    # smooth/same?
                    pt = Vector(seg.pt) + n1 * offsets[idx]
                    new_polyline.add_segment(Segment(pt, seg.curve, seg.flags))
                elif c > 0:
                    # convex, add arc
                    pass
                elif c < 0:
                    # concave?
                    pass

            prev_normal = Vector(n2)
        return new_polyline

    def _normals(self, idx):
        # The line is from idx-1 to idx
        next_idx = (idx + 1) % len(self.segments)
        basic_normal = (
            (
                Vector(self.segments[next_idx].pt)
                - Vector(self.segments[idx].pt)
            )
            .orthogonal()
            .normalize()
        )
        curve = self.segments[idx].curve
        if curve == 0:
            return basic_normal[:2], basic_normal[:2]
        else:
            assert abs(curve) <= 90.0, "Large curve values not supported yet"
            return (
                basic_normal.rot_z_deg(-curve / 2)[:2],
                basic_normal.rot_z_deg(+curve / 2)[:2],
            )

    def _is_smooth(self, idx):
        """Returns whether the vertex between idx-1 and idx is smooth."""
        _, n1 = self._normals((idx-1) % len(self.segments))
        n2, _ = self._normals(idx % len(self.segments))
        # TODO epsilon or tolerance constant, and consider keeping these as a
        # class instead of tuple (I'm just going to turn them back into 
        # or rays)
        return abs(n1[0] - n2[0]) < 0.0001 and abs(n1[1] - n2[1]) < 0.0001

    def roll(self):
        """Make this polyline start at a known point, preserving direction.

        This is useful for tests."""
        min_x = None
        min_i = None
        for i, seg in enumerate(self.segments):
            # There should not be ties
            if min_x is None or min_x > seg.pt:
                min_x = seg.pt
                min_i = i

        self.segments = self.segments[min_i:] + self.segments[:min_i]

