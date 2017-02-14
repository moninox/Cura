#!env python
import os
import sys
import subprocess

# A quick Python implementation of unix 'where' command.
def where(exeName):
    searchPath = os.getenv("PATH")
    paths = searchPath.split(";" if sys.platform == "win32" else ":")
    for path in paths:
        candidatePath = os.path.join(path, exeName)
        if os.path.exists(candidatePath):
            return candidatePath
    return None

def findModules(path):
    result = []
    for entry in os.scandir(path):
        if entry.is_dir() and os.path.exists(os.path.join(path, entry.name, "__init__.py")):
            result.append(entry.name)
    return result

def main():
    if sys.platform == "win32":
        os.putenv("MYPYPATH", r".;.\plugins;.\plugins\VersionUpgrade;..\Uranium\;..\Uranium\stubs\\" )
    else:
        os.putenv("MYPYPATH", r".:./plugins:./plugins/VersionUpgrade:../Uranium/:../Uranium\stubs/")

    # Mypy really needs to be run via its Python script otherwise it can't find its data files.
    mypyExe = where("mypy.bat" if sys.platform == "win32" else "mypy")
    mypyModule = os.path.join(os.path.dirname(mypyExe), "mypy")

    plugins = findModules("plugins")
    plugins.sort()

    mods = ["cura"] + plugins + findModules("plugins/VersionUpgrade")

    for mod in mods:
        print("------------- Checking module {mod}".format(**locals()))
        result = subprocess.run([sys.executable, mypyModule, "-p", mod])
        if result.returncode != 0:
            print("""
    Module {mod} failed checking. :(
    """.format(**locals()))
            break
    else:
        print("""

    Done checking. All is good.
    """)
    return 0
sys.exit(main())
