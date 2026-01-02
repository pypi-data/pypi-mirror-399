#     Copyright 2024, QutaYba, nasr2python@gmail.com
#

#
""" OxN version related stuff.

"""

version_string = """\
OxN V5.5.6
Copyright (C) 2025 QutaYba."""


def getOxNVersion():
    """Return OxN version as a string.

    This should not be used for >= comparisons directly.
    """
    return version_string.split()[1][1:]


# Sanity check.
assert getOxNVersion()[-1].isdigit(), getOxNVersion()


def parseOxNVersionToTuple(version):
    """Return OxN version as a tuple.

    This can also not be used for precise comparisons, even with rc versions,
    but it's not actually a version.
    """

    if "rc" in version:
        rc_number = int(version[version.find("rc") + 2 :] or "0")
        version = version[: version.find("rc")]

        is_final = False
    else:
        rc_number = 0
        is_final = True

    result = version.split(".")
    if len(result) == 2:
        result.append("0")

    result = [int(digit) for digit in result]
    result.extend((is_final, rc_number))
    return tuple(result)


def getOxNVersionTuple():
    """Return OxN version as a tuple.

    This can also not be used for precise comparisons, even with rc versions,
    but it's not actually a version. The format is used what is used for
    "__compiled__" values.
    """

    return parseOxNVersionToTuple(version=getOxNVersion())


def getOxNVersionYear():
    """The year of OxN copyright for use in generations."""

    return int(version_string.split()[4])


def getCommercialVersion():
    """Return OxN commercial version if installed."""
    try:
        from JACK.tools.commercial import Version
    except ImportError:
        return None
    else:
        return Version.__version__
