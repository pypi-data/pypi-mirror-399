from .Common import AutoCalcs2D, _calculate_collision_bounds
from .Constants import Pivot2D

class CollisionBounds:
    def __init__(self, location=(AutoCalcs2D.Center(), AutoCalcs2D.Center()), size=(0, 0), pivot=Pivot2D.TopLeft):
        self._size = tuple(size)
        self._location = tuple(location)
        self._pivot = pivot

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def pivot(self):
        return self._pivot

    @pivot.setter
    def pivot(self, pivot):
        self._pivot = pivot

    def getTrueLocationSize(self, obj_size, obj_location):
        return _calculate_collision_bounds(self._location, self._size, obj_size, obj_location, self._pivot)
