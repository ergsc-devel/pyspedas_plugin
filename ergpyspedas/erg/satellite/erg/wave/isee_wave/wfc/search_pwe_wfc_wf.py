from typing import List, Optional, Sequence, Tuple

import numpy as np
from pyspedas.utilities.time_double import time_double
from pytplot import get_data, store_data

# Use bugfixed below now instead of: from pyspedas.erg.satellite.erg.pwe.pwe_wfc import pwe_wfc
from ergpyspedas.erg import pwe_wfc

from ..utils.get_uname_passwd import get_uname_passwd
from ..utils.progress_manager import MessageKind, ProgressManagerInterface


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
        progress_manager.set_value(0)

    uname, passwd = get_uname_passwd()

    # Convert to float for comparison
    trange = (time_double(trange[0]), time_double(trange[1]))  # type: ignore

    # Try search 65khz data
    pwe_wfc(trange=trange, uname=uname, passwd=passwd, no_update=no_update)

    if progress_manager is not None:
        # If cancel is triggered by user, show message
        if progress_manager.canceled():
            progress_manager.ask_message(
                "The user cancelled operation.", MessageKind.information
            )
            return None
        # Set progress
        progress_manager.set_value(50)

    # If 65khz data exists
    # Use Bx data for calculating the representive of actual trange
    data = get_data("erg_pwe_wfc_l2_b_65khz_Bx_waveform")
    if data is not None:
        indices = np.where((data.times >= trange[0]) & (data.times <= trange[1]))[0]
        if len(indices) >= 1:
            # Actual trange
            start, end = data.times[indices[0]], data.times[indices[-1]]
            # Delete wp65khz data
            store_data("erg_pwe_wfc_l2_?_wp65khz_??_waveform", delete=True)
            # Also tlimit other data
            # NOTE: Time range of data from pwe_wfc is slightly different and
            # usually wider than that of IDL. It seems difficult which is better.
            # Therefore the difference is compensated here instead of inside pwe_wfc.
            tplot_names = [
                "erg_pwe_wfc_l2_b_65khz_Bx_waveform",
                "erg_pwe_wfc_l2_b_65khz_By_waveform",
                "erg_pwe_wfc_l2_b_65khz_Bz_waveform",
                "erg_pwe_wfc_l2_e_65khz_Ex_waveform",
                "erg_pwe_wfc_l2_e_65khz_Ey_waveform",
            ]
            for tplot_name in tplot_names:
                data = get_data(tplot_name)
                indices = np.where(
                    (data.times >= trange[0]) & (data.times <= trange[1])  # type: ignore
                )[0]
                if len(indices) >= 1:
                    dlim = get_data(tplot_name, metadata=True)
                    store_data(
                        tplot_name,
                        data={"x": data.times[indices], "y": data.y[indices]},  # type: ignore
                        attr_dict=dlim,
                    )
            return start, end

    # Try search wp65khz data if 65khz data does not exist
    # NOTE: Not tested in real data
    pwe_wfc(
        trange=trange,
        uname=uname,
        passwd=passwd,
        no_update=no_update,
        mode="wp65khz",
    )

    # If wp65khz data exists
    # Use Bx data for calculating the representive of actual trange
    data = get_data("erg_pwe_wfc_l2_b_wp65khz_Bx_waveform")
    if data is not None:
        indices = np.where((data.times >= trange[0]) & (data.times <= trange[1]))[0]
        if len(indices) >= 1:
            # Actual trange
            start, end = data.times[indices[0]], data.times[indices[-1]]
            # Delete 65khz data
            store_data("erg_pwe_wfc_l2_?_65khz_??_waveform", delete=True)
            # Also tlimit other data
            # NOTE: Time range of data from pwe_wfc is slightly different and
            # usually wider than that of IDL. It seems difficult which is better.
            # Therefore the difference is compensated here instead of inside pwe_wfc.
            tplot_names = [
                "erg_pwe_wfc_l2_b_wp65khz_Bx_waveform",
                "erg_pwe_wfc_l2_b_wp65khz_By_waveform",
                "erg_pwe_wfc_l2_b_wp65khz_Bz_waveform",
                "erg_pwe_wfc_l2_e_wp65khz_Ex_waveform",
                "erg_pwe_wfc_l2_e_wp65khz_Ey_waveform",
            ]
            for tplot_name in tplot_names:
                data = get_data(tplot_name)
                indices = np.where(
                    (data.times >= trange[0]) & (data.times <= trange[1])  # type: ignore
                )[0]
                if len(indices) >= 1:
                    dlim = get_data(tplot_name, metadata=True)
                    store_data(
                        tplot_name,
                        data={"x": data.times[indices], "y": data.y[indices]},  # type: ignore
                        attr_dict=dlim,
                    )
            return start, end

    if progress_manager is not None:
        if progress_manager.canceled():
            progress_manager.ask_message(
                "The user cancelled operation.", MessageKind.information
            )
            return None
        progress_manager.set_value(100)

    return None


if __name__ == "__main__":
    search_pwe_wfc_wf()
