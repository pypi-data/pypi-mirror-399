import os
import sys
from ctypes import CDLL
from platform import system
from ..Log import Log, LogInfo, LogError, LogWarn, ConsoleColors

def nullFunction(*args):
    return

def get_depsPath(file_name: str | list):
    file_name = file_name if isinstance(file_name, str) else file_name[0]
    system_name = system().lower()
    system_paths = []

    if system_name in ("win32", "windows"):
        system_paths = [
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "System32"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "SysWOW64"),
        ]
    elif system_name in ("linux", "linux2"):
        system_paths = [
            "/usr/lib",
            "/usr/local/lib",
            "/lib",
        ]
    elif system_name == "darwin":
        system_paths = [
            "/usr/lib",
            "/usr/local/lib",
        ]

    potential_paths = [
        os.path.abspath(f"./{file_name}"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), file_name)),
        os.path.abspath(os.path.join(os.path.dirname(__file__), f"../{file_name}")),
        *[os.path.join(path, file_name) for path in system_paths],
    ]

    for path in potential_paths:
        if os.path.exists(path):
            return path
    if not sys.argv or sys.argv[0] not in (f"{sys.prefix}\\Scripts\\libmge.exe", f"{sys.prefix}\\Scripts\\libmge"):
        LogInfo(f"{file_name} not found")
    return None

class DLL(object):
    def __init__(self, path=None):
        self._path = path
        if self._path is None:
            self._dll = None
        else:
            try:
                self._dll = CDLL(path)
            except FileNotFoundError:
                self._dll = None
                if not sys.argv or sys.argv[0] not in (f"{sys.prefix}\\Scripts\\libmge.exe", f"{sys.prefix}\\Scripts\\libmge"):
                    LogError(f"Error loading {self._path} missing dependency")

    def bindFunction(self, func_name, args=None, returns=None):
        if func_name == "check":
            return [self._path, self._dll]
        if self._dll is None:
            return None if func_name is None else nullFunction
        else:
            if func_name is None:
                return nullFunction
            func = getattr(self._dll, func_name, None)
            if not func:
                LogError(f"{func_name}")
                return nullFunction
            func.argtypes, func.restype = args, returns
            return func

def get_sdl_func(lib_name):
    extensions = {
        'win32': 'dll',
        'windows': 'dll',
        'darwin': 'dylib',
        'linux': 'so',
        'linux2': 'so',
        'android': 'so'
    }
    return DLL(get_depsPath(f"{lib_name}.{extensions.get(system().lower(), 'so')}")).bindFunction

SDLFunc = get_sdl_func("SDL2")
GFXFunc = get_sdl_func("SDL2_gfx")
IMAGEFunc = get_sdl_func("SDL2_image")
MIXERFunc = get_sdl_func("SDL2_mixer")
TTFFunc = get_sdl_func("SDL2_ttf")

if None in (SDLFunc(None), GFXFunc(None), IMAGEFunc(None), MIXERFunc(None), TTFFunc(None)):
    if not sys.argv or sys.argv[0] not in (f"{sys.prefix}\\Scripts\\libmge.exe", f"{sys.prefix}\\Scripts\\libmge"):
        LogWarn("LibMGE dependencies not found.")
        Log(f"\n{ConsoleColors.Reset}Run '{ConsoleColors.Bold}LibMGE deps install{ConsoleColors.Reset}' to install them")
        sys.exit(1)
