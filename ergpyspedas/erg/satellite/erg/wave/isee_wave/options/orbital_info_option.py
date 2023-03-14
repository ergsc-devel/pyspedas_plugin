from dataclasses import dataclass
from enum import Enum

# Default options
_orbital_information_option_dict = {
    "mlt": True,
    "mlat": True,
    "altitude": True,
    "lshell": True,
}


@dataclass
class OrbitalInfoOption:
    mlt: bool = True
    mlat: bool = True
    alt: bool = True
    lshell: bool = True


class OrbitalInfoName(Enum):
    mlt = "mlt"
    mlat = "mlat"
    alt = "alt"
    lshell = "lshell"
