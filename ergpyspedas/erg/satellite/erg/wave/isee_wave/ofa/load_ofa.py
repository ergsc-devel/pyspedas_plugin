from datetime import datetime
from typing import Dict, Sequence, Union

from pyspedas.erg.satellite.erg.pwe.pwe_ofa import pwe_ofa

from ..load.pwe_wfc_info import pwe_wfc_info
from ..options.orbital_info_option import OrbitalInfoName
from ..utils.get_uname_passwd import get_uname_passwd
from .add_orb import add_orb


def load_ofa(
    trange: Union[Sequence[str], Sequence[float], Sequence[datetime]] = [
        "2017-04-01/00:00:00",
        "2017-04-01/23:59:59",
    ],
    no_update: bool = False,
) -> Dict[OrbitalInfoName, str]:
    uname, passwd = get_uname_passwd()

    # Load data and configure general plot settings
    ofa_tvars = pwe_ofa(trange=trange, uname=uname, passwd=passwd, no_update=no_update)
    wfc_info_tvars = pwe_wfc_info(
        trange=trange, uname=uname, passwd=passwd, no_download=no_update
    )
    orb_tvars_dict = add_orb(
        mlt=True, mlat=True, alt=True, l=True, trange=trange, no_update=no_update
    )

    return orb_tvars_dict
