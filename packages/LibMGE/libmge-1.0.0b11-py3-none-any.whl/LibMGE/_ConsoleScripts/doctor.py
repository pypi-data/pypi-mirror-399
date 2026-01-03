from ..Log import Log, ConsoleColors
from ..Version import __version__, __projectName__
from ._sdl_introspection import _print_deps
from platform import system, python_version

__all__ = ['doctor']

def doctor():
    Log("LibMGE Doctor:", ConsoleColors.Reset)

    system_info = [
        ("System", system()),
        ("Python", python_version()),
        (__projectName__, __version__)
    ]

    Log("\n  Ambient:", ConsoleColors.Reset)

    for label, value in system_info:
        Log(f"    {label:<11} →  {ConsoleColors.Green}{value}", ConsoleColors.Reset)

    _print_deps(indent="    ")
    Log("")
