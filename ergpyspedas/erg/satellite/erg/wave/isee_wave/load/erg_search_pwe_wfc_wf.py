from typing import Optional, Tuple

from pyspedas.erg.satellite.erg.pwe.pwe_wfc import pwe_wfc
from pyspedas.utilities.time_double import time_double
from pytplot import get_data, store_data

from ..utils.get_uname_passwd import get_uname_passwd


def erg_search_pwe_wfc_wf(
    trange=["2017-04-01/13:57:45", "2017-04-01/13:57:53"], no_update=False
) -> Optional[Tuple[float, float]]:
    uname, passwd = get_uname_passwd()

    pwe_wfc(trange=trange, uname=uname, passwd=passwd, no_update=no_update)
    data = get_data("erg_pwe_wfc_l2_b_65khz_Bx_waveform")

    # Convert to float for comparison
    trange = (time_double(trange[0]), time_double(trange[1]))
    if data is not None:
        start = data.times[0]
        end = data.times[-1]
        if trange[0] < end and trange[1] > start:
            store_data("erg_pwe_wfc_l2_?_wp65khz_??_waveform", delete=True)
            return (start, end)

    # TODO: Cannot download "wp65khz"
    pwe_wfc(
        trange=trange, uname=uname, passwd=passwd, no_update=no_update, mode="wp65khz"
    )
    data = get_data("erg_pwe_wfc_l2_b_wp65khz_Bx_waveform")
    if data is not None:
        start = data.times[0]
        end = data.times[-1]
        if trange[0] < end and trange[1] > start:
            store_data("erg_pwe_wfc_l2_?_65khz_??_waveform", delete=True)
            return (start, end)

    return None
