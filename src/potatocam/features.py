import enum

import numpy
import openmesh
import pyclipper

__all__ = [
    "SpecialFeatureType",
    "PolygonOrientation",
    "FoldDirection",
    "FeatureExtractor",
    "load_mesh",
]


# This can be derived from winding order, but store explicitly to make simpler.
class PolygonOrientation(enum.IntEnum):
    OUTSIDE = 0
    INSIDE = 1


class FoldDirection(enum.IntEnum):
    UP = 3
    DOWN = 4


class SpecialFeatureType(enum.IntEnum):
    NORMAL = 0
    TOP = 10
    BOT = 11


class Feature:
    """
    A feature can be thought of roughly as a plateau (or canyon floor, but can
    also be a hybrid).

    It represents the path around a "ridge" which is the boundary.  Holes are
    represented as a list of Features which are also part of the same connected
    set of flat faces, but those will not have a further level.  Any contained
    features  will instead be treated as additional top-level objects.

    fold_directions[n] contains  whether the line from outline[n] to
    outline[n+1] goes up or down.  This will eventually migrate into a bitset on
    polyline segments.
    """

    def __init__(
        self,
        height,
        direction,
        outline,
        fold_directions,
        normal,
        # TODO: Consider bitset flags, we may want to recognize holes?
        flags=SpecialFeatureType.NORMAL,
    ):
        self.height = height
        self.direction = direction
        self.outline = outline
        self.fold_directions = fold_directions
        self.normal = normal
        self.flags = flags

        self.holes = []
        # TODO: start_height, to let higher pockets/facing plow over their
        # hole-islands, then when when a lower feature ~identical to the island
        # (think: connected by a small number of vertical halfedges) is to be
        # cut, it can start at the higher level rather than (stock top+safety)

    def roll(self):
        """Rotates outline/fold_directions so that they have a consistent
        starting point from one test to another. Does not change orientation.
        Mainly useful for tests."""
        min_x = None
        min_i = None
        for i, x in enumerate(self.outline):
            # There should not be ties
            if min_x is None or min_x > x:
                min_x = x
                min_i = i

        self.outline = self.outline[min_i:] + self.outline[:min_i]
        self.fold_directions = (
            self.fold_directions[min_i:] + self.fold_directions[:min_i]
        )

    def bbox(self):
        """Returns (x_min, y_min), (x_max, y_max)"""
        xs, ys = zip(*self.outline)
        return ((min(xs), min(ys)), (max(xs), max(ys)))

    def bbox_area(self):
        """See bbox, returns dx*dy"""
        (x_min, y_min), (x_max, y_max) = self.bbox()
        return (x_max - x_min) * (y_max - y_min)

    def __repr__(self):
        return "Feature(h={} d={} outline={} folds={})".format(
            self.height,
            self.direction,
            list(map(tuple, self.outline[:10])),
            set(x.name for x in self.fold_directions),
        )


class FeatureExtractor:
    def __init__(self, mesh, tolerance=1e-100):
        self.mesh = mesh
        self.tolerance = tolerance
        # A well-formed TriMesh may only have one ridge per flat face (considering
        # edges, not vertices).  Multiple (maybe even all) of the halfedges on
        # the face may be on the ridge, however.
        self.seen_faces = set()
        self.features = []

        self.max_height = numpy.amax(self.mesh.points()[:, 2])
        self.min_height = numpy.amin(self.mesh.points()[:, 2])
        assert self.min_height == 0.0, "Code is untested when not at z=0"

    def extract(self):
        """
        Find all flat features, storing their height, and for each halfedge
        whether it folds up (concave) or down (convex).  This includes
        upside-down ones at this point.

        * Top-most flat feature defines the stock height, but its only other use
          is if adding a chamfer.
        * Intermediate +z normal features are pockets.
        * Final outline and holes are found from the -z normal feature on
          the bottom -- hopefully this is just flat, with nothing interesting.

        When this is complete, self.features contains the exterior polylines.
        """

        for f in self.mesh.faces():
            if f.idx() in self.seen_faces:
                continue
            he = self.mesh.halfedge_handle(f)
            if not self._is_flat(he):
                continue
            # We have a flat face, see if any of its halfedges are folded
            # (on typically-tesselated meshes, most will)
            for i in range(3):
                if self._is_folded(he, self._pz(he)):
                    self._extract_plateau(he)
                    break
                he = self.mesh.next_halfedge_handle(he)

    def _pt(self, he):
        """Returns (x, y) from the halfedge from-vertex"""
        return self.mesh.point(self.mesh.from_vertex_handle(he))[:2]

    def _pz(self, he):
        """Returns z from the halfedge from-vertex"""
        return self.mesh.point(self.mesh.from_vertex_handle(he))[2]

    def _vz(self, v):
        """Returns z from the vertex"""
        return self.mesh.point(v)[2]

    def _extract_plateau(self, starting_halfedge):
        """
        We don't know if this halfedge is on the outline or a hole, so do
        flood-fill on the faces to discover remaining sections before deciding
        what the top-level feature is.
        """
        z = self._pz(starting_halfedge)
        assert self._is_flat(starting_halfedge)
        assert self._is_folded(starting_halfedge, z)
        # Get the first feature, but we don't yet know if it's a top-level
        # feature or a hole within one.
        feats = []
        # this `seen` is face indices that have been assigned to a ridge, not
        # ones followed in DFS.  We don't need to init with self.seen_faces
        # because those should be disjoint.
        f, seen = self._follow_ridge(starting_halfedge)
        feats.append(f)

        stack = [self.mesh.face_handle(starting_halfedge).idx()]
        dfs_seen = set()
        while stack:
            face = self.mesh.face_handle(stack.pop())
            dfs_seen.add(face.idx())
            # Maybe there's a new ridge
            if face.idx() not in seen:
                he = self.mesh.halfedge_handle(face)
                for i in range(3):
                    if self._is_folded(he, z):
                        f, seen2 = self._follow_ridge(he)
                        seen |= seen2
                        feats.append(f)
                        # with triangles a face may only participate in one ridge
                        break
            # Look at neighboring faces
            for nf in openmesh.FaceFaceIter(self.mesh, face):
                if nf.idx() in dfs_seen:
                    continue
                if self._is_flat(self.mesh.halfedge_handle(nf)):
                    stack.append(nf.idx())

        # This is an extremely simple heuristic that we can improve later.
        # Given two polygons that do not have overlapping lines, the one with
        # the smaller area is inside.  (Using bbox as a simple substitute for
        # area.)
        print("CONNECTED FEATURES:", len(feats))
        feats.sort(key=lambda f: f.bbox_area(), reverse=True)
        for f in feats:
            print("  ", f.bbox(), f)

        feats[0].holes = feats[1:]
        self.features.append(feats[0])
        self.seen_faces |= seen

    def _follow_ridge(self, starting_halfedge):
        """
        This logic is prone to drift, but assuming well-behaved input and a
        reasonable tolerance, this should not be an issue in practice.

        This must be called with a halfedge that meets the conditions of:
        - `is_flat` (meaning associated face is flat)
        - `fold_direction` is not `None` (meaning opposite face is non-flat)

        The resulting ridge is added to `self.features`.
        """
        he = starting_halfedge
        height = self._pz(he)
        assert self._is_flat(he)
        assert self._fold_direction(he, height) is not None
        normal = tuple(self.mesh.calc_face_normal(self.mesh.face_handle(he)))
        poly = []
        folds = []
        seen = set()

        while True:
            v = self.mesh.to_vertex_handle(he)
            # voh is vertex-outgoing-halfedges
            for nhe in self.mesh.voh(v):
                # Is the associated face flat?
                if self._is_flat(nhe):
                    # Make sure opposite face is folded
                    d = self._fold_direction(nhe, height)
                    if d is not None:
                        poly.append(tuple(self._pt(nhe)))
                        folds.append(d)
                        he = nhe
                        break
            else:
                raise ValueError("Non-closed ridge at {}".format(he.idx()))

            seen.add(self.mesh.face_handle(he).idx())
            if he == starting_halfedge:
                break

        # TODO: should use to_clipper

        # We're using an odd convention that the orientation of the outline is
        # The orientation of the outline is backwards to the normal triangle
        # winding
        poly = poly[::-1]
        folds = folds[::-1]
        folds.append(folds.pop(0))  # avoids off-by-one

        if pyclipper.Orientation(poly):
            orientation = PolygonOrientation.OUTSIDE
        else:
            orientation = PolygonOrientation.INSIDE
        # This helps us keep track of the type of operation we need to perform,
        # but means that the convention is potentially confusing because it's
        # opposite of convention.  (Normally positive offsets go outside, in our
        # case positive offset of bit-radius can provides the new path.)
        #
        # - TOP defines the work height but also may optionally be faced
        #   similarly to a pocket (it will only have DOWN folds, will have
        #   INSIDE orientation, and be wound CW)
        # - NORMAL is a pocket (will have INSIDE orientation, and be wound CW)
        # - BOT defines the outline and through-holes (but started upside-down;
        #   this will have OUTSIDE orientation and be wound CCW)
        flags = SpecialFeatureType.NORMAL
        if height == self.min_height:
            flags = SpecialFeatureType.BOT
        elif height == self.max_height:
            flags = SpecialFeatureType.TOP

        f = Feature(height, orientation, poly, folds, normal, flags)
        return f, seen

    def _is_folded(self, he, z):
        return self._fold_direction(he, z) is not None

    def _fold_direction(self, he, z):
        """Given the halfedge adjacent to the flat side, return the direction of
        the folded side (or None)."""
        opposite_vertex = self.mesh.to_vertex_handle(
            self.mesh.next_halfedge_handle(self.mesh.opposite_halfedge_handle(he))
        )
        # This looks reversed, but by tests I'm pretty sure it's right.
        dz3 = self._vz(opposite_vertex) - z
        # print(z, self._debug_halfedges_z(self.mesh.opposite_halfedge_handle(he)), dz3)
        if abs(dz3) < self.tolerance:
            return None
        return FoldDirection.DOWN if dz3 < 0 else FoldDirection.UP

    def _is_flat(self, he):
        """Given a halfedge, return whether its face is flat."""
        nz = self.mesh.calc_face_normal(self.mesh.face_handle(he))[2]
        r = 0.999 < abs(nz) < 1.001
        return r

    def _debug_halfedges_z(self, starting_he):
        buf = [self.mesh.point(self.mesh.from_vertex_handle(starting_he))[2]]
        he = self.mesh.next_halfedge_handle(starting_he)
        while he != starting_he:
            buf.append(self.mesh.point(self.mesh.from_vertex_handle(he))[2])
            he = self.mesh.next_halfedge_handle(he)
        return buf


def load_mesh(filename):
    return openmesh.read_trimesh(filename)
