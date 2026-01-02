#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Test tool to run a program with various Pythons. """

from JACK.PythonVersions import getSupportedPythonVersions
from JACK.utils.Execution import check_output
from JACK.utils.InstalledPythons import findPythons


def findAllPythons():
    for python_version in getSupportedPythonVersions():
        for python in findPythons(python_version):
            yield python, python_version


def executeWithInstalledPython(python, args):
    return check_output([python.getPythonExe()] + args)



