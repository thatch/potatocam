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

from potatocam import math2

class BaseMesh(object):
    # points
    # triangles (index)
    # bounding box
    # transform
    # truncate? (easy when triangle involves the slice, but need to heal edges)

    def __init__(self):
        self.faces = [] # indexing into points.
        self.points = []

    def mult(self, scales):
        b = BaseMesh()
        b.faces = self.faces[:]  # TODO deepcopy
        for p in self.points:
            b.points.append(math2.mult(p, scales))

    def add(self, offsets):
        b = BaseMesh()
        b.faces = self.faces[:]  # TODO deepcopy
        for p in self.points:
            b.points.append(math2.add(p, offsets))

    def bbox(self):
        coords = zip(*self.points)
        mins = map(min, coords)
        maxes = map(max, coords)
        return mins, maxes
