from datetime import datetime
from typing import Dict, List, Optional, Sequence, Tuple, Union

import pytplot
from pyspedas.utilities.tcopy import tcopy
from pytplot import get_data, store_data

from ..ofa.add_orb import add_orb
from ..options.data_option import DataName
from ..options.orbital_info_option import OrbitalInfoName
from ..utils.progress_manager import ProgressManagerInterface
from .erg_calc_pwe_wna import MessageKind, erg_calc_pwe_wna
from .search_pwe_wfc_wf import search_pwe_wfc_wf


def load_wfc(
    trange: Union[Sequence[str], Sequence[float], Sequence[datetime]] = [
        "2017-04-01/13:57:45",
        "2017-04-01/13:57:53",
    ],
    w: str = "Hanning",
    nfft: int = 4096,
    stride: int = 2048,
    n_average: int = 3,
    no_update: bool = False,
    progress_manager: Optional[ProgressManagerInterface] = None,
) -> Optional[Tuple[Dict[OrbitalInfoName, str], Tuple[float, float]]]:
    trange_actual = search_pwe_wfc_wf(
        trange=trange, no_update=no_update, progress_manager=progress_manager  # type: ignore
    )
    if trange_actual is None:
        if progress_manager is not None and not progress_manager.was_canceled():
            progress_manager.confirm_cancel(
                "No waveform data is available in the specified time interval.",
                MessageKind.information,
            )
        return None
    if (
        trange_actual[1] - trange_actual[0] > 150
        and progress_manager is not None
        and not progress_manager.was_canceled()
    ):
        if progress_manager.confirm_cancel(
            "Too long time interval was specified. Do you want to continue anyway?",
            MessageKind.question,
        ):
            return None

    # TODO: Interface changed a bit so need modification
    succeeded, message = erg_calc_pwe_wna(
        trange=trange_actual,  # type: ignore
        w=w,
        nfft=nfft,
        stride=stride,
        n_average=n_average,
        reload=~no_update,  # type: ignore
        no_update=no_update,
    )

    # Reset mask and plot tplot variables
    for name in DataName:
        tplot_name = name.value
        # tplot variable for mask
        tplot_name_for_mask = tplot_name + "_mask"
        tcopy(tplot_name, tplot_name_for_mask)
        # tplot variable for plot
        # this can have tplot_name_for_mask and species as pseudo vars
        tplot_name_for_plot = tplot_name + "_plot"
        # Need to pass attr_dict of tplot_name_for_mask to inform that this plot is spectrogram
        attr_dict = get_data(tplot_name_for_mask, metadata=True)
        store_data(tplot_name_for_plot, data=[tplot_name_for_mask], attr_dict=attr_dict)

    # Convert mask data to real
    for name in DataName:
        tplot_name = name.value
        tplot_name_for_mask = tplot_name + "_mask"
        data = get_data(tplot_name)
        assert data is not None
        y = data.y.real.copy()
        pytplot.data_quants[tplot_name_for_mask].values = y

    tplot_names_for_plot: List[str] = []
    for name in DataName:
        tplot_name = name.value
        tplot_name_for_plot = tplot_name + "_plot"
        tplot_names_for_plot.append(tplot_name_for_plot)

    # First set True for l, mlat, alt, mlt to get exact tplot_names for them
    var_label_dict = add_orb(
        l=True,
        mlat=True,
        alt=True,
        mlt=True,
        trange=trange,
        no_update=no_update,
    )

    return var_label_dict, trange_actual
