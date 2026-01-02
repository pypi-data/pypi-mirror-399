from ctypes import c_int, POINTER as _P, Array
from ._dll_loader import GFXFunc
from .sdl2 import Uint8, Sint16, SDL_Renderer, SDL_Surface

def pixelRGBA(renderer: SDL_Renderer, x: int, y: int, r: int, g: int, b: int, a: int):
    return GFXFunc("pixelRGBA", [_P(SDL_Renderer), Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, r, g, b, a)

def rectangleRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int):
    return GFXFunc("rectangleRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x1, y1, x2, y2, r, g, b, a)
def roundedRectangleRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, rad: int, r: int, g: int, b: int, a: int):
    return GFXFunc("roundedRectangleRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x1, y1, x2, y2, rad, r, g, b, a)

def boxRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int):
    return GFXFunc("boxRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x1, y1, x2, y2, r, g, b, a)
def roundedBoxRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, rad: int, r: int, g: int, b: int, a: int):
    return GFXFunc("roundedBoxRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x1, y1, x2, y2, rad, r, g, b, a)

def lineRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int):
    return GFXFunc("lineRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x1, y1, x2, y2, r, g, b, a)
def aalineRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int):
    return GFXFunc("aalineRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x1, y1, x2, y2, r, g, b, a)
def thickLineRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, width: int, r: int, g: int, b: int, a: int):
    return GFXFunc("thickLineRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x1, y1, x2, y2, width, r, g, b, a)

def circleRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, r: int, g: int, b: int, a: int):
    return GFXFunc("circleRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rad, r, g, b, a)
def arcRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int):
    return GFXFunc("arcRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rad, start, end, r, g, b, a)
def aacircleRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, r: int, g: int, b: int, a: int):
    return GFXFunc("aacircleRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rad, r, g, b, a)
def filledCircleRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, r: int, g: int, b: int, a: int):
    return GFXFunc("filledCircleRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rad, r, g, b, a)

def ellipseRGBA(renderer: SDL_Renderer, x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int):
    return GFXFunc("ellipseRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rx, ry, r, g, b, a)
def aaellipseRGBA(renderer: SDL_Renderer, x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int):
    return GFXFunc("aaellipseRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rx, ry, r, g, b, a)
def filledEllipseRGBA(renderer: SDL_Renderer, x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int):
    return GFXFunc("filledEllipseRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rx, ry, r, g, b, a)

def pieRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int):
    return GFXFunc("pieRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rad, start, end, r, g, b, a)
def filledPieRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int):
    return GFXFunc("filledPieRGBA", [_P(SDL_Renderer), Sint16, Sint16, Sint16, Sint16, Sint16, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, x, y, rad, start, end, r, g, b, a)

def polygonRGBA(renderer: SDL_Renderer, vx: Array, vy: Array, n: int, r: int, g: int, b: int, a: int):
    return GFXFunc("polygonRGBA", [_P(SDL_Renderer), _P(Sint16), _P(Sint16), c_int, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, vx, vy, n, r, g, b, a)
def aapolygonRGBA(renderer: SDL_Renderer, vx: Array, vy: Array, n: int, r: int, g: int, b: int, a: int):
    return GFXFunc("aapolygonRGBA", [_P(SDL_Renderer), _P(Sint16), _P(Sint16), c_int, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, vx, vy, n, r, g, b, a)
def filledPolygonRGBA(renderer: SDL_Renderer, vx: Array, vy: Array, n: int, r: int, g: int, b: int, a: int):
    return GFXFunc("filledPolygonRGBA", [_P(SDL_Renderer), _P(Sint16), _P(Sint16), c_int, Uint8, Uint8, Uint8, Uint8], c_int)(renderer, vx, vy, n, r, g, b, a)
def texturedPolygon(renderer: SDL_Renderer, vx: Array, vy: Array, n: int, texture: SDL_Surface, texture_dx: int, texture_dy: int):
    return GFXFunc("texturedPolygon", [_P(SDL_Renderer), _P(Sint16), _P(Sint16), c_int, _P(SDL_Surface), c_int, c_int], c_int)(renderer, vx, vy, n, texture, texture_dx, texture_dy)

def rotateSurface90Degrees(src: SDL_Surface, num: int) -> SDL_Surface:
    return GFXFunc("rotateSurface90Degrees", [_P(SDL_Surface), c_int], _P(SDL_Surface))(src, num)
