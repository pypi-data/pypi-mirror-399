from ..Log import Log, LogError, ConsoleColors
from ..Version import __version__, __versionData__
from ._sdl_introspection import _print_deps
import os
import json
import urllib.request
from zipfile import ZipFile
from tempfile import gettempdir
from platform import system

__all__ = ['depsInstall', 'depsVersions', 'depsCheck']

def _list_zip_dlls(zip_path):
    with ZipFile(zip_path, "r") as zip_ref:
        return {
            os.path.basename(f)
            for f in zip_ref.namelist()
            if f.lower().endswith(".dll")
        }

def _list_conflicting_dlls(target_path, zip_dlls):
    if not os.path.exists(target_path):
        return []

    existing = set(os.listdir(target_path))
    return list(existing & zip_dlls)

def _remove_conflicting_dlls(path, dlls):
    for dll in dlls:
        try:
            os.remove(os.path.join(path, dll))
        except PermissionError:
            LogError(f"Cannot remove {dll} (file in use)")
            return False
    return True

def depsInstall(target="global"):
    Log("Checking compatibility...", ConsoleColors.Reset)

    try:
        with urllib.request.urlopen(
            f"https://deps.libmge.org/?version={__version__}"
            f"&release={__versionData__['phase']}"
            f"&os={system().lower()}"
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
    except:
        Log("")
        LogError("Compatibility check failed")
        Log("Installation aborted", ConsoleColors.Red)
        return

    if "error" in data:
        Log("")
        LogError(data["error"]["message"])
        Log("Installation aborted", ConsoleColors.Red)
        return

    url = data["download"]
    temp_zip_path = os.path.join(gettempdir(), "libmge_deps.zip")

    extract_path = (
        os.getcwd()
        if target == "cwd"
        else os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    )

    def download_with_progress(url, filename):
        Log("\rDownloading dependencies...", ConsoleColors.Reset, "")
        with urllib.request.urlopen(url) as response:
            total = int(response.getheader("Content-Length"))
            downloaded = 0

            with open(filename, "wb") as out:
                while True:
                    chunk = response.read(1024)
                    if not chunk:
                        break
                    out.write(chunk)
                    downloaded += len(chunk)

                    percent = downloaded * 100 // total
                    Log(
                        f"\rDownloading ({ConsoleColors.Yellow}{percent}%{ConsoleColors.Reset}) "
                        f"{downloaded // 1024}KB / {total // 1024}KB",
                        ConsoleColors.Reset,
                        ""
                    )

        Log("\nDownload complete", ConsoleColors.Green)

    try:
        download_with_progress(url, temp_zip_path)
    except:
        Log("")
        LogError("Failed to download dependencies")
        Log("Installation aborted", ConsoleColors.Red)
        return

    zip_dlls = _list_zip_dlls(temp_zip_path)
    conflicts = _list_conflicting_dlls(extract_path, zip_dlls)

    if conflicts:
        if target == "cwd":
            Log("\nExisting dependencies detected.", ConsoleColors.Yellow)
            choice = input("Remove old files before installation? (y/N): ").strip().lower()

            if choice == "y":
                if not _remove_conflicting_dlls(extract_path, conflicts):
                    Log("Close applications using these files and try again.", ConsoleColors.Red)
                    os.remove(temp_zip_path)
                    return
        else:
            if not _remove_conflicting_dlls(extract_path, conflicts):
                Log("Close applications using LibMGE and try again.", ConsoleColors.Red)
                os.remove(temp_zip_path)
                return

    Log("Extracting files...", ConsoleColors.Reset)
    try:
        with ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
    except:
        os.remove(temp_zip_path)
        LogError("Failed to extract files")
        Log("Installation aborted", ConsoleColors.Red)
        return

    os.remove(temp_zip_path)

    if target == "cwd":
        Log(f"Dependencies installed at: {ConsoleColors.Cyan}{extract_path}", ConsoleColors.Reset)

    Log("Successfully installed", ConsoleColors.Green)

def depsVersions():
    try:
        from .._sdl._dll_loader import nullFunction
    except:
        Log(f"\n{ConsoleColors.Cyan}Tip:{ConsoleColors.Reset} Run '{ConsoleColors.Bold}LibMGE deps install{ConsoleColors.Reset}' to update missing or outdated dependencies.", ConsoleColors.Reset)
    else:
        from ..Platform import Platform
        Log(f"SDL       →  {ConsoleColors.Green}{Platform.SDL.SDL_version}", ConsoleColors.Reset)
        Log(f"SDLGFX    →  {ConsoleColors.Green}{Platform.SDL.SDLGFX_version}", ConsoleColors.Reset)
        Log(f"SDLIMAGE  →  {ConsoleColors.Green}{Platform.SDL.SDLIMAGE_version}", ConsoleColors.Reset)
        Log(f"SDLTTF    →  {ConsoleColors.Green}{Platform.SDL.SDLTTF_version}", ConsoleColors.Reset)
        Log(f"SDLMIXER  →  {ConsoleColors.Green}{Platform.SDL.SDLMIXER_version}", ConsoleColors.Reset)
        Log(f"{ConsoleColors.Cyan}Tip:{ConsoleColors.Reset} Run '{ConsoleColors.Bold}LibMGE deps install{ConsoleColors.Reset}' to update missing or outdated dependencies.", ConsoleColors.Reset)

def depsCheck():
    Log("Dependencies:", ConsoleColors.Reset)
    _print_deps(False)
    Log("")
