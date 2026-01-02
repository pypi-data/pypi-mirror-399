#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" For enhanced bug reporting, these exceptions should be used.

They ideally should point out what it ought to take for reproducing the
issue when output.

"""


class OxNJACErrorBase(Exception):
    pass


class OxNJACNodeError(OxNJACErrorBase):
    # Try to output more information about nodes passed.
    def __str__(self):
        try:
            from barkMatterPy.code_generation.Indentation import indented

            parts = [""]

            for arg in self.args:  # false alarm, pylint: disable=I0021,not-an-iterable
                if hasattr(arg, "asXmlText"):
                    parts.append(indented("\n%s\n" % arg.asXmlText()))
                else:
                    parts.append(str(arg))

            parts.append("")
            parts.append("The above information should be included in a bug report.")

            return "\n".join(parts)
        except Exception as e:  # Catch all the things, pylint: disable=broad-except
            return "<OxNJACNodeError failed with %r>" % e


class OxNJACOptimizationError(OxNJACNodeError):
    pass


class OxNJACAssumptionError(AssertionError):
    pass


class OxNJACCodeDeficit(OxNJACErrorBase):
    pass


class OxNJACNodeDesignError(Exception):
    pass


class OxNJACForbiddenImportEncounter(Exception):
    """This import was an error to attempt and include it."""


class CodeTooComplexCode(Exception):
    """The code of the module is too complex.

    It cannot be compiled, with recursive code, and therefore the bytecode
    should be used instead.

    Example of this is "idnadata".
    """


class OxNJACNotYetSupported(Exception):
    """A feature is not yet supported, please help adding it."""


class OxNJACForbiddenDLLEncounter(Exception):
    """This DLL is not allowed to be included."""


class OxNJACSyntaxError(Exception):
    """The code cannot be read due to SyntaxError"""



