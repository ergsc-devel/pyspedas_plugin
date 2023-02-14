from typing import Dict, Optional

import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import pytplot
from pyspedas.utilities.tcopy import tcopy
from pytplot import get_data, options, tplot, tplot_options, xlim

from add_orb import add_orb
from erg_calc_pwe_wna import erg_calc_pwe_wna
from get_uname_passwd import get_uname_passwd
from plot_ofa import _postprocess_var_label_panel, _preprocess_var_label_panel, load_ofa
from wfc_options import (
    DataInfo,
    DataName,
    DataOption,
    OrbitalInformationOption,
    create_data_infos,
    create_data_options,
    orbital_information_option_dict,
)


def get_min_max(z: np.ndarray, zlog: int) -> tuple[float, float]:
    assert zlog in [0, 1]
    z_real = z.real
    if zlog == 0:
        return z_real.min(), z_real.max()
    else:
        z_real = z_real[np.abs(z) > 0]
        z_exponent = np.log10(z_real)
        return z_exponent.min(), z_exponent.max()


def get_mask(z: np.ndarray, threshold: float, zlog: int) -> np.ndarray:
    """
    >>> mask(np.array([1, 2, 3]), 2, 0)
    array([false, false, true])
    """
    assert zlog in [0, 1]
    if zlog == 0:
        return z.real >= threshold
    else:
        z_real = z.real.copy()
        m1 = z_real > 0
        z_real[~m1] = np.nan
        m2 = np.log10(z_real) >= threshold
        return m1 & m2


def load_wfc(
    trange=["2017-04-01/13:57:45", "2017-04-01/13:57:53"],
    data_infos: Optional[Dict[DataName, DataInfo]] = None,
    data_options: Optional[Dict[DataName, DataOption]] = None,
    no_update=False,
):
    if data_infos is None:
        data_infos = create_data_infos()

    if data_options is None:
        data_options = create_data_options()

    uname1, passwd1 = get_uname_passwd()

    # TODO: seems unnecessary now, but maybe better implement
    # t2 = erg_search_pwe_wfc_wf(t, cgProgressBar, ret)

    # seems this is only the essential load function in wfc
    succeeded, message = erg_calc_pwe_wna(
        trange=trange,
        w="hanning",
        nfft=4096,
        stride=2048,
        n_average=3,
        reload=~no_update,
        no_update=no_update,
    )

    # TODO: add orb is done in ofa, and if not so still add orb can be only once
    # TODO: add no update option
    orb_opt = OrbitalInformationOption(**orbital_information_option_dict)
    var_label_list = add_orb(
        orb_opt.mlt, orb_opt.mlat, orb_opt.altitude, orb_opt.lshell, trange, no_update
    )

    for name in DataName:
        opt = data_options[name]
        tplot_name = name.value
        tplot_name_for_plot = tplot_name + "_plot"
        tcopy(tplot_name, tplot_name_for_plot)
        options(tplot_name_for_plot, "ylog", opt.ylog)
        options(tplot_name_for_plot, "zlog", opt.zlog)
        options(tplot_name_for_plot, "ytitle", opt.ytitle)
        options(tplot_name_for_plot, "ysubtitle", opt.ysubtitle)
        options(tplot_name_for_plot, "ztitle", opt.ztitle)
        options(tplot_name_for_plot, "zrange", [opt.zmin, opt.zmax])
        options(tplot_name_for_plot, "yrange", [opt.ymin, opt.ymax])

    _set_info(data_options, data_infos)

    _mask(data_options, data_infos)

    tplot_names_for_plot = []
    for name in DataName:
        tplot_name = name.value
        tplot_name_for_plot = tplot_name + "_plot"
        tplot_names_for_plot.append(tplot_name_for_plot)

    return tplot_names_for_plot, var_label_list


def _set_info(data_options, data_infos):
    for name in DataName:
        opt = data_options[name]
        info = data_infos[name]
        tplot_name = name.value
        data = get_data(tplot_name)
        minimum, maximum = get_min_max(data.y, opt.zlog)
        info.min = minimum
        info.max = maximum
        # Set mask threshold (minimum means that mask does nothing)
        info.mask = minimum


def _mask(data_options, data_infos):
    # Total mask is logical sum of mask of each variable
    # Make mask
    mask = None
    for name in DataName:
        opt = data_options[name]
        info = data_infos[name]
        tplot_name = name.value
        data = get_data(tplot_name)
        assert data is not None
        if mask is None:
            mask = get_mask(data.y, info.mask, opt.zlog)
        else:
            mask = mask & get_mask(data.y, info.mask, opt.zlog)
    assert mask is not None

    # Apply mask
    for name in DataName:
        tplot_name = name.value
        tplot_name_for_plot = tplot_name + "_plot"
        data = get_data(tplot_name)
        assert data is not None
        # Data value can be complex, so convert to real for plot
        y = data.y.real.copy()
        # Make invalid except mask
        y[~mask] = -np.inf
        # Replace masked data
        pytplot.data_quants[tplot_name_for_plot].values = y


def plot_wfc_init(xsize: float = 8, ysize: float = 10) -> matplotlib.figure.Figure:
    # Figure size is 650 x 900 (px)
    # In the case of dpi = 100
    fig = plt.figure(figsize=(xsize, ysize), facecolor="black")
    return fig


def plot_wfc(
    fig: matplotlib.figure.Figure, trange, tplot_names_for_plot, var_label_list
) -> matplotlib.figure.Figure:
    fig.clf()
    # Controls not loaded data xrange but plot xrange
    xlim(*trange)

    # Layout settings
    tplot_options("vertical_spacing", 0.1)

    # font size
    fs = 10
    tplot_options("charsize", fs)
    tplot_options("axis_font_size", fs)
    tplot_options("ymargin", [0.05, 0.05])

    # Preprocess var panels
    fig, axes = _preprocess_var_label_panel(fig, tplot_names_for_plot, var_label_list)

    # Then tplot
    fig, axes = tplot(
        tplot_names_for_plot,
        return_plot_objects=True,
        fig=fig,
        axis=axes,
        display=False,
    )

    # Postprocess var panels
    _postprocess_var_label_panel(tplot_names_for_plot, var_label_list, axes, fs)

    n_tplot_panels = len(tplot_names_for_plot) + 1
    # Must be fig.axes, not axes (tplot does not return colorbar axes)
    for ax in fig.axes[n_tplot_panels:]:
        pos = ax.get_position()
        pos.x0 -= 0.008
        pos.x1 -= 0.008
        ax.set_position(pos)

    return fig


if __name__ == "__main__":
    no_update = False
    trange_ofa = ["2017-04-01/00:00:00", "2017-04-01/23:59:59"]
    _ = load_ofa(trange=trange_ofa, no_update=no_update)
    trange_wfc = ["2017-04-01/13:57:45", "2017-04-01/13:57:53"]
    data_options = create_data_options()
    data_infos = create_data_infos()
    tplot_names_for_plot, var_label_list = load_wfc(
        trange=trange_wfc,
        data_infos=data_infos,
        data_options=data_options,
        no_update=no_update,
    )
    fig = plot_wfc_init()
    fig = plot_wfc(fig, trange_wfc, tplot_names_for_plot, var_label_list)
    plt.show()
