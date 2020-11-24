"""
Module with bool utilities.
"""
import os
from typing import Any


def env(key: str, default: bool = None):
    return to_bool(os.getenv(key, default))


def to_bool(obj: Any):
    """
       Converts 'something' to boolean. Raises ValueError for invalid obj
           Possible True  objects: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False objects: 0, False, None, "", "0", "faLse", "no", "n", "f", ...
       Reference: https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python
    """

    obj_str = str(obj).lower()
    if obj_str in ("yes", "y", "true", "t", "1", "on"):
        return True
    elif obj_str in ("no", "n", "false", "f", "0", "off", "", "none"):
        return False
    else:
        raise ValueError('Invalid value for boolean conversion: {}'.format(obj))
