from .Window import Window, InternalWindow
from .Camera import Camera
from .Constants import Colors
from .Object2D import Object2D
from .Color import Color

__all__ = ["_find_line_intersection", "rayCast", "collision"]

def _find_line_intersection(start_1:list[int, int]|tuple[int, int], end_1:list[int, int]|tuple[int, int], start_2:list[int, int]|tuple[int, int], end_2:list[int, int]|tuple[int, int]) -> None|tuple: ...

def rayCast(window:Window|InternalWindow, camera:None|Camera, start:list[int, int]|tuple[int, int], end:list[int, int]|tuple[int, int], objs:list[Object2D]|tuple[Object2D]|None, variables:str|list[str]|tuple[str]) -> bool|list: ...

def collision(window:Window|InternalWindow, camera:None|Camera, obj:Object2D, objs:list[Object2D]|tuple[Object2D]|None, variables:str|list[str]|tuple[str], draw:bool=False, draw_color:Color=Colors.Blue) -> bool|list: ...
