#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Test tool to run a program with various Pythons. """

from barkMatterPy.PythonVersions import getSupportedPythonVersions
from barkMatterPy.utils.Execution import check_output
from barkMatterPy.utils.InstalledPythons import findPythons


def findAllPythons():
    for python_version in getSupportedPythonVersions():
        for python in findPythons(python_version):
            yield python, python_version


def executeWithInstalledPython(python, args):
    return check_output([python.getPythonExe()] + args)



