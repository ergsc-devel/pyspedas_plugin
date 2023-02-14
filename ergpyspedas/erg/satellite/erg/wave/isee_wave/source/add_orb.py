from typing import List

from pyspedas.erg.satellite.erg.orb.orb import orb
from pyspedas.utilities.tnames import tnames
from pytplot import options, split_vec


def add_orb(
    mlt=True,
    mlat=True,
    alt=True,
    l=True,
    trange=["2017-04-01/00:00:00", "2017-04-01/23:59:59"],
    no_update=False,
) -> List[str]:
    # TODO: imcomplete

    # TODO: data is reproduced but var_label_list must be passed as arguments to tplot
    # therefore written this way so far

    # load orb
    orb(trange=trange, no_update=no_update)

    prefix_orbit = "erg_orb_l2_"
    if not tnames(prefix_orbit + "pos_blocal_mag"):
        # TODO: orb_predict is not in python but not used here
        # orb_predict()
        prefix_orbit = "erg_orb_pre_l2_"

    # prepare tplot
    split_vec(prefix_orbit + "pos_rmlatmlt")
    split_vec(prefix_orbit + "pos_Lm")
    options(prefix_orbit + "pos_Lm_x", "ytitle", r"L")
    options(prefix_orbit + "pos_rmlatmlt_x", "ytitle", r"$R_E$")
    options(prefix_orbit + "pos_rmlatmlt_y", "ytitle", r"MLAT")
    options(prefix_orbit + "pos_rmlatmlt_z", "ytitle", r"MLT")

    var_label_list = []
    if l:
        var_label_list += [prefix_orbit + "pos_Lm_x"]
    if alt:
        var_label_list += [prefix_orbit + "pos_rmlatmlt_x"]
    if mlat:
        var_label_list += [prefix_orbit + "pos_rmlatmlt_y"]
    if mlt:
        var_label_list += [prefix_orbit + "pos_rmlatmlt_z"]

    return var_label_list


if __name__ == "__main__":
    var_label_list = add_orb()
    print(var_label_list)
