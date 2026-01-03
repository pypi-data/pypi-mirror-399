from .Camera import Camera
from .Vector import object2dSimpleMotion
from .Mouse import object2dSimpleHover
from .Material import Material, DefaultMaterial
from .Constants import Pivot2D, Meshes2D
from .Collisions import collision
from .CollisionBounds import CollisionBounds
from .Mesh import Mesh2D
from .Common import _temp, _calculate_object2d, _calculate_size, _calculate_location
from .Time import Time, fps_to_time
from .Window import Window, InternalWindow
from .Color import Color
from ._sdl import sdl2

__all__ = ["Object2D"]

class Object2D:
    def __init__(self, location=(0, 0), rotation: int = 0, size=(0, 0), scale=(1, 1), material: Material = DefaultMaterial, mesh: Mesh2D = Meshes2D.Plane):
        self._size = list(size)
        self._location = list(location)
        self._rotation = rotation
        self._scale = list(scale)
        self._mesh = mesh
        self._pivot = Pivot2D.TopLeft
        self._border_size = 0
        self._border_color = Color((100, 100, 255))
        self._border_radius = [0, 0, 0, 0]
        self._cursor = 11
        self._material = material

        self._frames = []

        self._motion_tick_time = {"x": Time(fps_to_time(60)), "y": Time(fps_to_time(60))}

        self.variables = {"_type": "Object2D"}

        self._showMoreDetailsOfCollisions = False
        self.collisionBounds: CollisionBounds | None = None
        self._directionalCollisionDetectionZone = 5

        self.object_render = self.thed_render = self.always_render = False

        self.cache_object = None
        self.cache_object_tx = None

    def render(self, window):
        if self.object_render:
            return
        material = self._material
        if material.textures:
            if self.cache_object is None:
                material.render()
                self.cache_object = material.surface
                if self.cache_object_tx is not None:
                    sdl2.SDL_DestroyTexture(self.cache_object_tx)
                self.cache_object_tx = sdl2.SDL_CreateTextureFromSurface(window.renderer, self.cache_object).contents
                sdl2.SDL_SetTextureScaleMode(self.cache_object_tx, 1)
        else:
            if self.cache_object is not None:
                self.cleanCache()
            material.render()
        self.object_render = True

    def drawObject(self, window: Window | InternalWindow, camera: Camera = None):
        if not window.__WindowActive__ or not window.drawnObjects.addObject(id(self), self):
            return

        _render, cache_location, cache_size = _calculate_object2d(self._location, self._size, self._rotation, self._scale, window, camera, self._pivot)
        if not _render:
            return

        if not self.object_render or self.always_render or window.render_all_objects:
            self.render(window)

        material = self._material
        if self._mesh.vertices:
            _color = material.surfaceColor if material.textures else material.color
            window.drawPolygon(cache_location, self._scale, self._rotation, self._mesh, _color)
        else:
            if self.cache_object is None:
                window.drawSquare(cache_location, cache_size, self._rotation, self._border_radius, material.color)
            else:
                material.update()
                frames_updated = False
                self._frames.extend([0] * (len(material.textures) - len(self._frames)))
                for i, texture in enumerate(material.textures):
                    if self._frames[i] != texture._frame:
                        frames_updated = True
                        self._frames[i] = texture._frame
                if frames_updated:
                    self.cache_object = material.surface
                    sdl2.SDL_UpdateTexture(self.cache_object_tx, None, self.cache_object.pixels, self.cache_object.pitch)
                window.blit(self.cache_object_tx, cache_location, cache_size, self._rotation)
            if self._border_size > 0:
                window.drawEdgesSquare(cache_location, cache_size, self._rotation, self._border_size, self._border_radius, self._border_color)

    def hover(self, window, camera: Camera = None) -> bool:
        if object2dSimpleHover(window, camera, self._location, self._size, self._scale, self._pivot):
            _temp.MouseCursor = self._cursor
            return True
        return False

    def cleanCache(self):
        self.cache_object = None
        if self.cache_object_tx is not None:
            sdl2.SDL_DestroyTexture(self.cache_object_tx)
            self.cache_object_tx = None

    def close(self):
        self.cleanCache()
        del self

    @property
    def location(self) -> list[int, int]:
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    def getTrueLocation(self, window: Window | InternalWindow, camera: Camera = None):
        _location_camera = camera.location if camera is not None else window.camera.location
        _size_window = window.logicalResolution

        _size = _calculate_size((0, 0), self._size, _size_window, self._scale)
        _location = _calculate_location(self._location, _size, _size_window, self._scale)

        return _location[0] + _location_camera[0], _location[1] + _location_camera[1]

    @property
    def size(self) -> list[int, int]:
        return self._size

    @size.setter
    def size(self, size):
        if self._size != size:
            self._size = size
            self.object_render = False

    def getTrueSize(self, window: Window | InternalWindow, camera: Camera = None):
        _location_camera = camera.location if camera is not None else window.camera.location
        _size_window = window.logicalResolution

        return _calculate_size((0, 0), self._size, _size_window, self._scale)

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: int | float):
        if self._rotation != rotation:
            self._rotation = round(rotation, 4)
            self._rotation %= 360

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        if self._scale != scale:
            self._scale = scale
            self.object_render = self._material.object_render = False

    @property
    def pivot(self):
        return self._pivot

    @pivot.setter
    def pivot(self, pivot):
        self._pivot = pivot

    def getTrueRenderLocationSize(self, window: Window | InternalWindow, camera: Camera = None):
        return _calculate_object2d(self._location, self._size, self._rotation, self._scale, window, camera, self._pivot)

    @property
    def borderSize(self):
        return self._border_size

    @borderSize.setter
    def borderSize(self, border_size: int):
        self._border_size = border_size

    @property
    def borderColor(self):
        return self._border_color

    @borderColor.setter
    def borderColor(self, border_color: Color):
        self._border_color = border_color

    @property
    def borderRadius(self):
        return self._border_radius

    @borderRadius.setter
    def borderRadius(self, radius: int | tuple[int, int, int, int]):
        if isinstance(radius, int):
            self._border_radius = [radius, radius, radius, radius]
        elif isinstance(radius, (tuple, list)) and len(radius) == 4:
            self._border_radius = [radius[0], radius[1], radius[2], radius[3]]

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, material: Material):
        if self._material != material:
            self._material = material
            self.object_render = self._material.object_render = False

    def cursor(self, cursor: int):
        self._cursor = cursor

    @property
    def mesh(self):
        return self._mesh

    @mesh.setter
    def mesh(self, mesh):
        self._mesh = mesh

    def motion(self, axis, axis_type, speed: int | float | tuple):
        #Program.Temp.ForceRender = True
        if axis_type == 10:  # global
            if axis == 1 or axis == -1:  # x
                self._location[0] += (speed if type(speed) == int or type(speed) == float else speed[0]) * self._motion_tick_time["x"].tickMotion()
            if axis == 2 or axis == -1:  # y
                self._location[1] += (speed if type(speed) == int or type(speed) == float else speed[1]) * self._motion_tick_time["y"].tickMotion()
        if axis_type == 30:  # local
            if self._motion_tick_time["y"].tick():
                self.location = object2dSimpleMotion(self, axis, speed)

    def collision(self, window: Window | InternalWindow, camera: Camera = None, objects: object | list = None, variables: str | list = None) -> bool | list:
        _ret = collision(window, camera, self, objects, variables, False)
        if _ret:
            return _ret if self._showMoreDetailsOfCollisions else True
        return False
