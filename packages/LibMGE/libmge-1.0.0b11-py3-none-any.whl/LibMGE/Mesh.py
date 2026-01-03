import os
from math import cos, sin, radians
from .Log import LogError

def rotate_point(x, y, cx, cy, angle):
    angle_rad = radians(angle)

    dx = x - cx
    dy = y - cy

    new_x = dx * cos(angle_rad) - dy * sin(angle_rad) + cx
    new_y = dx * sin(angle_rad) + dy * cos(angle_rad) + cy

    return round(new_x), round(new_y)

def calculate_square_vertices(location, size, rotation_angle):
    x, y = location
    width, height = size

    cx = x + width / 2
    cy = y + height / 2

    vertices = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]

    if rotation_angle != 0:
        vertices = [rotate_point(v[0], v[1], cx, cy, rotation_angle) for v in vertices]

    return vertices

def edges(vertices):
    _edges = [(vertices[num], vertices[num+1 if num+1 <= len(vertices)-1 else 0]) for num in range(len(vertices))]
    return _edges

class Mesh2D:
    def __init__(self, vertices: list):
        self._vertices = vertices
        self._edges = []
        self._faces = []

    @property
    def vertices(self):
        return self._vertices

    @property
    def edges(self):
        return edges(self._vertices)

def LoadObj(path):
    vertices = []
    if os.path.exists(path):
        with open(path) as obj:
            r = obj.read()
            for rr in r.split("\n"):
                if len(rr) > 0 and rr[0] == "v":
                    r2 = rr.split()
                    vertices.append((int(float(r2[1]) * 100), int(float(r2[3] if len(r2) == 4 else r2[2]) * 100)))
    if len(vertices) == 0:
        LogError(f"{path}")
    return Mesh2D(vertices)

def CreateMeshPlane(size):
    return Mesh2D([(0, 0), (size[0], 0), (size[0], size[1]), (0, size[1])])
