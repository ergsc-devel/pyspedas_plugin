import matplotlib as mpl
import matplotlib.figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pytplot
from pyspedas.erg.satellite.erg.pwe.pwe_ofa import pwe_ofa
from pytplot import tplot_options, xlim
from pytplot.MPLPlotter.tplot import get_var_label_ticks
from pytplot.options import options
from pytplot.tplot import tplot

from add_orb import add_orb
from get_uname_passwd import get_uname_passwd
from pwe_wfc_info import pwe_wfc_info


def load_ofa(trange=["2017-04-01/00:00:00", "2017-04-01/23:59:59"], no_update=False):
    uname1, passwd1 = get_uname_passwd()

    # Loading data and general option settings
    pwe_ofa(trange=trange, uname=uname1, passwd=passwd1, no_update=no_update)
    pwe_wfc_info(trange=trange, uname=uname1, passwd=passwd1, no_download=no_update)
    var_label_list = add_orb(
        mlt=True, mlat=True, alt=True, l=True, trange=trange, no_update=no_update
    )
    ofa_tplotlist = [
        "erg_pwe_ofa_l2_spec_E_spectra_132",
        "erg_pwe_ofa_l2_spec_B_spectra_132",
        "erg_pwe_wfc_l2_infostat_chorus",
        "erg_pwe_wfc_l2_infostat_swpia",
    ]
    return ofa_tplotlist, var_label_list


def plot_ofa_init(xsize: float = 12.8, ysize: float = 6) -> matplotlib.figure.Figure:
    # Figure size is 1280 x 600 (px)
    # In the case of dpi = 300
    # However, width of axes spines, ticks should be also managed for dpi = 300
    # factor = 1
    # In the case of dpi = 100
    fig = plt.figure(figsize=(xsize, ysize), facecolor="black")
    return fig


def _preprocess_var_label_panel(fig, variables, var_label_list):
    # All var labels are plotted as text inside a single subplot (a.k.a panel)
    # So define all panel sizes first
    num_panels = len(variables) + 1
    panel_sizes = [1] * len(variables) + [0.1 * (len(var_label_list) + 2)]
    for var_idx, variable in enumerate(variables):
        if pytplot.data_quants.get(variable) is None:
            continue
        panel_size = (
            pytplot.data_quants[variable]
            .attrs["plot_options"]["extras"]
            .get("panel_size")
        )
        if panel_size is not None:
            panel_sizes[var_idx] = panel_size

    fig.set_facecolor("white")
    gs = fig.add_gridspec(nrows=num_panels, height_ratios=panel_sizes)
    axes = gs.subplots(sharex=True)
    return fig, axes


def _postprocess_var_label_panel(variables, var_label_list, axes, fs):
    # Postprocess var label panel
    last_data_idx = len(variables) - 1
    last_data_axis = axes[last_data_idx]

    # List[float] (Number of days since epoch)
    xaxis_ticks = last_data_axis.get_xticks().tolist()

    # Get formatted time strings from Matplotlib
    # The format is not identical to IDL version
    # but is suitable for showing in Matplotlib
    # They are the same as xticklabels,
    # but xticklabels is initialized only after figure is drawn
    # So you need to directly use formatter to get the strings
    locator = last_data_axis.xaxis.get_major_locator()
    formatter = mpl.dates.ConciseDateFormatter(locator)
    # Ex. 12:34
    time_suffixes = formatter.format_ticks(xaxis_ticks)
    # Ex. 2017-Apr-01
    time_prefix = formatter.get_offset()

    # List[np.datetime64]
    xaxis_ticks_dt = [
        np.datetime64(mpl.dates.num2date(tick_val).isoformat())
        for tick_val in xaxis_ticks
    ]

    # Var label panel
    var_label_axis = axes[last_data_idx + 1]
    var_label_axis.spines["top"].set_visible(False)
    var_label_axis.spines["right"].set_visible(False)
    var_label_axis.spines["bottom"].set_visible(False)
    var_label_axis.spines["left"].set_visible(False)
    var_label_axis.tick_params(axis="x", which="both", length=0, labelbottom=False)
    var_label_axis.tick_params(axis="y", which="both", length=0, pad=fs * 3)
    var_label_axis.set_ylim(0, len(var_label_list) + 2)

    ys = []
    y_labels = []
    for i in range(len(var_label_list) + 2):
        y = len(var_label_list) + 2 - 0.5 - i
        # Time prefix (Ex. 2017-Apr-01) is plotted at y = 0.5 (bottom)
        if i == len(var_label_list) + 1:
            y_label = ""
            _, xmax = var_label_axis.get_xlim()
            var_label_axis.text(
                xmax, y, time_prefix, fontsize=fs, ha="right", va="center"
            )
        else:
            xmin, xmax = var_label_axis.get_xlim()
            # Time suffix (Ex. 12:34) is plotted at y = 1.5 (bottom)
            if i == len(var_label_list):
                y_label = ""
                xaxis_labels = time_suffixes
            # Other var labels are plotted above time suffix
            else:
                label = var_label_list[i]
                label_data = pytplot.get_data(label, xarray=True, dt=True)
                y_label = label_data.attrs["plot_options"]["yaxis_opt"]["axis_label"]
                xaxis_labels = get_var_label_ticks(label_data, xaxis_ticks_dt)

            for xaxis_tick, xaxis_label in zip(xaxis_ticks, xaxis_labels):
                # Sometimes ticks produced by locator can be outside xlim, so let exclude them
                if xmin <= xaxis_tick <= xmax:
                    var_label_axis.text(
                        xaxis_tick,
                        y,
                        xaxis_label,
                        fontsize=fs,
                        ha="center",
                        va="center",
                    )
            ys.append(y)
            y_labels.append(y_label)
    var_label_axis.set_yticks(ys, y_labels, ha="right")


def plot_ofa(
    fig: matplotlib.figure.Figure, trange, ofa_tplotlist, var_label_list
) -> matplotlib.figure.Figure:
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
    fs = 10
    tplot_options("charsize", fs)
    tplot_options("axis_font_size", fs)
    # In tplot(), xmargin is ineffective when specplot exists
    # plot_options("xmargin", [0.05, 0.05])
    tplot_options("ymargin", [0.05, 0.05])
    wfi = "erg_pwe_wfc_l2_infostat_"
    kinds = ["chorus", "emic", "efd", "swpia"]
    names = [wfi + kind for kind in kinds]
    for name in names:
        options(name, "marker_size", fs * 2)

    # Preprocess var panels
    fig, axes = _preprocess_var_label_panel(fig, ofa_tplotlist, var_label_list)

    # Then tplot
    fig, axes = tplot(
        ofa_tplotlist, return_plot_objects=True, fig=fig, axis=axes, display=False
    )

    # Postprocess var panels
    ax_e = axes[0]
    ax_e.collections[-1].colorbar.ax.yaxis.set_major_locator(
        ticker.LogLocator(base=10, numticks=10)
    )
    ax_b = axes[1]
    ax_b.collections[-1].colorbar.ax.yaxis.set_major_locator(
        ticker.LogLocator(base=10, numticks=10)
    )
    ax_chorus = axes[2]
    ax_chorus.set_yticks([1.5, 2.0, 2.5], [" ", "65k", " "])
    ax_swpia = axes[3]
    ax_swpia.set_yticks([0.5, 1.0, 1.5], [" ", "WP", " "])

    _postprocess_var_label_panel(ofa_tplotlist, var_label_list, axes, fs)
    return fig


if __name__ == "__main__":
    trange = ["2017-04-01/00:00:00", "2017-04-01/23:59:59"]
    ofa_tplotlist, var_label_list = load_ofa(no_update=False)
    fig = plot_ofa_init()
    fig = plot_ofa(fig, trange, ofa_tplotlist, var_label_list)
    plt.show()
