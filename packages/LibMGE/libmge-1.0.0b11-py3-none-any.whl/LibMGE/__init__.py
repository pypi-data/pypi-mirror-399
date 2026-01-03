"""
LibMGE is an open-source library created for the development of 2D programs and games in Python.
Our goal is to provide a simple and accessible solution, allowing developers,
from beginners to professionals, to rely on an efficient tool for creating
games and graphical interfaces.

Whether for prototyping or full game development, LibMGE was designed to make the process more
intuitive and faster without compromising quality.

zlib License

Copyright (c) 2024 Lucas Guimarães

This software is provided 'as-is', without any express or implied
warranty.  In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
"""
import sys

if not sys.argv or sys.argv[0] not in (f"{sys.prefix}\\Scripts\\libmge.exe", f"{sys.prefix}\\Scripts\\libmge"):
    from .Common import *
    from .Log import *
    from .Audio import Music, Sound
    from .Platform import Platform
    from .Constants import *
    from .Collisions import collision, rayCast
    from .CollisionBounds import CollisionBounds
    from .Camera import Camera
    from .Window import Window, CreateGlWindow, InternalWindow
    from .Monitors import Monitors, Monitor
    from .Text import ObjectText, ObjectInputTextLine, ObjectInputPassLine, ObjectInputTextBox
    from .Object2D import Object2D
    from .Line import Line
    from .Material import Material
    from .Texture import Texture
    from .Image import *
    from .Color import Color
    from .Mesh import Mesh2D, CreateMeshPlane
    from .Mouse import *
    from .Keyboard import keyboard
    from .GameController import *
    from .Button import *
    from .Time import *
    from .Version import __version__, __versionData__, __versionList__, __projectName__

    print(f"{__projectName__} {__version__} (SDL {Platform.SDL.SDL_version} | Python {Platform.python_version})")
