from typing import Tuple

from pyspedas.utilities.tnames import tnames
from pytplot import get_data


def get_uname_passwd() -> Tuple[str, str]:
    if tnames("uname"):
        uname1 = get_data("uname").y[0]
        passwd1 = get_data("passwd").y[0]
    else:
        uname1 = ""
        passwd1 = ""
    return (uname1, passwd1)
