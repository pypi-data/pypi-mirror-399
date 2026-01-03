from ..Log import Log, ConsoleColors
from ..Version import __version__, __projectName__, __versionDisplay__
import os

__all__ = ['version', 'about', 'path']

def version():
    Log(f"{__projectName__}  →  {ConsoleColors.Green}{__version__}", ConsoleColors.Reset)

def about():
    Log("LibMGE", ConsoleColors.Reset)
    Log("")

    info = [
        ("Description", "A powerful 2D graphics and game development library"),
        ("Version", __versionDisplay__),
        ("Python", ">= 3.5"),
        ("License", "Zlib"),
        ("Author", "Lucas Guimarães"),
        ("Organization", "Monumental Games"),
    ]

    links = [
        ("Website", "https://libmge.org/"),
        ("Documentation", "https://docs.libmge.org/"),
        ("Source Code", "https://github.com/MonumentalGames/LibMGE"),
        ("Bug Tracker", "https://github.com/MonumentalGames/LibMGE/issues"),
    ]

    Log("  Info:", ConsoleColors.Reset)
    for label, value in info:
        Log(f"    {label:<13} →  {ConsoleColors.Green}{value}", ConsoleColors.Reset)

    Log("\n  Links:", ConsoleColors.Reset)
    for label, value in links:
        Log(f"    {label:<13} →  {ConsoleColors.Cyan}{value}", ConsoleColors.Reset)

    Log("\n  Dependencies:", ConsoleColors.Reset)
    Log(f"    SDL2, SDL2_image, SDL2_mixer, SDL2_ttf, SDL2_gfx", ConsoleColors.Reset)
    Log("")

def path():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    Log("LibMGE Paths:", ConsoleColors.Reset)
    Log(f"  Base        →  {ConsoleColors.Green}{base}", ConsoleColors.Reset)
