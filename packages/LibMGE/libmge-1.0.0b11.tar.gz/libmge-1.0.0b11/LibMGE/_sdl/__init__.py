import sys

__all__ = ["sdl2", "sdlgfx", "sdlimage", "sdlttf", "sdlmixer"]

if not sys.argv or sys.argv[0] not in (f"{sys.prefix}\\Scripts\\libmge.exe", f"{sys.prefix}\\Scripts\\libmge"):
    from . import sdl2
    from . import sdlgfx
    from . import sdlimage
    from . import sdlttf
    from . import sdlmixer
