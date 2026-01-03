from ..Log import Log, ConsoleColors
import sys

from .deps import *
from .doctor import *
from .info import *
from .help import *

__all__ = ["main"]

def _not_command_found():
    Log("Unknown command.", ConsoleColors.Yellow)
    Log(f"Run '{ConsoleColors.Bold}LibMGE help{ConsoleColors.Reset}' to see available commands.\n", ConsoleColors.Reset)

def main():
    if len(sys.argv) < 2:
        _not_command_found()
        return

    command = sys.argv[1].lower()

    if command == "version":
        version()

    elif command == "deps" and len(sys.argv) >= 3:
        subcommand = sys.argv[2].lower()

        if subcommand == "install":
            target = "global"

            if len(sys.argv) >= 4:
                flag = sys.argv[3].lower()
                if flag in ("--local", "--cwd"):
                    target = "cwd"

            depsInstall(target=target)

        elif subcommand == "versions":
            depsVersions()

        elif subcommand == "check":
            depsCheck()

        else:
            _not_command_found()

    elif command == "help":
        help()

    elif command == "doctor":
        doctor()

    elif command == "path":
        path()

    elif command == "about":
        about()

    else:
        _not_command_found()
