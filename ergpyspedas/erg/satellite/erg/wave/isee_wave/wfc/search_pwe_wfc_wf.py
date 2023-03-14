from typing import Optional, Sequence, Tuple

from pyspedas.erg.satellite.erg.pwe.pwe_wfc import pwe_wfc
from pyspedas.utilities.time_double import time_double
from pytplot import get_data, store_data

from ..utils.get_uname_passwd import get_uname_passwd
from ..utils.progress_manager import ProgressManagerInterface
from .erg_calc_pwe_wna import MessageKind


def search_pwe_wfc_wf(
    trange: Sequence[str] = [
        "2017-04-01/13:57:45",
        "2017-04-01/13:57:53",
    ],
    no_update: bool = False,
    progress_manager: Optional[ProgressManagerInterface] = None,
) -> Optional[Tuple[float, float]]:
    """Try search pwe_wfc_wf data and return actual trange that data exists"""

    # Set progress manager a label if exists
    if progress_manager is not None:
        progress_manager.set_label_text("Downloading...")

    uname, passwd = get_uname_passwd()

    # Convert to float for comparison
    trange = (time_double(trange[0]), time_double(trange[1]))  # type: ignore

    # Try search 65khz data
    try:
        pwe_wfc(trange=trange, uname=uname, passwd=passwd, no_update=no_update)
    # May fail due to bug so print exception w/o system one
    except Exception as e:
        print(f"Error ignored in search_pwe_wfc_wf: {e}")

    if progress_manager is not None:
        # If cancel is triggered by user, show message
        if progress_manager.was_cancel_triggered():
            if progress_manager.confirm_cancel(
                "The user cancelled operation.", MessageKind.information
            ):
                return None
        # Set progress
        progress_manager.set_value(50)

    data = get_data("erg_pwe_wfc_l2_b_65khz_Bx_waveform")
    if data is not None:
        start = data.times[0]
        end = data.times[-1]
        if trange[0] < end and trange[1] > start:
            store_data("erg_pwe_wfc_l2_?_wp65khz_??_waveform", delete=True)
            return (start, end)

    # Try search wp65khz data if 65khz data does not exist
    # NOTE: Not tested in real data
    try:
        pwe_wfc(
            trange=trange,
            uname=uname,
            passwd=passwd,
            no_update=no_update,
            mode="wp65khz",
        )
    # May fail due to bug so print exception w/o system one
    except Exception as e:
        print(f"Error ignored in search_pwe_wfc_wf: {e}")

    data = get_data("erg_pwe_wfc_l2_b_wp65khz_Bx_waveform")
    if data is not None:
        start = data.times[0]
        end = data.times[-1]
        if trange[0] < end and trange[1] > start:
            store_data("erg_pwe_wfc_l2_?_65khz_??_waveform", delete=True)
            return (start, end)

    if progress_manager is not None:
        if progress_manager.was_cancel_triggered():
            if progress_manager.confirm_cancel(
                "The user cancelled operation.", MessageKind.information
            ):
                return None
        progress_manager.set_value(90)

    return None


if __name__ == "__main__":
    search_pwe_wfc_wf()
