from enum import Enum, auto
from typing import Callable, List, Optional, Tuple

import numpy as np
from pyspedas.erg.satellite.erg.mgf.mgf import mgf
from pyspedas.erg.satellite.erg.pwe.pwe_wfc import pwe_wfc
from pyspedas.utilities.tnames import tnames
from pytplot import get_data, options, store_data, ylim, zlim
from pytplot.importers.tplot_restore import tplot_restore
from pytplot.tplot_math.join_vec import join_vec

from ..load.add_fc import add_fc
from ..utils.get_uname_passwd import get_uname_passwd


class MessageKind(Enum):
    information = auto()
    error = auto()
    warning = auto()


class Message:
    def __init__(self, content: str, kind: MessageKind) -> None:
        self.content = content
        self.kind = kind


def hanning(n: int, alpha: float = 0.5) -> np.ndarray:
    """Port of hanning function in IDL, which is different from NumPy one.

    Parameters
    ----------
    n : int
        Number of points in the output window.
        It must be n >= 1.
    alpha : float
        0.5 is for Hanning window, 0.54 is for Hamming window.
        It must be alpha >= 0.5 and alpha <= 1.

    Returns
    -------
    np.ndarray
        The window of shape (n,).

    Raises
    ------
    ValueError
        Raises ValueError if parameters are inappropriate.

    Examples
    --------
    >>> np.hanning(12)
    array([0.        , 0.07937323, 0.29229249, 0.57115742, 0.82743037,
           0.97974649, 0.97974649, 0.82743037, 0.57115742, 0.29229249,
           0.07937323, 0.        ])
    """
    if not isinstance(n, int):
        raise ValueError("n must be int")
    if not isinstance(alpha, float):
        raise ValueError("alpha must be float")
    if not n >= 1:
        raise ValueError("It must be n >= 1")
    if not (alpha >= 0.5 and alpha <= 1):
        raise ValueError("It must be alpha >= 0.5 and alpha <= 1")
    k = np.arange(0, n)
    return alpha - (1 - alpha) * np.cos(2 * np.pi * k / n)


def test_hanning():
    # results of hanning(12, /DOUBLE) in IDL
    result_idl = [
        0.0000000000000000,
        0.066987298107780646,
        0.24999999999999994,
        0.49999999999999994,
        0.74999999999999989,
        0.93301270189221919,
        1.0000000000000000,
        0.93301270189221941,
        0.75000000000000022,
        0.50000000000000011,
        0.25000000000000033,
        0.066987298107780813,
    ]
    assert np.allclose(result_idl, hanning(12))


def analysis_impl_dummy():
    # NOTE: Use this code to get analysis result from IDL version, if analysis part is not yet implemented
    # Please specify dummy_data_dir correctly if you use this function
    import os

    dummy_data_dir = os.getenv("WAVE_DUMMY_DATA_DIR", ".")
    if not (
        os.path.exists(os.path.join(dummy_data_dir, "espec.tplot"))
        and os.path.exists(os.path.join(dummy_data_dir, "bspec.tplot"))
        and os.path.exists(os.path.join(dummy_data_dir, "wna.tplot"))
        and os.path.exists(os.path.join(dummy_data_dir, "polarization.tplot"))
        and os.path.exists(os.path.join(dummy_data_dir, "planarity.tplot"))
        and os.path.exists(os.path.join(dummy_data_dir, "poyntingvec.tplot"))
    ):
        raise FileNotFoundError(
            f"Dummy data files do not exist in dir: {dummy_data_dir}"
        )

    tplot_restore(os.path.join(dummy_data_dir, "espec.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "bspec.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "wna.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "polarization.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "planarity.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "poyntingvec.tplot"))

    tplot_restore(os.path.join(dummy_data_dir, "espec_mask.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "bspec_mask.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "wna_mask.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "polarization_mask.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "planarity_mask.tplot"))
    tplot_restore(os.path.join(dummy_data_dir, "poyntingvec_mask.tplot"))

    espec = get_data("espec")
    bspec = get_data("bspec")
    wna = get_data("wna")
    polarization = get_data("polarization")
    planarity = get_data("planarity")
    poyntingvec = get_data("poyntingvec")

    ts_e = espec.times
    powspec_e = espec.y
    freq = espec.v
    ts_b = bspec.times
    powspec_b = bspec.y
    wna = wna.y
    polarization = polarization.y
    planarity = planarity.y
    theta = poyntingvec.y

    fsamp = 65536
    # TODO: "ystyle": 1 but not in python
    # This stands for decimal format (1, 10, ...) (vs scienfic notation (10^0, 10^1, ...))
    scwlim = {"spec": 1, "zlog": 1, "ylog": 1, "yrange": [0, fsamp / 2], "ystyle": 1}

    return (
        ts_e,
        powspec_e,
        freq,
        ts_b,
        powspec_b,
        wna,
        polarization,
        planarity,
        theta,
        scwlim,
    )


def analysis_impl(
    uname1, passwd1, trange, no_update, b_waveform, cancel_callback, update_callback
):
    # TODO: NU implement this function
    # Please add necessary arguments
    if not b_waveform:
        return (False, Message("No data found.", MessageKind.warning))

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )

    update_callback(30)

    mgf(uname=uname1, passwd=passwd1, trange=trange, no_update=no_update)

    if False:
        return (
            False,
            Message("Spacecraft attitude data not found.", MessageKind.information),
        )

    if False:
        return (
            False,
            Message("Spacecraft attitude data not found.", MessageKind.information),
        )

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(40)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(50)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(60)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(70)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(80)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(90)

    # TODO: must return those results
    # Please change the following dummy values to real values
    ts_e = np.zeros((252,))
    powspec_e = np.zeros((252, 2048))
    freq = np.zeros((2048,))
    ts_b = np.zeros((252,))
    powspec_b = np.zeros((252, 2048))
    wna = np.zeros((252, 2048))
    polarization = np.zeros((252, 2048))
    planarity = np.zeros((252, 2048))
    theta = np.zeros((252, 2048))
    fsamp = 65536
    scwlim = {"spec": 1, "zlog": 1, "ylog": 1, "yrange": [0, fsamp / 2], "ystyle": 1}

    return (
        ts_e,
        powspec_e,
        freq,
        ts_b,
        powspec_b,
        wna,
        polarization,
        planarity,
        theta,
        scwlim,
    )


def erg_calc_pwe_wna(
    trange: List[str] = ["2017-04-01/13:57:45", "2017-04-01/13:57:53"],
    w: str = "hanning",
    nfft: int = 4096,  # TODO: This value is the default of app, while 1024 is the real default of the corresponding function.
    stride: int = 2048,  # TODO: This value is the default of app, while 512 is the real default of the corresponding function.
    n_average: int = 3,
    cancel_callback: Callable[[], bool] = lambda: False,
    update_callback: Callable[[int], None] = lambda x: None,
    reload: bool = False,
    no_update: bool = False,
) -> Tuple[bool, Optional[Message]]:
    bw = 65536 / nfft

    if w == "hamming":
        alpha = 0.54
    elif w == "hanning":
        alpha = 0.5
    else:
        raise ValueError("w must be hamming or hanning")

    win = hanning(nfft, alpha=alpha) * 2

    uname1, passwd1 = get_uname_passwd()

    if reload:
        pwe_wfc(uname=uname1, passwd=passwd1, trange=trange, no_update=no_update)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(10)

    if tnames("erg_pwe_wfc_l2_b_65khz_Bx_waveform"):
        data = get_data("erg_pwe_wfc_l2_b_65khz_Bx_waveform")
        if data:
            join_vec(
                ["erg_pwe_wfc_l2_e_65khz_" + x + "_waveform" for x in ["Ex", "Ey"]],
                "E_waveform_sgi",
            )
            join_vec(
                [
                    "erg_pwe_wfc_l2_b_65khz_" + x + "_waveform"
                    for x in ["Bx", "By", "Bz"]
                ],
                "B_waveform_sgi",
            )
    else:
        if reload:
            # TODO: mode wp65khz is not yet available in python pwe_wfc
            pwe_wfc(
                uname=uname1,
                passwd=passwd1,
                mode="wp65khz",
                trange=trange,
                no_update=no_update,
            )

        if cancel_callback():
            return (
                False,
                Message("The user cancelled operation.", MessageKind.information),
            )
        update_callback(15)

        if tnames("erg_pwe_wfc_l2_b_wp65khz_Bx_waveform"):
            data = get_data("erg_pwe_wfc_l2_b_wp65khz_Bx_waveform")
            if data:
                join_vec(
                    [
                        "erg_pwe_wfc_l2_e_wp65khz_" + x + "_waveform"
                        for x in ["Ex", "Ey"]
                    ],
                    "E_waveform_sgi",
                )
                join_vec(
                    [
                        "erg_pwe_wfc_l2_b_wp65khz_" + x + "_waveform"
                        for x in ["Bx", "By", "Bz"]
                    ],
                    "B_waveform_sgi",
                )

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(20)

    store_data("erg_pwe_wfc_l2_*65khz_??_waveform", delete=True)

    e_waveform = get_data("E_waveform_sgi")
    store_data("E_waveform_sgi", delete=True)

    b_waveform = get_data("B_waveform_sgi")
    store_data("B_waveform_sgi", delete=True)

    # NOTE: Use this code to get analysis result from IDL version, if analysis part is not yet implemented
    (
        ts_e,
        powspec_e,
        freq,
        ts_b,
        powspec_b,
        wna,
        polarization,
        planarity,
        theta,
        scwlim,
    ) = analysis_impl_dummy()

    # # TODO: NU implement here
    # ret = analysis_impl(
    #     uname1, passwd1, trange, no_update, b_waveform, cancel_callback, update_callback
    # )
    # # This case ret is tuple of succeeded flag and message
    # if len(ret) == 2:
    #     return ret
    # # This case ret is data
    # else:
    #     (
    #         ts_e,
    #         powspec_e,
    #         freq,
    #         ts_b,
    #         powspec_b,
    #         wna,
    #         polarization,
    #         planarity,
    #         theta,
    #         scwlim,
    #     ) = ret

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )
    update_callback(100)

    # tplot settings
    store_data("espec", data={"x": ts_e, "y": powspec_e, "v": freq})
    store_data("bspec", data={"x": ts_b, "y": powspec_b, "v": freq})
    store_data("wna", data={"x": ts_b, "y": wna, "v": freq})
    store_data("polarization", data={"x": ts_b, "y": polarization, "v": freq})
    store_data("planarity", data={"x": ts_b, "y": planarity, "v": freq})
    store_data("poyntingvec", data={"x": ts_e, "y": theta, "v": freq})

    store_data("espec_mask", data={"x": ts_e, "y": powspec_e, "v": freq})
    store_data("bspec_mask", data={"x": ts_b, "y": powspec_b, "v": freq})
    store_data("wna_mask", data={"x": ts_b, "y": wna, "v": freq})
    store_data("polarization_mask", data={"x": ts_b, "y": polarization, "v": freq})
    store_data("planarity_mask", data={"x": ts_b, "y": planarity, "v": freq})
    store_data("poyntingvec_mask", data={"x": ts_e, "y": theta, "v": freq})

    add_fc(
        [
            "espec",
            "bspec",
            "wna",
            "polarization",
            "planarity",
            "poyntingvec",
        ],
        [],
        [],
        [],
        [],
        [],
        no_update=no_update,
    )

    # same options
    options("espec", "Spec", 1)
    options("bspec", "Spec", 1)
    options("wna", "Spec", 1)
    options("polarization", "Spec", 1)
    options("planarity", "Spec", 1)
    options("poyntingvec", "Spec", 1)
    options("espec_mask", "Spec", 1)
    options("bspec_mask", "Spec", 1)
    options("wna_mask", "Spec", 1)
    options("polarization_mask", "Spec", 1)
    options("planarity_mask", "Spec", 1)
    options("poyntingvec_mask", "Spec", 1)

    # ylabel
    options("espec", "ytitle", "E total")
    options("bspec", "ytitle", "B total")
    options("wna", "ytitle", "wave normal (polar)")
    options("polarization", "ytitle", "polarization")
    options("planarity", "ytitle", "planarity")
    options("poyntingvec", "ytitle", "Poynting vector")
    options("espec_mask", "ytitle", "E total")
    options("bspec_mask", "ytitle", "B total")
    options("wna_mask", "ytitle", "wave normal (polar)")
    options("polarization_mask", "ytitle", "polarization")
    options("planarity_mask", "ytitle", "planarity")
    options("poyntingvec_mask", "ytitle", "Poynting vector")

    # ysubtitle
    options("espec", "ysubtitle", "frequency [Hz]")
    options("bspec", "ysubtitle", "frequency [Hz]")
    options("wna", "ysubtitle", "frequency [Hz]")
    options("polarization", "ysubtitle", "frequency [Hz]")
    options("planarity", "ysubtitle", "frequency [Hz]")
    options("poyntingvec", "ysubtitle", "frequency [Hz]")
    options("espec_mask", "ysubtitle", "frequency [Hz]")
    options("bspec_mask", "ysubtitle", "frequency [Hz]")
    options("wna_mask", "ysubtitle", "frequency [Hz]")
    options("polarization_mask", "ysubtitle", "frequency [Hz]")
    options("planarity_mask", "ysubtitle", "frequency [Hz]")
    options("poyntingvec_mask", "ysubtitle", "frequency [Hz]")

    # zlabel
    options("espec", "ztitle", r"$[mV^2/m^2/Hz]$")
    options("bspec", "ztitle", r"$[pT^2/Hz]$")
    options("wna", "ztitle", "[degree]")
    options("polarization", "ztitle", "")
    options("planarity", "ztitle", "")
    options("poyntingvec", "ztitle", "[degree]")
    options("espec_mask", "ztitle", r"$[mV^2/m^2/Hz]$")
    options("bspec_mask", "ztitle", r"$[pT^2/Hz]$")
    options("wna_mask", "ztitle", "[degree]")
    options("polarization_mask", "ztitle", "")
    options("planarity_mask", "ztitle", "")
    options("poyntingvec_mask", "ztitle", "[degree]")

    # TODO: not in python yet
    # options, "espec*", "ztickunits", "scientific"
    # options, "bspec*", "ztickunits", "scientific"

    # ylim
    ylim("espec", 32, 20000)
    ylim("bspec", 32, 20000)
    ylim("wna", 32, 20000)
    ylim("polarization", 32, 20000)
    ylim("planarity", 32, 20000)
    ylim("poyntingvec", 32, 20000)
    ylim("espec_mask", 32, 20000)
    ylim("bspec_mask", 32, 20000)
    ylim("wna_mask", 32, 20000)
    ylim("polarization_mask", 32, 20000)
    ylim("planarity_mask", 32, 20000)
    ylim("poyntingvec_mask", 32, 20000)

    options("espec", "ylog", 1)
    options("bspec", "ylog", 1)
    options("wna", "ylog", 1)
    options("polarization", "ylog", 1)
    options("planarity", "ylog", 1)
    options("poyntingvec", "ylog", 1)
    options("espec_mask", "ylog", 1)
    options("bspec_mask", "ylog", 1)
    options("wna_mask", "ylog", 1)
    options("polarization_mask", "ylog", 1)
    options("planarity_mask", "ylog", 1)
    options("poyntingvec_mask", "ylog", 1)

    # zlim
    zlim("espec", 1e-9, 1e-2)
    zlim("bspec", 1e-4, 1e2)
    zlim("wna", 0, 90.0)
    zlim("polarization", -1, 1)
    zlim("planarity", 0, 1)
    zlim("poyntingvec", 0, 180)
    zlim("espec_mask", 1e-9, 1e-2)
    zlim("bspec_mask", 1e-4, 1e2)
    zlim("wna_mask", 0, 90.0)
    zlim("polarization_mask", -1, 1)
    zlim("planarity_mask", 0, 1)
    zlim("poyntingvec_mask", 0, 180)

    options("espec", "zlog", 1)
    options("bspec", "zlog", 1)
    options("wna", "zlog", 0)
    options("polarization", "zlog", 0)
    options("planarity", "zlog", 0)
    options("poyntingvec", "zlog", 0)
    options("espec_mask", "zlog", 1)
    options("bspec_mask", "zlog", 1)
    options("wna_mask", "zlog", 0)
    options("polarization_mask", "zlog", 0)
    options("planarity_mask", "zlog", 0)
    options("poyntingvec_mask", "zlog", 0)

    # TODO: not in python yet
    # ct
    # options, "polarization*", "color_table", 33
    # options, "planarity*", "color_table", 33

    # options, "wna*", "ztickinterval", 30.0
    # options, "polarization*", "ztickinterval", 0.5
    # options, "planarity*", "ztickinterval", 0.2
    # options, "poyntingvec*", "ztickinterval", 30.0

    return (True, None)


if __name__ == "__main__":
    # Usage example of erg_calc_pwe_wna
    succeeded, message = erg_calc_pwe_wna(
        trange=["2017-04-01/13:57:45", "2017-04-01/13:57:53"],
        w="hanning",
        nfft=4096,
        stride=2048,
        n_average=3,
        reload=True,
        no_update=False,
    )
    print(f"{succeeded}")
