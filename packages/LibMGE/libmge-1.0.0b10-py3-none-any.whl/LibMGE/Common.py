import os

from .Log import LogCritical
from ctypes import cast, POINTER as _P
from ._sdl import sdl2, sdlimage, sdlttf, sdlmixer
from .Time import Time as _Time, fps_to_time
from .Monitors import _update_monitors_datas
from .Constants import All
from .Mesh import edges, calculate_square_vertices
from .Collisions import _find_line_intersection

__all__ = ["_temp", "init", "update", "SetLogicClock", "GetLogicClock", "OpenUrl",
           "AllEvents", "QuitEvent", "WindowEvents", "AutoCalcs2D",
           "_calculate_size", "_calculate_location", "_calculate_object2d", "_calculate_line", "_calculate_collision_bounds"]

class _temp:
    LogicClock = 1024

    mouse_motion_tick_time = {"x": _Time(fps_to_time(60)), "y": _Time(fps_to_time(60))}

    Time = {"LogicTime": _Time(fps_to_time(LogicClock))}

    Events = []

    KeyboardState = sdl2.SDL_GetKeyboardState(None)
    KeyboardCache = []
    for num in range(530):
        KeyboardCache.append(True)

    MouseState = [False, False, False, False, False]
    Mouse = {"location": None, "button_cache": [False, False, False, False, False]}

    MouseCursor = 0

    MouseCursors = []

    Button = {"button_active": False}

def init(video=True, audio=False, events=True, controller=False, sensor=False):
    if sdl2.SDL_Init(0) != 0:
        LogCritical("initializing SDL2")

    def sdl2_init(system):
        if sdl2.SDL_InitSubSystem(system) != 0:
            LogCritical(f"initializing the {system} subsystem")

    sdl2_init(sdl2.SDL_INIT_TIMER)
    if events:
        sdl2_init(sdl2.SDL_INIT_EVENTS)
    if video:
        sdl2_init(sdl2.SDL_INIT_VIDEO)
        for num in range(12):
            _temp.MouseCursors.append(sdl2.SDL_CreateSystemCursor(num).contents)
        _update_monitors_datas()
        sdlttf.TTF_Init()
        sdlimage.IMG_Init()
        os.environ["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"
    if audio:
        sdlmixer.Mix_OpenAudio(360000, sdl2.AUDIO_S16SYS, 2, 1024)
        sdlmixer.Mix_Init()
    if controller:
        sdl2_init(sdl2.SDL_INIT_JOYSTICK)
        sdl2_init(sdl2.SDL_INIT_GAMECONTROLLER)
    # if haptic:
    #    sdl2_init(sdl2.SDL_INIT_HAPTIC)
    if sensor:
        sdl2_init(sdl2.SDL_INIT_SENSOR)

def update():
    _temp.Time["LogicTime"].tickSleep()

    sdl2.SDL_PumpEvents()
    events = (sdl2.SDL_Event * 10)()
    _events = sdl2.SDL_PeepEvents(
        cast(events, _P(sdl2.SDL_Event)), 10, sdl2.SDL_GETEVENT,
        sdl2.SDL_FIRSTEVENT, sdl2.SDL_LASTEVENT
    )
    _temp.Events = events[:_events]

    _keyboard = sdl2.SDL_GetKeyboardState(None)
    _temp.KeyboardState = [bool(_keyboard[i]) for i in range(530)]

    _mouse = sdl2.SDL_GetMouseState(None, None)
    _temp.MouseState = [(_mouse & (1 << i)) != 0 for i in range(5)]

    if _temp.Button["button_active"]:
        _temp.Button["button_active"] = False
    sdl2.SDL_SetCursor(_temp.MouseCursors[_temp.MouseCursor])
    _temp.MouseCursor = 0

def SetLogicClock(logic_clock: int):
    _temp.Time["LogicTime"].delta_time = fps_to_time(logic_clock)

def GetLogicClock() -> int:
    return _temp.LogicClock

def OpenUrl(url: str):
    sdl2.SDL_OpenURL(url)

def AllEvents() -> list:
    return _temp.Events

def QuitEvent() -> bool:
    for event in AllEvents():
        if event.type == 256:
            return True
    return False

def WindowEvents(window: int = All, event: int = All):
    for _event in AllEvents():
        if _event.type == 512:
            if window == _event.window.windowID or window == All:
                if event == _event.window.event or event == All:
                    return _event.window.event
    return 0

class AutoCalcs2D:
    @staticmethod
    def Percent(percent: int):
        return lambda location, size, size_window, scale: size_window / 100 * percent

    @staticmethod
    def Center():
        return lambda location, size, size_window, scale: size_window / 2

def _calculate_size(location, size, size_window, scale) -> list:
    return [round(size[num](location[num], size[num], size_window[num], scale[num]) * scale[num]) if callable(size[num]) else round(size[num] * scale[num]) for num in range(2)]

def _calculate_location(location, size, size_window, scale) -> list:
    return [round(location[num](location[num], size[num], size_window[num], scale[num])) if callable(location[num]) else round(location[num]) for num in range(2)]

def _calculate_pivot(location, size, pivot) -> tuple:
    return round(location[0] + int(pivot[0] * size[0])), round(location[1] + int(pivot[1] * size[1]))

def _calculate_object2d(location, size, rotation, scale, window, camera, pivot) -> tuple[bool, tuple[int, int], tuple[int, int]]:
    _location_camera = camera.location if camera is not None else window.camera.location
    _size_window = window.logicalResolution

    _size = tuple(_calculate_size((0, 0), size, _size_window, scale))
    _location = _calculate_location(location, _size, _size_window, scale)

    _location = (_location[0] + _location_camera[0], _location[1] + _location_camera[1])
    _location = _calculate_pivot(_location, _size, pivot)

    render = (-_size[0] < _location[0] < _size_window[0] and -_size[1] < _location[1] < _size_window[1])
    if not render:
        obj_edges = edges(calculate_square_vertices(_location, _size, rotation))
        win_edges = edges([(0, 0), (0, window.resolution[1]), window.resolution, (window.resolution[0], 0)])
        render = any(_find_line_intersection(obj_edges[i][0], obj_edges[i][1], win_edges[j][0], win_edges[j][1]) for i in range(4) for j in range(4))

    return render, _location, _size

def _calculate_line(start, end, size, window, camera) -> tuple[bool, tuple[int, int], tuple[int, int], int]:
    _location_camera = camera.location if camera is not None else window.camera.location
    _size_window = window.logicalResolution

    _size = _calculate_size((0, 0), (size, 0), _size_window, (1, 1))[0]
    _start = _calculate_location(start, (0, 0), _size_window, (1, 1))
    _end = _calculate_location(end, (0, 0), _size_window, (1, 1))

    _start = _start[0] + _location_camera[0], _start[1] + _location_camera[1]
    _end = _end[0] + _location_camera[0], _end[1] + _location_camera[1]

    render = (-_size < _start[0] < _size_window[0] and -_size < _start[1] < _size_window[1]) or (-_size < _end[0] < _size_window[0] and -_size < _end[1] < _size_window[1])
    if not render:
        win_edges = edges([(0, 0), (0, window.resolution[1]), window.resolution, (window.resolution[0], 0)])
        render = any(_find_line_intersection(_start, _end, win_edges[i][0], win_edges[i][1]) for i in range(4))

    return render, _start, _end, _size

def _calculate_collision_bounds(location, size, obj_size, obj_location, pivot) -> tuple[tuple[int, int], tuple[int, int]]:
    _size = tuple(_calculate_size((0, 0), size, obj_size, (1, 1)))
    _location = _calculate_pivot(_calculate_location(location, _size, obj_size, (1, 1)), _size, pivot)
    _location = (_location[0] + obj_location[0], _location[1] + obj_location[1])

    return _location, _size
