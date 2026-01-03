from ..Log import Log, ConsoleColors
from ctypes import POINTER as _P, Structure, c_uint8
from .._sdl._dll_loader import SDLFunc, GFXFunc, IMAGEFunc, MIXERFunc, TTFFunc

class SDL_version(Structure):
    _fields_ = [("major", c_uint8), ("minor", c_uint8), ("patch", c_uint8)]

def _get_sdl_version():
    if SDLFunc(None) is None:
        return None

    version = SDL_version()
    SDLFunc("SDL_GetVersion", [_P(SDL_version)])(version)
    return f"{version.major}.{version.minor}.{version.patch}"

def _get_sdlimage_version():
    if IMAGEFunc(None) is None:
        return None

    version = IMAGEFunc("IMG_Linked_Version", None, _P(SDL_version))().contents
    return f"{version.major}.{version.minor}.{version.patch}"

def _get_sdlmixer_version():
    if MIXERFunc(None) is None:
        return None

    version = MIXERFunc("Mix_Linked_Version", None, _P(SDL_version))().contents
    return f"{version.major}.{version.minor}.{version.patch}"

def _get_sdlttf_version():
    if TTFFunc(None) is None:
        return None

    version = TTFFunc("TTF_Linked_Version", None, _P(SDL_version))().contents
    return f"{version.major}.{version.minor}.{version.patch}"

def check():
    return {
        "SDL2": {
            "present": SDLFunc("check"),
            "version": _get_sdl_version(),
        },
        "SDL2_gfx": {
            "present": GFXFunc("check"),
            "version": None,
        },
        "SDL2_image": {
            "present": IMAGEFunc("check"),
            "version": _get_sdlimage_version(),
        },
        "SDL2_mixer": {
            "present": MIXERFunc("check"),
            "version": _get_sdlmixer_version(),
        },
        "SDL2_ttf": {
            "present": TTFFunc("check"),
            "version": _get_sdlttf_version(),
        },
    }

def _print_deps(show_header=True, indent="  "):
    if show_header:
        Log("\n  Dependencies:", ConsoleColors.Reset)

    deps = check()
    for name, info in deps.items():
        path, dll = info["present"]

        if not path:
            status = f"{ConsoleColors.Red}MISSING"
        elif not dll:
            status = f"{ConsoleColors.Yellow}FOUND - missing dependency"
        else:
            version_str = f" v{info['version']}" if info["version"] else ""
            status = f"{ConsoleColors.Green}OK{version_str}"

        Log(f"{indent}{name:<11} →  {status}", ConsoleColors.Reset)
