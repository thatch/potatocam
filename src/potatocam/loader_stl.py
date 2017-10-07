# Copyright 2017 Tim Hatch
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# This is a simplified version of stl.py from my 2d-utils.

import struct
from potatocam import basemesh, math2

class StlFile(object):
    def __init__(self, mesh=None):
        self.mesh = mesh or basemesh.BaseMesh()
        # float -> point index
        self._point_idx = {}
        self.name = None

    def _add_ascii(self, lines):
        in_facet = in_loop = False
        face_points = None

        for line in lines:
            parts = line.split()
            if parts[0] == 'solid':
                self.name = line[5:].strip()
            elif parts[0] == 'facet':
                assert not in_facet
                in_facet = True
                # TODO these normals are often wrong!
                normal = tuple(map(float, parts[2:]))
                face_points = [normal]
            elif parts[-1] == 'loop':
                assert in_facet
                assert not in_loop
                in_loop = True
            elif parts[0] == 'vertex':
                # TODO bad commas.
                pt = tuple(map(float, parts[1:]))
                n = self._add_point(pt)
                face_points.append(n)
            elif parts[0] == 'endloop':
                in_loop = False
            elif parts[0] == 'endfacet':
                # So many normals are bad in files, we just fix it regardless.
                face_points[0] = math2.cross3(
                    math2.sub(self.mesh.points[face_points[2]], self.mesh.points[face_points[1]]),
                    math2.sub(self.mesh.points[face_points[3]], self.mesh.points[face_points[1]]))
                self.mesh.faces.append(face_points)
                face_points = None
                in_facet = False

        assert not in_facet
        assert not in_loop
        assert not face_points

    def _add_point(self, pt):
        n = self._point_idx.get(pt)
        if n is None:
            n = len(self.mesh.points)
            self._point_idx[pt] = n
            self.mesh.points.append(pt)
        return n

    def _add_binary(self, file_obj):
        comment = file_obj.read(80).rstrip('\0').rstrip()
        self.name = comment
        count = struct.unpack('<I', file_obj.read(4))[0]
        for _ in xrange(count):
            floats = struct.unpack('3f3f3f3f', file_obj.read(48))
            normal = tuple(floats[:3])
            a_idx = self._add_point(floats[3:6])
            b_idx = self._add_point(floats[6:9])
            c_idx = self._add_point(floats[9:12])
            self.mesh.faces.append((normal, a_idx, b_idx, c_idx))
            file_obj.read(2) # "should be zero"

    def write_binary(self, file_obj):
        # header
        file_obj.write(self.name.ljust(80))
        file_obj.write(struct.pack('<I', len(self.mesh.faces)))

        for n, a, b, c in self.mesh.faces:
            floats = list(n)
            floats.extend(self.mesh.points[a])
            floats.extend(self.mesh.points[b])
            floats.extend(self.mesh.points[c])
            file_obj.write(struct.pack('3f3f3f3f', *floats))
            file_obj.write('\x00\x00')

    def write_ascii(self, file_obj):
        file_obj.write('solid %s\n' % (self.name,))
        # facet <normal>, loop, vertex
        for n, a, b, c in self.faces:
            file_obj.write('  facet normal %f %f %f\n' % n)
            file_obj.write('    outer loop\n')
            for i in (a, b, c):
                file_obj.write('      vertex %f %f %f\n' % self.points[i])
            file_obj.write('    endloop\n')
            file_obj.write('  endfacet\n')

        file_obj.write('endsolid')


def load(filename):
    with open(filename) as fo:
        return parse(fo)

def parse(file_obj):
    # Quickly check to see if it's ascii.  Requires seekable file object.
    word = file_obj.read(5)
    file_obj.seek(0, 0)
    ret = StlFile()
    if word == 'solid':
        ret._add_ascii(file_obj)
    else:
        ret._add_binary(file_obj)

    return ret

