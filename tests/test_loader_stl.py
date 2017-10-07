import os.path

from potatocam import loader_stl

BASE = os.path.abspath(os.path.dirname(__file__))

def test_file_object():
    with open(os.path.join(BASE, 'stl/widget.stl'), 'rb') as fo:
        obj = loader_stl.parse(fo)
    assert len(obj.mesh.faces) > 100
    assert len(obj.mesh.points) > 100

def test_file_name():
    obj = loader_stl.load(os.path.join(BASE, 'stl/widget.stl'))
    assert len(obj.mesh.faces) > 100
    assert len(obj.mesh.points) > 100
