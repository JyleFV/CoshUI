import warnings
import sys

class CoshUIError(Exception):
    __module__ = "builtins"

class CoshMLError(Exception):
    __module__ = "builtins"

class CoshUIWarning(UserWarning):
    pass

def _coshui_warning_handler(message, category, filename, lineno, file=None, line=None):
    if issubclass(category, CoshUIWarning):
        print(f"\033[93mCoshUIWarning: {message}\033[0m")  # yellow
    else:
        warnings._showwarning_orig(message, category, filename, lineno, file, line)

def _coshui_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, CoshUIError):
        print(f"\033[91mCoshUIError: {exc_value}\033[0m")  # red
    elif issubclass(exc_type, CoshMLError):
        print(f"\033[95mCoshMLError: {exc_value}\033[0m")  # light purple
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

def warn(message: str):
    warnings.warn(message, CoshUIWarning, stacklevel=2)

warnings.showwarning = _coshui_warning_handler
sys.excepthook = _coshui_exception_handler