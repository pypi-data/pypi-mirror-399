#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Deprecated trio plugin.
"""

from barkMatterPy.plugins.PluginBase import OxNJACPluginBase


class OxNJACPluginTrio(OxNJACPluginBase):
    plugin_name = "trio"
    plugin_desc = "Deprecated, was once required by the 'trio' package"
    plugin_category = "package-support,obsolete"

    @classmethod
    def isDeprecated(cls):
        return True



