from ctypes import Structure, c_int, c_char_p, POINTER as _P
from ._dll_loader import IMAGEFunc
from .sdl2 import SDL_version, SDL_RWops, SDL_Surface, SDL_Texture, SDL_Renderer

class IMG_Animation(Structure):
    _fields_ = [("w", c_int), ("h", c_int), ("count", c_int), ("frames", _P(_P(SDL_Surface))), ("delays", _P(c_int))]

def IMG_Linked_Version() -> SDL_version: return IMAGEFunc("IMG_Linked_Version", None, _P(SDL_version))()

def IMG_Init(flags=0) -> int: return IMAGEFunc("IMG_Init", [c_int], c_int)(flags)
def IMG_Quit(): IMAGEFunc("IMG_Quit")()

def IMG_Load(file: str) -> SDL_Surface: return IMAGEFunc("IMG_Load", [c_char_p], _P(SDL_Surface))(file.encode())
def IMG_Load_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_Load_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadTexture(renderer: SDL_Renderer, file: str) -> SDL_Texture: return IMAGEFunc("IMG_LoadTexture", [_P(SDL_Renderer), c_char_p], _P(SDL_Texture))(renderer, file.encode())

def IMG_isAVIF(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isAVIF", [_P(SDL_RWops)], c_int)(src))
def IMG_isICO(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isICO", [_P(SDL_RWops)], c_int)(src))
def IMG_isCUR(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isCUR", [_P(SDL_RWops)], c_int)(src))
def IMG_isBMP(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isBMP", [_P(SDL_RWops)], c_int)(src))
def IMG_isGIF(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isGIF", [_P(SDL_RWops)], c_int)(src))
def IMG_isJPG(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isJPG", [_P(SDL_RWops)], c_int)(src))
def IMG_isJXL(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isJXL", [_P(SDL_RWops)], c_int)(src))
def IMG_isLBM(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isLBM", [_P(SDL_RWops)], c_int)(src))
def IMG_isPCX(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isPCX", [_P(SDL_RWops)], c_int)(src))
def IMG_isPNG(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isPNG", [_P(SDL_RWops)], c_int)(src))
def IMG_isPNM(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isPNM", [_P(SDL_RWops)], c_int)(src))
def IMG_isSVG(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isSVG", [_P(SDL_RWops)], c_int)(src))
def IMG_isQOI(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isQOI", [_P(SDL_RWops)], c_int)(src))
def IMG_isTIF(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isTIF", [_P(SDL_RWops)], c_int)(src))
def IMG_isXCF(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isXCF", [_P(SDL_RWops)], c_int)(src))
def IMG_isXPM(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isXPM", [_P(SDL_RWops)], c_int)(src))
def IMG_isXV(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isXV", [_P(SDL_RWops)], c_int)(src))
def IMG_isWEBP(src: SDL_RWops) -> bool: return bool(IMAGEFunc("IMG_isWEBP", [_P(SDL_RWops)], c_int)(src))

def IMG_LoadAVIF_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadAVIF_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadICO_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadICO_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadCUR_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadCUR_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadBMP_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadBMP_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadGIF_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadGIF_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadJPG_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadJPG_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadJXL_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadJXL_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadLBM_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadLBM_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadPCX_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadPCX_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadPNG_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadPNG_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadPNM_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadPNM_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadSVG_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadSVG_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadQOI_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadQOI_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadTGA_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadTGA_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadTIF_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadTIF_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadXCF_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadXCF_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadXPM_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadXPM_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadXV_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadXV_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)
def IMG_LoadWEBP_RW(src: SDL_RWops) -> SDL_Surface: return IMAGEFunc("IMG_LoadWEBP_RW", [_P(SDL_RWops)], _P(SDL_Surface))(src)

def IMG_LoadSizedSVG_RW(src: SDL_RWops, width: int, height: int) -> SDL_Surface: return IMAGEFunc("IMG_LoadSizedSVG_RW", [_P(SDL_RWops), c_int, c_int], _P(SDL_Surface))(src, width, height)

def IMG_ReadXPMFromArray(xpm: str) -> SDL_Surface: return IMAGEFunc("IMG_ReadXPMFromArray", [_P(c_char_p)], _P(SDL_Surface))(xpm.encode())
def IMG_ReadXPMFromArrayToRGB888(xpm: str) -> SDL_Surface: return IMAGEFunc("IMG_ReadXPMFromArrayToRGB888", [_P(c_char_p)], _P(SDL_Surface))(xpm.encode())

def IMG_SavePNG(surface: SDL_Surface, file: str): return IMAGEFunc("IMG_SavePNG", [_P(SDL_Surface), c_char_p], c_int)(surface, file.encode())
def IMG_SaveJPG(surface: SDL_Surface, file: str, quality: int): return IMAGEFunc("IMG_SaveJPG", [_P(SDL_Surface), c_char_p, c_int], c_int)(surface, file.encode(), quality)
# NOTE: Not available in official macOS binaries

def IMG_LoadAnimation(file: str) -> IMG_Animation: return IMAGEFunc("IMG_LoadAnimation", [c_char_p], _P(IMG_Animation))(file.encode())
def IMG_LoadAnimation_RW(src: SDL_RWops) -> IMG_Animation: return IMAGEFunc("IMG_LoadAnimation_RW", [_P(SDL_RWops), c_int], _P(IMG_Animation))(src, 1)
def IMG_FreeAnimation(anim: IMG_Animation): IMAGEFunc("IMG_FreeAnimation", [_P(IMG_Animation)])(anim)
