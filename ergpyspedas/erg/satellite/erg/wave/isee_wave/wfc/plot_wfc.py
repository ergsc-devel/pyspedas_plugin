from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pytplot
from matplotlib.figure import Figure
from pyspedas.utilities.tcopy import tcopy
from pytplot import get_data, options, store_data, tplot, tplot_options, xlim

from ..load.add_orb import add_orb
from ..load.erg_search_pwe_wfc_wf import erg_search_pwe_wfc_wf
from ..ofa.plot_ofa import (
    _postprocess_var_label_panel,
    _preprocess_var_label_panel,
    load_ofa,
)
from ..options.options import (
    DataInfo,
    DataName,
    DataOption,
    OrbitalInfoName,
    create_data_options,
    create_orbital_informations,
    data_option_dict_dict,
    orbital_information_option_dict,
)
from ..utils.get_uname_passwd import get_uname_passwd
from .erg_calc_pwe_wna import erg_calc_pwe_wna


def get_min_max_idl(z: np.ndarray, zlog: int) -> Tuple[float, float]:
    """
    >>> get_min_max_idl(np.array([1, 2]), 1)
    array([1, 2])
    >>> get_min_max_idl(np.array([1, -2]), 1)
    array([1, 1])
    >>> get_min_max_idl(np.array([-1, -2]), 1)
    array([-inf, -inf])
    """

    # Compatible with pw_get_minmax_val in IDL
    assert zlog in [0, 1]
    z_real = z.real
    if zlog == 0:
        return z_real.min(), z_real.max()
    else:
        z_real = z_real[np.abs(z) > 0]
        z_pos = z_real[z_real > 0]
        if len(z_pos) == 0:
            return -2147483648, -2147483648
        z_exponent = np.log10(z_pos)
        # Rounding is same in IDL and Python
        # This cuts off some data, which seems not good
        return round(z_exponent.min()), round(z_exponent.max())


def get_mask_idl(z: np.ndarray, threshold: float, zlog: int) -> np.ndarray:
    """
    >>> get_mask_idl(np.array([1, 2, 3]), 2, 0)
    array([false, false, true])
    """
    # Compatible with pw_event_mask_set in IDL
    assert zlog in [0, 1]
    if zlog == 0:
        return z.real >= threshold
    else:
        z_real = z.real.copy()
        # z_real < 0 and nans are false, meaning passed at final
        # I don't know how they are treated in plotting at IDL or Matplotlib
        # z_real == 0 is generally true for all threshold, meaning blocked at final
        # when threshold is -2147483648, z_real == 0 is true
        # Ideally, z_real <= 0 should be all blocked
        blocking_mask = np.log10(z_real) < threshold
        # TODO:
        # it is different to mask or plot
        # nan in one data should not spread to other data for masking
        return ~blocking_mask


def get_min_max(z: np.ndarray, zlog: bool) -> Tuple[float, float]:
    z_real = z.real
    if zlog:
        z_pos = z_real[z_real > 0]
        if len(z_pos) == 0:
            return np.nan, np.nan
        else:
            return z_pos.min(), z_pos.max()
    else:
        return z_real.min(), z_real.max()


def get_mask(z: np.ndarray, threshold: float, zlog: bool) -> np.ndarray:
    z_real = z.real
    if zlog:
        z_pos = z_real.copy()
        z_pos[z_real <= 0] = np.nan
        # Notice NaNs and non-positives are evaluated as False not in mask
        return z_pos <= threshold
    else:
        # Notice NaNs are evaluated as False and thus not in mask
        return z_real <= threshold


def load_wfc(
    trange=["2017-04-01/13:57:45", "2017-04-01/13:57:53"],
    data_options: Optional[Dict[DataName, DataOption]] = None,
    no_update=False,
) -> Optional[
    Tuple[
        List[str],
        Dict[OrbitalInfoName, str],
        Dict[DataName, DataInfo],
        Tuple[float, float],
    ]
]:
    if data_options is None:
        data_options = create_data_options(data_option_dict_dict)

    uname1, passwd1 = get_uname_passwd()

    trange_actual = erg_search_pwe_wfc_wf(trange=trange, no_update=no_update)
    if trange_actual is None:
        # TODO: Should be dialog
        print("No waveform data is available in the specified time interval.")
        return None
    if trange_actual[1] - trange_actual[0] > 150:
        # TODO: Should be dialog
        print("Too long time interval was specified. Do you want to continue anyway?")

    # seems this is only the essential load function in wfc
    succeeded, message = erg_calc_pwe_wna(
        trange=trange_actual,  # type: ignore
        w="hanning",
        nfft=4096,
        stride=2048,
        n_average=3,
        reload=~no_update,  # type: ignore
        no_update=no_update,
    )

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

    # Reset mask data
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

    # TODO: add orb is done in ofa, and if not so still add orb can be only once
    # TODO: add no update option
    orb_opt = create_orbital_informations(orbital_information_option_dict)
    var_label_list = add_orb(
        l=orb_opt[OrbitalInfoName.l],
        mlat=orb_opt[OrbitalInfoName.mlat],
        alt=orb_opt[OrbitalInfoName.alt],
        mlt=orb_opt[OrbitalInfoName.mlt],
        trange=trange,
        no_update=no_update,
    )

    data_infos = _get_info(data_options)

    return tplot_names_for_plot, var_label_list, data_infos, trange_actual


def _update_info(
    name: DataName,
    data_options: Dict[DataName, DataOption],
    data_infos: Dict[DataName, DataInfo],
) -> None:
    opt = data_options[name]
    # Data should be taken from original tplot data
    tplot_name = name.value
    data = get_data(tplot_name)
    # minimum, maximum = get_min_max_idl(data.y, opt.zlog)
    minimum, maximum = get_min_max(data.y, opt.zlog)  # type: ignore
    info = DataInfo(min=minimum, max=maximum, mask=minimum)
    data_infos[name] = info


def _get_info(data_options: Dict[DataName, DataOption]) -> Dict[DataName, DataInfo]:
    data_infos: Dict[DataName, DataInfo] = {}
    for name in DataName:
        _update_info(name, data_options, data_infos)
    return data_infos


def _mask(
    data_options: Dict[DataName, DataOption], data_infos: Dict[DataName, DataInfo]
) -> None:
    # Total mask is logical sum of mask of each variable
    # Make mask
    mask = None
    for name in DataName:
        opt = data_options[name]
        info = data_infos[name]
        # Data should be taken from original tplot data
        tplot_name = name.value
        data = get_data(tplot_name)
        assert data is not None
        if mask is None:
            # mask = get_mask_idl(data.y, info.mask, opt.zlog)
            mask = get_mask(data.y, info.mask, opt.zlog)
        else:
            # mask = mask & get_mask_idl(data.y, info.mask, opt.zlog)
            mask = mask | get_mask(data.y, info.mask, opt.zlog)
    assert mask is not None
    # Apply mask
    for name in DataName:
        tplot_name = name.value
        tplot_name_for_plot = tplot_name + "_mask"
        data = get_data(tplot_name)
        assert data is not None
        y = data.y.real.copy()
        opt = data_options[name]
        if opt.mask:
            y[mask] = np.nan
        # Replace masked data
        pytplot.data_quants[tplot_name_for_plot].values = y


def plot_wfc_init(
    xsize: float = 800,
    ysize: float = 1000,
    dpi: int = 100,
    fig: Optional[Figure] = None,
) -> Figure:
    # Figure size is 650 x 900 (px)
    # In the case of dpi = 100
    xsize_inch = xsize / dpi
    ysize_inch = ysize / dpi
    if fig is None:
        fig = Figure()
    fig.set_size_inches(xsize_inch, ysize_inch)
    fig.set_facecolor("black")
    return fig


def plot_wfc(
    fig: Figure,
    trange: Tuple[float, float],
    tplot_names_for_plot: Sequence[str],
    var_label_dict: Dict[OrbitalInfoName, str],
    species: Optional[Sequence[str]],
    font_size: float = 10,
    data_options: Optional[Dict[DataName, DataOption]] = None,
    orbital_info_options: Optional[Dict[OrbitalInfoName, bool]] = None,
    rasterized: bool = False,
) -> Figure:
    fig.clf()
    if data_options is not None:
        tplot_names_for_plot_tmp = []
        for name, opt in data_options.items():
            tplot_name = name.value
            tplot_name_for_mask = tplot_name + "_mask"
            tplot_name_for_plot = tplot_name + "_plot"
            if opt.ylog:
                if not opt.ymin > 0:
                    raise ValueError("ymin must be > 0 if ylog == True")
                if not opt.ymax > 0:
                    raise ValueError("ymax must be > 0 if ylog == True")
            if opt.zlog:
                if not opt.zmin > 0:
                    raise ValueError("zmin must be > 0 if zlog == True")
                if not opt.zmax > 0:
                    raise ValueError("zmax must be > 0 if zlog == True")
            options(tplot_name_for_mask, "ylog", opt.ylog)
            options(tplot_name_for_mask, "zlog", opt.zlog)
            options(tplot_name_for_mask, "ytitle", opt.ytitle)
            options(tplot_name_for_mask, "ysubtitle", opt.ysubtitle)
            options(tplot_name_for_mask, "ztitle", opt.ztitle)
            options(tplot_name_for_mask, "zrange", [opt.zmin, opt.zmax])
            options(tplot_name_for_mask, "yrange", [opt.ymin, opt.ymax])
            if opt.plot and tplot_name_for_plot in tplot_names_for_plot:
                # tplot_names_for_plot_tmp.append(tplot_name_for_plot)
                # HACK: Use mask instead of plot because Python tplot() does not support overplot with specs
                tplot_names_for_plot_tmp.append(tplot_name_for_mask)
        tplot_names_for_plot = tplot_names_for_plot_tmp

    if orbital_info_options is None:
        var_label_list = [var_label for var_label in var_label_dict.values()]
    else:
        var_label_list = []
        for id_, var_label in var_label_dict.items():
            will_plot = orbital_info_options.get(id_)
            if will_plot:
                var_label_list.append(var_label)

    # Controls not loaded data xrange but plot xrange
    xlim(*trange)

    # Layout settings
    tplot_options("vertical_spacing", 0.1)

    # font size
    tplot_options("charsize", font_size)
    tplot_options("axis_font_size", font_size)
    tplot_options("ymargin", [0.05, 0.05])

    # Preprocess var panels
    fig, axs = _preprocess_var_label_panel(fig, tplot_names_for_plot, var_label_list)

    # Then tplot
    fig, axs = tplot(
        tplot_names_for_plot,
        return_plot_objects=True,
        fig=fig,
        axis=axs,
        display=False,
    )

    # HACK: Ideally overplots should be managed inside tplot() but it is not yet
    if species is not None:
        n_tplots = len(tplot_names_for_plot)
        for i in range(n_tplots):
            ax = axs[i]
            for s in species:
                s_data = get_data(s, dt=True)
                assert s_data is not None
                s_metadata = get_data(s, metadata=True)
                line_opts: Dict[Any] = s_metadata["plot_options"]["line_opt"]  # type: ignore
                plot_extras: Dict[Any] = s_metadata["plot_options"]["extras"]  # type: ignore
                line_color: Optional[List[Any]] = plot_extras.get("line_color")
                line_width: Optional[List[float]] = line_opts.get("line_width")
                line_style_user: Optional[List[str]] = line_opts.get("line_style_name")
                if line_color is not None:
                    color = line_color[0]
                else:
                    color = None
                if line_width is not None:
                    width = line_width[0]
                else:
                    width = 0.5
                if line_style_user is not None:
                    # line_style_user should already be a list
                    # handle legacy values
                    line_style = []
                    for linestyle in line_style_user:
                        if linestyle == "solid_line":
                            line_style.append("solid")
                        elif linestyle == "dot":
                            line_style.append("dotted")
                        elif linestyle == "dash":
                            line_style.append("dashed")
                        elif linestyle == "dash_dot":
                            line_style.append("dashdot")
                        else:
                            line_style.append(linestyle)
                else:
                    line_style = ["solid"]
                line_style = line_style[0]

                ax.plot(
                    s_data.times,
                    s_data.y,
                    color=color,
                    linewidth=width,
                    linestyle=line_style,
                )

    # Postprocess var panels
    _postprocess_var_label_panel(tplot_names_for_plot, var_label_list, axs, font_size)

    n_tplots = len(tplot_names_for_plot)
    if rasterized:
        for ax in fig.axes[:n_tplots]:
            # Line, spectrogram (which originates from data) is rasterized
            # Ticks, grid lines, text, legend is vectorized
            ax.set_axisbelow(False)
            ax.set_rasterization_zorder(2.005)

    return fig


if __name__ == "__main__":
    no_update = False
    trange_ofa = ["2017-04-01/00:00:00", "2017-04-01/23:59:59"]
    _ = load_ofa(trange=trange_ofa, no_update=no_update)
    trange_wfc = ["2017-04-01/13:57:45", "2017-04-01/13:57:53"]
    data_options = create_data_options(data_option_dict_dict)
    ret = load_wfc(
        trange=trange_wfc,
        data_options=data_options,
        no_update=no_update,
    )
    if ret is not None:
        tplot_names_for_plot, var_label_dict, data_infos, trange_actual = ret
        # Need to initialize figure by plt.figure() instead of Figure() if you do not use FigureCanvas
        fig = plt.figure()
        fig = plot_wfc_init(fig=fig)
        fig = plot_wfc(
            fig=fig,
            trange=trange_actual,
            tplot_names_for_plot=tplot_names_for_plot,
            var_label_dict=var_label_dict,
            species=None,
        )
        plt.show()
