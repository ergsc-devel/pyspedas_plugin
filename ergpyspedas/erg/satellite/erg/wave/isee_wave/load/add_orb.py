from typing import Dict, Optional

from pyspedas.erg.satellite.erg.orb.orb import orb
from pyspedas.utilities.tnames import tnames
from pytplot import options, split_vec

from ..options.options import OrbitalInfoName
from ..utils.get_uname_passwd import get_uname_passwd
from .orb_predict import orb_predict


def add_orb(
    mlt=True,
    mlat=True,
    alt=True,
    l=True,
    trange=["2017-04-01/00:00:00", "2017-04-01/23:59:59"],
    no_update=False,
) -> Dict[OrbitalInfoName, str]:
    # Get username and password
    uname, passwd = get_uname_passwd()
    # load orb
    orb(trange=trange, no_update=no_update, uname=uname, passwd=passwd)
    prefix_orbit = "erg_orb_l2_"
    if not tnames(prefix_orbit + "pos_blocal_mag"):
        # TODO: I need to check if download is done
        orb_predict(trange=trange, no_download=no_update, uname=uname, passwd=passwd)
        prefix_orbit = "erg_orb_pre_l2_"
    # TODO: What if data is None
    # if not tnames(prefix_orbit + "pos_blocal_mag"):
    #     return

    # prepare tplot
    split_vec(prefix_orbit + "pos_rmlatmlt")
    split_vec(prefix_orbit + "pos_Lm")
    options(prefix_orbit + "pos_Lm_x", "ytitle", r"L")
    options(prefix_orbit + "pos_rmlatmlt_x", "ytitle", r"$R_E$")
    options(prefix_orbit + "pos_rmlatmlt_y", "ytitle", r"MLAT")
    options(prefix_orbit + "pos_rmlatmlt_z", "ytitle", r"MLT")

    var_label_dict: Dict[OrbitalInfoName, str] = {}
    if l:
        var_label_dict[OrbitalInfoName.l] = prefix_orbit + "pos_Lm_x"
    if alt:
        var_label_dict[OrbitalInfoName.alt] = prefix_orbit + "pos_rmlatmlt_x"
    if mlat:
        var_label_dict[OrbitalInfoName.mlat] = prefix_orbit + "pos_rmlatmlt_y"
    if mlt:
        var_label_dict[OrbitalInfoName.mlt] = prefix_orbit + "pos_rmlatmlt_z"

    return var_label_dict


if __name__ == "__main__":
    var_label_dict = add_orb()
    print(var_label_dict)
