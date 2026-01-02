
__all__ = ["Camera"]

class Camera:
    _location:list
    motion_tick_time:any

    def __init__(self, location:tuple[int, int]|list[int, int]=(0, 0)): ...

    def motionTimeStart(self, axis:int=-1): ...

    def motion(self, axis:int, speed:int|float|tuple[int, int]|list[int, int]): ...

    @property
    def location(self) -> tuple: ...

    @location.setter
    def location(self, location:tuple[int, int]|list[int, int]): ...
