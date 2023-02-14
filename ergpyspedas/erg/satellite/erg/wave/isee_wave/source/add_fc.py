from typing import Sequence

import numpy as np
from pyspedas.erg.satellite.erg.mgf.mgf import mgf
from pyspedas.erg.satellite.erg.orb.orb import orb
from pyspedas.utilities.tnames import tnames
from pytplot import get_data, options, store_data, tplot_copy

from get_uname_passwd import get_uname_passwd
from orb_predict import orb_predict


def add_fc(
    tnum: Sequence[str],
    species: Sequence[str],
    m: Sequence[float],
    q: Sequence[float],
    lsty: Sequence[float],
    lcol: Sequence[float],
    khz: bool = False,
    trange=["2017-04-01/13:57:45", "2017-04-01/13:57:53"],
    no_update=False,
):
    # Get username and password
    uname1, passwd1 = get_uname_passwd()
    # Load orb
    orb(uname=uname1, passwd=passwd1, trange=trange, no_update=no_update)
    prefix_orbit = "erg_orb_l2_"
    if not tnames(prefix_orbit + "pos_blocal_mag"):
        orb_predict(uname=uname1, passwd=passwd1, trange=trange, no_download=no_update)
        prefix_orbit = "erg_orb_pre_l2_"

    # Load mgf L2
    mgf(uname=uname1, passwd=passwd1, trange=trange, no_update=no_update)

    if tnames("erg_mgf_l2_magt_8sec"):
        # use MGF L2
        data = get_data("erg_mgf_l2_magt_8sec")
    else:
        # use IGRF
        data = get_data(prefix_orbit + "pos_blocal_mag")

    # calc Fc
    factor = 1
    if khz:
        factor = 1000
    fce = (
        data.y
        / 10**9
        * 1.6
        * 10 ** (-19)
        / (9.1093 * 10 ** (-31))
        / 2
        / np.pi
        / factor
    )

    for i in range(len(m)):
        store_data(
            species[i],
            data={"x": data.x, "y": q[i] * fce / (1837 * m[i])},
            attr_dict={"Color": 5, "thick": 2},
        )
        # TODO: implement
        # tinterpol_mxn, species[i], tnames(tnum[i])+'_mask', newname=species[i]
        options(species[i], "Color", int(lcol[i]))
        options(species[i], "line_style", int(lsty[i]))

    for i in range(len(tnum)):
        # TODO: not sure this is correct
        if tnames(tnum[i] + "_plot"):
            attrs = get_data(tnum[i] + "_plot", metadata=True)
            # Combine mask and species
            store_data(
                tnum[i] + "_plot",
                [tnum[i] + "_mask"] + list(species),
                attr_dict=attrs,
            )
        else:
            store_data(tnum[i] + "_plot", [tnum[i] + "_mask"] + list(species))


if __name__ == "__main__":
    add_fc(
        ["espec", "bspec", "wna", "polarization", "planarity", "poyntingvec"],
        [],
        [],
        [],
        [],
        [],
        trange=["2017-04-01/13:57:45", "2017-04-01/13:57:53"],
        no_update=False,
    )
