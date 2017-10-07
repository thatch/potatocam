from potatocam import basemesh

def test_bbox():
    b = basemesh.BaseMesh()
    b.points = [[0,0,0], [1,2,3]]
    m, n = b.bbox()
    assert m == [0,0,0]
    assert n == [1,2,3]

def test_bbox_indep():
    b = basemesh.BaseMesh()
    b.points = [[0,0,0], [1,2,3], [3, 2, 1], [0, 3, 0]]
    m, n = b.bbox()
    assert m == [0,0,0]
    assert n == [3,3,3]
