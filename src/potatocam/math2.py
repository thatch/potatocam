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

def sub(a, b):
    return [x-y for x, y in zip(a, b)]

def add(a, b):
    return [x+y for x, y in zip(a, b)]

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def mult(a, s):
    return [x*s for x in a]

def cross3(a, b):
    # Formula from https://www.khronos.org/opengl/wiki/Calculating_a_Surface_Normal
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]]

def length(v):
    return sum(c**2 for c in v) ** 0.5

def norm(v):
    return mult(v, 1/length(v))

def normal(t):
    a = sub(t[1], t[0])
    b = sub(t[2], t[0])
    return cross3(a, b)
