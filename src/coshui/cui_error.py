import warnings
import sys

class CoshUIError:
    class Main(Exception):
        __module__ = "builtins"

    class CoshML(Exception):
        __module__ = "builtins"

    class Warning(UserWarning):
        pass

    @staticmethod
    def warn(message: str):
        warnings.warn(
            message,
            CoshUIError.Warning,
            stacklevel=2
        )

_original_showwarning = warnings.showwarning

def _coshui_warning_handler(message, category, filename, lineno, file=None, line=None):
    if issubclass(category, CoshUIError.Warning):
        print(f"\033[93mCoshUIWarning: {message}\033[0m")
    else:
        _original_showwarning(message, category, filename, lineno, file, line)

warnings.showwarning = _coshui_warning_handler