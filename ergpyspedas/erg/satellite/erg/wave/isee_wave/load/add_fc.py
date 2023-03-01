from typing import Sequence

import numpy as np
from pyspedas.erg.satellite.erg.mgf.mgf import mgf
from pyspedas.erg.satellite.erg.orb.orb import orb
from pyspedas.utilities.tnames import tnames
from pytplot import get_data, options, store_data, tinterp

from ..utils.colormaps import colormaps
from ..utils.get_uname_passwd import get_uname_passwd
from ..utils.utils import line_style_idl_to_mpl
from .orb_predict import orb_predict


def add_fc(
    tplots: Sequence[str],
    species: Sequence[str],
    m: Sequence[float],
    q: Sequence[float],
    lsty: Sequence[int],
    lcol: Sequence[int],
    khz: bool = False,
    trange=["2017-04-01/13:57:45", "2017-04-01/13:57:53"],
    no_update=False,
) -> bool:
    if not len(species) == len(m) == len(q) == len(lsty) == len(lcol):
        raise ValueError("species, m, q, lcol, lsty must have same length")
    if not len(tplots) >= 1:
        raise ValueError("Must be len(tplots) >= 1")
    for i in range(len(m)):
        if not tnames(tplots[i] + "_mask"):
            raise ValueError(f'tplot variable {tplots[i] + "_mask"} does not exist')

    # TODO: Downloading can be suppressed but since it is difficult to know
    # that sufficient data for target trange exists from tplot variables,
    # whether target trange data is downloaded or not should be managed by
    # like downloaded_range = [trange1, trange2, ...]
    # Also sometimes download fails due to network connection problem,
    # so it's nice to enable download at least several times
    # If this is cumbersome, download every time is better

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
    if data is None:
        return False

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

    tplot = tplots[0]
    for i in range(len(m)):
        # Create fc data
        store_data(
            species[i],
            data={"x": data.times, "y": q[i] * fce / (1837 * m[i])},
        )
        # Interpolated species's time is changed to that of tplot
        tinterp(tplot + "_mask", species[i], replace=True)

        # Options
        colormap = colormaps["Blue-Red"]
        options(species[i], "Color", colormap(lcol[i]))
        options(species[i], "line_style", line_style_idl_to_mpl(lsty[i]))
        options(species[i], "thick", 2)

    # Add fc data to tplot
    for i in range(len(tplots)):
        attrs = get_data(tplots[i] + "_plot", metadata=True)
        # Plotting tplots[i] + "_plot" results in overplotting [tplots[i] + "_mask"] + list(species)
        store_data(
            tplots[i] + "_plot",
            [tplots[i] + "_mask"] + list(species),
            attr_dict=attrs,
        )
    return True


if __name__ == "__main__":
    print(
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
    )
