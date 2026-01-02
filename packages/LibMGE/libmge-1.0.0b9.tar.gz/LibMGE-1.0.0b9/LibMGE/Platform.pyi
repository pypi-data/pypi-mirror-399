from typing import Optional

__all__ = ["Platform"]

class Platform:
    system:str
    system_version:int
    python_version:str
    drivers:list[RenderDriver]

    class SDL:
        SDL_version_list:list[int, int, int]
        SDL_version:str

        SDLGFX_version_list:list[int, int, int]
        SDLGFX_version:str

        SDLIMAGE_version_list:list[int, int, int]
        SDLIMAGE_version:str

        SDLMIXER_version_list:list[int, int, int]
        SDLMIXER_version:str

        SDLTTF_version_list:list[int, int, int]
        SDLTTF_version:str

class RenderDriver:
    id: Optional[int]
    name: Optional[str]
    hardware: Optional[bool]
    software: Optional[bool]
    bufferTexture: Optional[bool]
    targetTexture: Optional[bool]
