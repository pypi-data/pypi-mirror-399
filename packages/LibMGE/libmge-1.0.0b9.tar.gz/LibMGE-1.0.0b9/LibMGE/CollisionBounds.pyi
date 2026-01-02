from .Common import AutoCalcs2D
from .Constants import Pivot2D

class CollisionBounds:
    _size:tuple[int, int]
    _location:tuple[int, int]
    _pivot:tuple

    def __init__(self, location:tuple|list=(AutoCalcs2D.Center(), AutoCalcs2D.Center()), size:tuple|list=(0, 0), pivot:tuple=Pivot2D.TopLeft):

    @property
    def location(self) -> tuple[int, int]: ...

    @location.setter
    def location(self, location:tuple[int, int]): ...

    @property
    def size(self) -> tuple[int, int]: ...

    @size.setter
    def size(self, size:tuple[int, int]): ...

    @property
    def pivot(self) -> tuple: ...

    @pivot.setter
    def pivot(self, pivot:tuple): ...

    def getTrueLocationSize(self, obj_size:tuple|list, obj_location:tuple|list) -> tuple[tuple[int, int], tuple[int, int]]: ...
