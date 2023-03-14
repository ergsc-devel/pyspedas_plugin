from datetime import datetime
from typing import Dict, Optional, Sequence, Union

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
from pytplot import tplot_options, xlim
from pytplot.options import options

from ..options.orbital_info_option import OrbitalInfoName
from ..plot.common import plot_init, tplot_with_var_label_panel


def plot_ofa(
    trange: Union[Sequence[str], Sequence[float], Sequence[datetime]],
    orb_dict: Dict[OrbitalInfoName, str],
    fig: Optional[Figure] = None,
    font_size: float = 10,
) -> Figure:
    """Plot ofa.

    Parameters
    ----------
    trange : Union[Sequence[str], Sequence[float], Sequence[datetime]]
        trange to show in plot
    orb_dict : Dict[OrbitalInfoName, str]
        Orbital info to plot
    fig : Optional[Figure], optional
        Figure to plot, by default None
    font_size : float, optional
        Font size, by default 10

    Returns
    -------
    Figure
        Figure
    """
    if fig is None:
        fig = plt.figure()
        fig = plot_init(xsize=1280, ysize=600, dpi=100, fig=fig)

    # Data
    tplot_list = [
        "erg_pwe_ofa_l2_spec_E_spectra_132",
        "erg_pwe_ofa_l2_spec_B_spectra_132",
        "erg_pwe_wfc_l2_infostat_chorus",
        "erg_pwe_wfc_l2_infostat_swpia",
    ]
    var_label_list = [tplot_name for tplot_name in orb_dict.values()]

    # Plot-specific settings
    # Clear figure
    fig.clf()

    # Controls not loaded data xrange but plot xrange
    xlim(*trange)

    # Specific option settings
    options("erg_pwe_ofa_l2_spec_E_spectra_132", "ytitle", "PWE/OFA-SPEC E")
    options("erg_pwe_ofa_l2_spec_E_spectra_132", "ztitle", r"$\rm{[mV^2/m^2/Hz]}$")
    options("erg_pwe_ofa_l2_spec_B_spectra_132", "ytitle", "PWE/OFA-SPEC B")
    options("erg_pwe_ofa_l2_spec_B_spectra_132", "ztitle", r"$\rm{[pT^2/Hz]}$")

    # Layout settings
    tplot_options("vertical_spacing", 0.2)

    # font size
    tplot_options("charsize", font_size)
    tplot_options("axis_font_size", font_size)
    # Setting xmargin from tplot_options when a spectrogram exists is ineffective in pytplot-mpl-temp == 2.1.17
    tplot_options("xmargin", [0.11, 0.87])
    tplot_options("ymargin", [0.05, 0.05])
    wfi = "erg_pwe_wfc_l2_infostat_"
    kinds = ["chorus", "emic", "efd", "swpia"]
    names = [wfi + kind for kind in kinds]
    for name in names:
        options(name, "marker_size", font_size * 2)

    # Plot
    fig, axs = tplot_with_var_label_panel(
        tplot_list=tplot_list,
        var_label_list=var_label_list,
        fig=fig,
        display=False,
        return_plot_objects=True,
        font_size=font_size,
    )  # type: ignore

    # When setting xmargin from tplot_options is ineffective, set it from Matplotlib
    fig.subplots_adjust(left=0.11, right=0.87)

    ax_e = axs[0]
    # Only if data exists
    if len(ax_e.collections) > 0:
        ax_e.collections[-1].colorbar.ax.yaxis.set_major_locator(
            ticker.LogLocator(base=10, numticks=10)
        )
    ax_b = axs[1]
    # Only if data exists
    if len(ax_b.collections) > 0:
        ax_b.collections[-1].colorbar.ax.yaxis.set_major_locator(
            ticker.LogLocator(base=10, numticks=10)
        )
    ax_chorus = axs[2]
    ax_chorus.set_yticks([1.5, 2.0, 2.5], [" ", "65k", " "])
    ax_swpia = axs[3]
    ax_swpia.set_yticks([0.5, 1.0, 1.5], [" ", "WP", " "])

    return fig


if __name__ == "__main__":
    from .load_ofa import load_ofa

    trange = ["2017-04-01/00:00:00", "2017-04-01/23:59:59"]
    orb_dict = load_ofa(trange=trange, no_update=False)
    fig = plot_ofa(trange=trange, orb_dict=orb_dict)
    plt.show()
