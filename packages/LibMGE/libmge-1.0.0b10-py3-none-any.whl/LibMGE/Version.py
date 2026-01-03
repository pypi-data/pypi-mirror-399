
__versionList__ = [1, 0, 0, 10]  # Major, Minor, Patch, Build

__versionData__ = {
    "major": __versionList__[0],
    "minor": __versionList__[1],
    "patch": __versionList__[2],
    "build": __versionList__[3],
    "phase": "b"  # 'a' (alpha), 'b' (beta), '' (stable)
}

# Generates a version in PEP 440 format
if __versionData__['phase'] and __versionData__['build']:
    __version__ = f"{__versionData__['major']}.{__versionData__['minor']}.{__versionData__['patch']}{__versionData__['phase']}{__versionData__['build']}"
else:
    __version__ = f"{__versionData__['major']}.{__versionData__['minor']}.{__versionData__['patch']}"

# Phase mapping to readable name
__phaseNames__ = {
    'a': 'Alpha',
    'b': 'Beta',
    '': 'Stable'
}

# Project name with phase
__projectName__ = __phaseNames__.get(__versionData__['phase'], 'Stable')
if __projectName__ != 'Stable':
    __projectName__ = f"{__projectName__}-LibMGE"
else:
    __projectName__ = "LibMGE"
