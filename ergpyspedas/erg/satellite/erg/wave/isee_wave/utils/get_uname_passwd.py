from typing import Tuple

from pyspedas.utilities.tnames import tnames
from pytplot import get_data


def get_uname_passwd() -> Tuple[str, str]:
    """Convenient function to get uname and passwd after login"""
    if tnames("uname") and tnames("passwd"):
        uname = get_data("uname").y[0]  # type: ignore
        passwd = get_data("passwd").y[0]  # type: ignore
    else:
        uname = ""
        passwd = ""
    return (uname, passwd)
