from ..Log import Log, ConsoleColors

__all__ = ['help']

def help():
    Log("Usage:", ConsoleColors.Reset)
    Log("")
    Log("  LibMGE version         →  Show LibMGE version", ConsoleColors.Reset)
    Log("  LibMGE doctor          →  Diagnose environment and dependencies", ConsoleColors.Reset)
    Log("  LibMGE deps install    →  Install required dependencies", ConsoleColors.Reset)
    Log("  LibMGE deps check      →  Check dependency status", ConsoleColors.Reset)
    Log("  LibMGE path            →  Show LibMGE base path", ConsoleColors.Reset)
    Log("  LibMGE about           →  Show information about LibMGE", ConsoleColors.Reset)
    Log("  LibMGE help            →  Show this help message", ConsoleColors.Reset)
    Log("")
    Log(f"{ConsoleColors.Cyan}Tip:{ConsoleColors.Reset} Run '{ConsoleColors.Bold}LibMGE doctor{ConsoleColors.Reset}' if something is not working.", ConsoleColors.Reset)