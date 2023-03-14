from datetime import datetime
from typing import Dict, Optional, Sequence, Union

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pytplot import options, tplot_options, xlim

from ..options.data_option import DataName, DataOptions
from ..options.orbital_info_option import OrbitalInfoName, OrbitalInfoOption
from ..plot.common import overplot_line, plot_init, tplot_with_var_label_panel


def plot_wfc(
    trange: Union[Sequence[str], Sequence[float], Sequence[datetime]],
    orb_dict: Dict[OrbitalInfoName, str],
    species: Optional[Sequence[str]],
    fig: Optional[Figure] = None,
    font_size: float = 10,
    data_options: Optional[DataOptions] = None,
    orbital_info_options: Optional[OrbitalInfoOption] = None,
    rasterized: bool = False,
) -> Figure:
    """Plot wfc.

    Parameters
    ----------
    trange : Union[Sequence[str], Sequence[float], Sequence[datetime]]
        trange to show in plot
    orb_dict : Dict[OrbitalInfoName, str]
        Orbital info to plot
    species : Optional[Sequence[str]]
        Fc species to plot
    fig : Optional[Figure], optional
        Figure to plot, by default None
    font_size : float, optional
        Font size, by default 10
    data_options : Optional[DataOptions], optional
        DataOptions, by default None
    orbital_info_options : Optional[OrbitalInfoOption], optional
        OrbitalInfoOption, by default None
    rasterized : bool, optional
        If rasterize spec data, by default False

    Returns
    -------
    Figure
        Figure
    """
    if fig is None:
        fig = plt.figure()
        fig = plot_init(xsize=800, ysize=1000, dpi=100, fig=fig)

    tplot_names_for_plot = [name.value + "_plot" for name in DataName]
    # Clear figure
    fig.clf()

    if data_options is not None:
        tplot_names_for_plot_tmp = []
        for name, opt in data_options.items():
            tplot_name = name.value
            tplot_name_for_mask = tplot_name + "_mask"
            options(tplot_name_for_mask, "ytitle", opt.ytitle)
            options(tplot_name_for_mask, "ysubtitle", opt.ysubtitle)
            options(tplot_name_for_mask, "ylog", opt.ylog)
            options(tplot_name_for_mask, "yrange", [opt.ymin, opt.ymax])
            options(tplot_name_for_mask, "ztitle", opt.ztitle)
            options(tplot_name_for_mask, "zlog", opt.zlog)
            options(tplot_name_for_mask, "zrange", [opt.zmin, opt.zmax])
            tplot_name_for_plot = tplot_name + "_plot"
            if opt.plot:
                tplot_names_for_plot_tmp.append(tplot_name_for_plot)
        tplot_names_for_plot = tplot_names_for_plot_tmp

    if orbital_info_options is None:
        var_label_list = [var_label for var_label in orb_dict.values()]
    else:
        var_label_list = []
        for id_, var_label in orb_dict.items():
            will_plot = getattr(orbital_info_options, id_.value)
            if will_plot:
                var_label_list.append(var_label)

    # xlim does not control data range but plot range
    xlim(*trange)

    # Layout settings
    tplot_options("vertical_spacing", 0.1)

    # font size
    tplot_options("charsize", font_size)
    tplot_options("axis_font_size", font_size)
    # NOTE: Setting xmargin from tplot_options when a spectrogram exists is ineffective in pytplot-mpl-temp == 2.1.17
    tplot_options("xmargin", [0.11, 0.87])
    tplot_options("ymargin", [0.05, 0.05])

    # HACK: Use mask instead of plot because Python tplot() does not support overplot with specs yet
    # Also, plot 2D line for species directly using Matplotlib
    tplot_names_for_plot = [
        name.replace("_plot", "_mask") for name in tplot_names_for_plot
    ]

    fig, axs = tplot_with_var_label_panel(
        tplot_list=tplot_names_for_plot,
        var_label_list=var_label_list,
        fig=fig,
        display=False,
        return_plot_objects=True,
        font_size=font_size,
    )  # type: ignore

    if species is not None:
        n_tplots = len(tplot_names_for_plot)
        for i in range(n_tplots):
            ax = axs[i]
            for s in species:
                overplot_line(s, ax)

    # When setting xmargin from tplot_options is ineffective, set it from Matplotlib
    fig.subplots_adjust(left=0.11, right=0.87)

    if rasterized:
        n_tplots = len(tplot_names_for_plot)
        for ax in fig.axes[:n_tplots]:
            # Line, spectrogram (which originates from data) is rasterized
            # Available in *.eps, *.pdf files but not in GUI
            # Below means ticks, grid lines, text, legend is vectorized
            ax.set_axisbelow(False)
            ax.set_rasterization_zorder(2.005)

    return fig


if __name__ == "__main__":
    from .load_wfc import load_wfc

    no_update = False
    trange_wfc = ["2017-04-01/13:57:45", "2017-04-01/13:57:53"]
    ret = load_wfc(
        trange=trange_wfc,
        no_update=no_update,
    )
    if ret is not None:
        orb_dict, trange_actual = ret
        fig = plot_wfc(
            trange=trange_actual,
            orb_dict=orb_dict,
            species=None,
        )
        plt.show()
