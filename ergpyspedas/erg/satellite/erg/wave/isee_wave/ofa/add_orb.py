from datetime import datetime
from typing import Dict, Sequence, Union

from pyspedas.erg.satellite.erg.orb.orb import orb
from pyspedas.utilities.tnames import tnames
from pytplot import options, split_vec

from ..load.orb_predict import orb_predict
from ..options.orbital_info_option import OrbitalInfoName
from ..utils.get_uname_passwd import get_uname_passwd


def add_orb(
    mlt: bool = True,
    mlat: bool = True,
    alt: bool = True,
    l: bool = True,
    trange: Union[Sequence[str], Sequence[float], Sequence[datetime]] = [
        "2017-04-01/00:00:00",
        "2017-04-01/23:59:59",
    ],
    no_update: bool = False,
) -> Dict[OrbitalInfoName, str]:
    """Try add orb data and return actual tplot name of the orb data"""
    # Get username and password
    uname, passwd = get_uname_passwd()
    # Load orb
    orb(trange=trange, no_update=no_update, uname=uname, passwd=passwd)
    prefix_orbit = "erg_orb_l2_"
    if not tnames(prefix_orbit + "pos_blocal_mag"):
        orb_predict(trange=trange, no_download=no_update, uname=uname, passwd=passwd)
        prefix_orbit = "erg_orb_pre_l2_"
    if not tnames(prefix_orbit + "pos_blocal_mag"):
        return {}

    # Prepare tplot
    split_vec(prefix_orbit + "pos_rmlatmlt")
    split_vec(prefix_orbit + "pos_Lm")
    options(prefix_orbit + "pos_Lm_x", "ytitle", r"L")
    options(prefix_orbit + "pos_rmlatmlt_x", "ytitle", r"$R_E$")
    options(prefix_orbit + "pos_rmlatmlt_y", "ytitle", r"MLAT")
    options(prefix_orbit + "pos_rmlatmlt_z", "ytitle", r"MLT")

    # Return tplot name for each data
    orb_dict: Dict[OrbitalInfoName, str] = {}
    if l:
        orb_dict[OrbitalInfoName.lshell] = prefix_orbit + "pos_Lm_x"
    if alt:
        orb_dict[OrbitalInfoName.alt] = prefix_orbit + "pos_rmlatmlt_x"
    if mlat:
        orb_dict[OrbitalInfoName.mlat] = prefix_orbit + "pos_rmlatmlt_y"
    if mlt:
        orb_dict[OrbitalInfoName.mlt] = prefix_orbit + "pos_rmlatmlt_z"

    return orb_dict


if __name__ == "__main__":
    orb_dict = add_orb()
    print(orb_dict)
