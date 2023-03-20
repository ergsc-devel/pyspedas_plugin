import gc
import math
from enum import Enum, auto
from typing import Callable, List, Optional, Tuple

import numpy as np
from pyspedas.analysis.tinterpol import tinterpol
from pyspedas.erg.satellite.erg.mgf.mgf import mgf
from pyspedas.utilities.tnames import tnames
from pytplot import get_data, options, split_vec, store_data, ylim, zlim
from pytplot.importers.tplot_restore import tplot_restore
from pytplot.tplot_math.join_vec import join_vec

# Use bugfixed below now instead of: from pyspedas.erg.satellite.erg.pwe.pwe_wfc import pwe_wfc
from ergpyspedas.erg import pwe_wfc
from ergpyspedas.erg.satellite.erg.common.cotrans.erg_cotrans import erg_cotrans

from ..utils.get_uname_passwd import get_uname_passwd
from .add_fc import add_fc


class MessageKind(Enum):
    error = auto()
    information = auto()
    question = auto()
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


def value_locate(refx, x):
    refx = np.array(refx)
    x = np.array(x)
    loc = np.zeros(len(x), dtype="int")
    for i in range(len(x)):
        ix = x[i]
        ind = ((refx - ix) <= 0).nonzero()[0]
        if len(ind) == 0:
            loc[i] = -1
        else:
            loc[i] = ind[-1]
    return loc


def nn2(time1, time2):
    w = value_locate(time1, time2)
    w1 = np.minimum(np.maximum(w, np.zeros(w.size)), np.full(w.size, time1.size - 1))
    w2 = np.minimum(
        np.maximum(w1 + 1, np.zeros(w.size)), np.full(w.size, time1.size - 1)
    )

    dt1 = np.abs(time2 - time1[w1.astype("int64")])
    dt2 = np.abs(time2 - time1[w2.astype("int64")])
    w = np.concatenate([w1, w2])

    dt = [dt1, dt2]
    imin = np.arange(dt1.size) + np.argmin([dt], axis=1).reshape(dt1.size) * 3
    n2 = w[imin.astype("int64")]

    return n2.astype("int64")


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
    uname1,
    passwd1,
    trange,
    no_update,
    win,
    nfft,
    stride,
    n_average,
    e_waveform,
    b_waveform,
    cancel_callback,
    update_callback,
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

    if not e_waveform:
        start_time = b_waveform.times[0]
        end_time = b_waveform.x[-1]
        # return (False, Message("No data found.", MessageKind.warning))
    else:
        if e_waveform.times[0] >= b_waveform.times[0]:
            start_time = b_waveform.times[0]
            offset_e = (e_waveform.times[0] - b_waveform.times[0]) / (
                e_waveform.times[1] - e_waveform.times[0]
            )
            offset_b = 0.0
        else:
            start_time = e_waveform.times[0]
            offset_e = 0.0
            offset_b = (b_waveform.times[0] - e_waveform.times[0]) / (
                b_waveform.times[1] - b_waveform.times[0]
            )

        if e_waveform.times[-1] < b_waveform.times[-1]:
            end_time = b_waveform.times[-1]
        else:
            end_time = e_waveform.times[-1]

    ndata = math.floor(
        (end_time - start_time) / (b_waveform.times[1] - b_waveform.times[0])
    )
    e_waveform_fft = np.full(
        (math.floor((ndata - nfft) / stride) + 1, nfft, 3), np.nan, dtype=complex
    )
    b_waveform_fft = np.full(
        (math.floor((ndata - nfft) / stride) + 1, nfft, 3), np.nan, dtype=complex
    )
    e_waveform_t = np.full(math.floor((ndata - nfft) / stride) + 1, np.nan)
    b_waveform_t = np.full(math.floor((ndata - nfft) / stride) + 1, np.nan)
    e_waveform_fft[:, :, :] = np.nan
    b_waveform_fft[:, :, :] = np.nan

    ts_e = start_time + (
        b_waveform.times[1] - b_waveform.times[0]
    ) * stride * np.arange(math.floor((ndata - nfft) / stride) + 1 - n_average + 1)
    ts_b = ts_e

    n = e_waveform.times.size - nfft - 1
    for j in range(int(-offset_e), ndata - nfft, stride):
        if j < 0:
            continue
        if j >= n:
            continue

        i = math.floor(
            (e_waveform.times[j] - start_time)
            / stride
            / (b_waveform.times[1] - b_waveform.times[0])
        )
        if i >= math.floor((ndata - nfft) / stride) + 1:
            continue

        for k in range(2):
            e_waveform_fft[i, :, k] = (
                np.fft.fft(e_waveform.y[j : j + nfft, k] * win) / nfft
            )

        e_waveform_t[i] = e_waveform.times[j]

    n = b_waveform.times.size - nfft - 1
    for j in range(int(-offset_b), ndata - nfft, stride):
        if j < 0:
            continue
        if j >= n:
            continue

        i = math.floor(
            (b_waveform.times[j] - start_time)
            / stride
            / (b_waveform.times[1] - b_waveform.times[0])
        )
        if i >= math.floor((ndata - nfft) / stride) + 1:
            continue

        for k in range(3):
            b_waveform_fft[i, :, k] = (
                np.fft.fft(b_waveform.y[j : j + nfft, k] * win) / nfft
            )

        b_waveform_t[i] = b_waveform.times[j]

    fsamp = 65536.0
    freq = np.arange(nfft / 2) * fsamp / nfft
    bw = fsamp / nfft

    update_callback(30)

    # *****************
    # load MGF L2 CDF
    # *****************
    mgf(uname=uname1, passwd=passwd1, trange=trange, no_update=no_update)

    tinterpol(
        "erg_mgf_l2_mag_8sec_dsi",
        ts_e,
        method=None,
        newname="erg_mgf_l2_mag_8sec_dsi_interp_e",
        suffix=None,
    )
    erg_cotrans(
        in_name="erg_mgf_l2_mag_8sec_dsi_interp_e",
        out_name="erg_mgf_l2_mag_8sec_sgi_e",
        in_coord="dsi",
        out_coord="sgi",
        noload=False,
    )
    split_vec("erg_mgf_l2_mag_8sec_sgi_e")

    tinterpol(
        "erg_mgf_l2_mag_8sec_dsi",
        ts_b,
        method=None,
        newname="erg_mgf_l2_mag_8sec_dsi_interp_b",
        suffix=None,
    )
    erg_cotrans(
        in_name="erg_mgf_l2_mag_8sec_dsi_interp_b",
        out_name="erg_mgf_l2_mag_8sec_sgi_b",
        in_coord="dsi",
        out_coord="sgi",
        noload=False,
    )
    split_vec("erg_mgf_l2_mag_8sec_sgi_b")

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

    store_data("erg_mgf_l2_mag_8sec_dsi_interp_?", delete=True)
    store_data("erg_att_*", delete=True)

    # *****************
    # calc Ez
    # *****************
    eueu = np.full((ts_e.size, freq.size), np.nan, dtype=complex)
    evev = np.full((ts_e.size, freq.size), np.nan, dtype=complex)
    powspec_e = np.full((ts_e.size, freq.size), np.nan, dtype=complex)

    c_ex = e_waveform_fft[:, 0 : int(nfft / 2), 0] * 1e-3
    c_ey = e_waveform_fft[:, 0 : int(nfft / 2), 1] * 1e-3
    c_bx = b_waveform_fft[:, 0 : int(nfft / 2), 0] * 1e-12
    c_by = b_waveform_fft[:, 0 : int(nfft / 2), 1] * 1e-12
    c_bz = b_waveform_fft[:, 0 : int(nfft / 2), 2] * 1e-12

    c_ez = np.full((ts_e.size, freq.size), np.nan, dtype=complex)
    idx = nn2(b_waveform_t, ts_e)

    for i in range(ts_e.size):
        c_ez[i, :] = (
            -c_ex[i, :] * c_bx[idx[i], :] - c_ey[i, :] * c_by[idx[i], :]
        ) / c_bz[idx[i], :]

    Sx = np.full((ts_e.size, freq.size), np.nan)
    Sy = np.full((ts_e.size, freq.size), np.nan)
    Sz = np.full((ts_e.size, freq.size), np.nan)
    gap = np.full((ts_e.size), np.nan)

    # calc Poynting flux
    idx = nn2(e_waveform_t, b_waveform_t)
    gap = b_waveform_t - e_waveform_t[idx]

    for i in range(ts_e.size):
        if (
            i >= ts_b.size
            or i >= ts_e.size
            or idx[i] >= ts_b.size
            or idx[i] >= ts_e.size
        ):
            Sx[i, :] = np.nan
            Sy[i, :] = np.nan
            Sz[i, :] = np.nan
            continue

        if np.abs(gap[i]) > 0.0001:
            Sx[i, :] = np.nan
            Sy[i, :] = np.nan
            Sz[i, :] = np.nan
        else:
            Sx[i, :] = c_ey[idx[i], :] * np.conj(c_bz[i, :]) - c_ez[
                idx[i], :
            ] * np.conj(c_by[i, :])
            Sy[i, :] = (-1.0) * (
                c_ex[idx[i], :] * np.conj(c_bz[i, :])
                - c_ez[idx[i], :] * np.conj(c_bx[i, :])
            )
            Sz[i, :] = c_ex[idx[i], :] * np.conj(c_by[i, :]) - c_ey[
                idx[i], :
            ] * np.conj(c_bx[i, :])

    # *****************
    # calc E power spec
    # *****************
    npt = ts_e.size
    for i in range(ts_e.size):
        for j in range(freq.size - 1):
            indx = i + np.arange(n_average) - 1
            eueu[i, j] = np.sum(
                e_waveform_fft[indx, j, 0] * np.conj(e_waveform_fft[indx, j, 0])
            )
            evev[i, j] = np.sum(
                e_waveform_fft[indx, j, 1] * np.conj(e_waveform_fft[indx, j, 1])
            )

    eueu /= bw * n_average
    evev /= bw * n_average
    powspec_e = np.sqrt(np.real(eueu) ** 2 + np.real(evev) ** 2)

    # free allocated memory
    del eueu, evev
    gc.collect()

    update_callback(40)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )

    # *****************
    # Calc. spectral matrix
    # *****************
    npt = ts_b.size
    freq = np.arange(nfft / 2.0) * fsamp / nfft

    # scwlim={spec:1,zlog:1,ylog:0,yrange:[0,fsamp/2],ystyle:1}
    # bubu = bubv = bubw = bvbu = bvbv = bvbw = bwbu = bwbv = bwbw = np.full((npt, freq.size), np.nan, dtype=complex)
    bubu = np.full((npt, freq.size), np.nan, dtype=complex)
    bubv = np.full((npt, freq.size), np.nan, dtype=complex)
    bubw = np.full((npt, freq.size), np.nan, dtype=complex)
    bvbu = np.full((npt, freq.size), np.nan, dtype=complex)
    bvbv = np.full((npt, freq.size), np.nan, dtype=complex)
    bvbw = np.full((npt, freq.size), np.nan, dtype=complex)
    bwbu = np.full((npt, freq.size), np.nan, dtype=complex)
    bwbv = np.full((npt, freq.size), np.nan, dtype=complex)
    bwbw = np.full((npt, freq.size), np.nan, dtype=complex)

    for i in range(ts_b.size):
        for j in range(freq.size - 1):
            indx = i + np.arange(n_average) - 1

            bubu[i, j] = np.sum(
                b_waveform_fft[indx, j, 0] * np.conj(b_waveform_fft[indx, j, 0])
            )
            bubv[i, j] = np.sum(
                b_waveform_fft[indx, j, 0] * np.conj(b_waveform_fft[indx, j, 1])
            )
            bubw[i, j] = np.sum(
                b_waveform_fft[indx, j, 0] * np.conj(b_waveform_fft[indx, j, 2])
            )

            bvbv[i, j] = np.sum(
                b_waveform_fft[indx, j, 1] * np.conj(b_waveform_fft[indx, j, 1])
            )
            bvbw[i, j] = np.sum(
                b_waveform_fft[indx, j, 1] * np.conj(b_waveform_fft[indx, j, 2])
            )

            bwbw[i, j] = np.sum(
                b_waveform_fft[indx, j, 2] * np.conj(b_waveform_fft[indx, j, 2])
            )

    bubu /= bw * n_average
    bubv /= bw * n_average
    bubw /= bw * n_average
    bvbv /= bw * n_average
    bvbw /= bw * n_average
    bwbw /= bw * n_average
    bvbu = np.conj(bubv)
    bwbu = np.conj(bubw)
    bwbv = np.conj(bvbw)

    r = np.full((3, 3, ts_b.size, freq.size, 2), np.nan)
    rr = np.full((3, 3, ts_b.size, freq.size, 2), np.nan)

    rr[0, 0, :, :, 0] = np.real(bubu)
    rr[1, 0, :, :, 0] = np.real(bubv)
    rr[2, 0, :, :, 0] = np.real(bubw)
    rr[0, 1, :, :, 0] = np.real(bvbu)
    rr[1, 1, :, :, 0] = np.real(bvbv)
    rr[2, 1, :, :, 0] = np.real(bvbw)
    rr[0, 2, :, :, 0] = np.real(bwbu)
    rr[1, 2, :, :, 0] = np.real(bwbv)
    rr[2, 2, :, :, 0] = np.real(bwbw)

    rr[0, 0, :, :, 1] = np.imag(bubu)
    rr[1, 0, :, :, 1] = np.imag(bubv)
    rr[2, 0, :, :, 1] = np.imag(bubw)
    rr[0, 1, :, :, 1] = np.imag(bvbu)
    rr[1, 1, :, :, 1] = np.imag(bvbv)
    rr[2, 1, :, :, 1] = np.imag(bvbw)
    rr[0, 2, :, :, 1] = np.imag(bwbu)
    rr[1, 2, :, :, 1] = np.imag(bwbv)
    rr[2, 2, :, :, 1] = np.imag(bwbw)

    # free allocated memory
    del bubu, bubv, bubw, bvbu, bvbv, bvbw, bwbu, bwbv, bwbw
    gc.collect()

    update_callback(50)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )

    # *****************
    # Calc. rotation matrix
    # *****************
    name_mgf1 = "erg_mgf_l2_mag_8sec_sgi_b"
    data_x = get_data(name_mgf1 + "_x")
    data_y = get_data(name_mgf1 + "_y")
    data_z = get_data(name_mgf1 + "_z")

    rotmat = rotmat_t = np.full((ts_b.size, 3, 3), np.nan)

    # MGF rotation (crossp)
    for i in range(ts_b.size):
        bvec = np.array([[data_x.y[i]], [data_y.y[i]], [data_z.y[i]]]).T
        zz = [0.0, 0.0, 1.0]

        yhat = np.cross(zz, bvec)
        xhat = np.cross(yhat, bvec)
        zhat = bvec

        xhat = xhat / np.sqrt(xhat[0, 0] ** 2 + xhat[0, 1] ** 2 + xhat[0, 2] ** 2)
        yhat = yhat / np.sqrt(yhat[0, 0] ** 2 + yhat[0, 1] ** 2 + yhat[0, 2] ** 2)
        zhat = zhat / np.sqrt(zhat[0, 0] ** 2 + zhat[0, 1] ** 2 + zhat[0, 2] ** 2)

        rotmat[i, :, :] = np.reshape([[xhat], [yhat], [zhat]], [3, 3])
        rotmat_t[
            i,
            :,
        ] = np.transpose(np.reshape([[xhat], [yhat], [zhat]], [3, 3]))

    # *****************
    # Matrix rotation
    # *****************
    for i in range(ts_b.size):
        for j in range(freq.size - 1):
            for k in range(2):
                r[:, :, i, j, k] = np.dot(
                    np.reshape(np.array([rotmat[i, :, :]]).T, [3, 3]), rr[:, :, i, j, k]
                )
                rr[:, :, i, j, k] = np.dot(
                    r[:, :, i, j, k], np.reshape(rotmat_t[i, :, :], [3, 3])
                )

    # free allocated memory
    del rotmat, rotmat_t
    gc.collect()

    update_callback(60)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )

    # *****************
    # SVD analysis
    # *****************
    A = np.full((3, 6, npt, freq.size), np.nan)
    W2 = np.full((3, npt, freq.size), np.nan)
    W_SORT = np.full((3, npt, freq.size), np.nan)
    V2 = np.full((3, 3, npt, freq.size), np.nan)
    V_SORT = np.full((3, 3, npt, freq.size), np.nan)

    A[0, 0, :, :] = rr[0, 0, :, :, 0]
    A[1, 0, :, :] = rr[1, 0, :, :, 0]
    A[2, 0, :, :] = rr[2, 0, :, :, 0]

    A[0, 1, :, :] = rr[1, 0, :, :, 0]
    A[1, 1, :, :] = rr[1, 1, :, :, 0]
    A[2, 1, :, :] = rr[2, 1, :, :, 0]

    A[0, 2, :, :] = rr[2, 0, :, :, 0]
    A[1, 2, :, :] = rr[2, 1, :, :, 0]
    A[2, 2, :, :] = rr[2, 2, :, :, 0]

    A[0, 3, :, :] = 0.0
    A[1, 3, :, :] = -rr[1, 0, :, :, 1]
    A[2, 3, :, :] = -rr[2, 0, :, :, 1]

    A[0, 4, :, :] = rr[1, 0, :, :, 1]
    A[1, 4, :, :] = 0.0
    A[2, 4, :, :] = -rr[2, 1, :, :, 1]

    A[0, 5, :, :] = rr[2, 0, :, :, 1]
    A[1, 5, :, :] = rr[2, 1, :, :, 1]
    A[2, 5, :, :] = 0.0

    for i in range(ts_b.size):
        for j in range(freq.size - 1):
            if np.isnan(A[:, :, i, j]).any() == True:
                continue

            if np.isinf(A[:, :, i, j]).any() == True:
                continue

            U, W, V = np.linalg.svd(np.array([np.array(A[:, :, i, j]).T]))

            W2[:, i, j] = W
            V2[:, :, i, j] = np.reshape(V, [3, 3]).T
            W_ORDER = np.argsort(W2[:, i, j])

            for k in range(3):
                W_SORT[k, i, j] = W2[W_ORDER[k], i, j]
                V_SORT[k, :, i, j] = V2[W_ORDER[k], :, i, j]

    update_callback(70)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )

    # *****************
    # Calc. WNA & Polarization
    # *****************
    powspec_b = np.full((ts_b.size, freq.size), np.nan)
    wna = np.full((ts_b.size, freq.size), np.nan)
    wna_azm = np.full((ts_b.size, freq.size), np.nan)
    polarization = np.full((ts_b.size, freq.size), np.nan)
    planarity = np.full((ts_b.size, freq.size), np.nan)

    for i in range(ts_b.size):
        for j in range(freq.size - 1):
            # power spec
            powspec_b[i, j] = np.sqrt(
                A[0, 0, i, j] ** 2 + A[1, 1, i, j] ** 2 + A[2, 2, i, j] ** 2
            )

            # wave normal
            wna[i, j] = np.abs(
                np.degrees(
                    np.arctan(
                        np.sqrt(V_SORT[0, 0, i, j] ** 2 + V_SORT[0, 1, i, j] ** 2)
                        / V_SORT[0, 2, i, j]
                    )
                )
            )
            wna_azm[i, j] = np.degrees(
                np.arctan2(V_SORT[0, 1, i, j], V_SORT[0, 0, i, j])
            )

            # polarization
            polarization[i, j] = W_SORT[1, i, j] / W_SORT[2, i, j]
            if rr[1, 0, i, j, 1] < 0.0:
                polarization[i, j] *= -1.0

            # planarity
            planarity[i, j] = 1.0 - np.sqrt(W_SORT[0, i, j] / W_SORT[2, i, j])

    # free allocated memory
    del r, rr
    del A, W2, V2, W_SORT, V_SORT
    gc.collect()

    update_callback(80)

    if cancel_callback():
        return (
            False,
            Message("The user cancelled operation.", MessageKind.information),
        )

    # *****************
    # Poynting vector calculation
    # *****************
    name_mgf1 = "erg_mgf_l2_mag_8sec_sgi_e"
    data_x = get_data(name_mgf1 + "_x")
    data_y = get_data(name_mgf1 + "_y")
    data_z = get_data(name_mgf1 + "_z")
    store_data("erg_mgf_l2_*", delete=True)

    rotmat = np.full((ts_b.size, 3, 3), np.nan)

    # MGF rotation (crossp)
    for i in range(data_x.times.size):
        bvec = np.array([[data_x.y[i]], [data_y.y[i]], [data_z.y[i]]]).T
        zz = [0.0, 0.0, 1.0]

        yhat = np.cross(zz, bvec)
        xhat = np.cross(yhat, bvec)
        zhat = bvec

        xhat = xhat / np.sqrt(xhat[0, 0] ** 2 + xhat[0, 1] ** 2 + xhat[0, 2] ** 2)
        yhat = yhat / np.sqrt(yhat[0, 0] ** 2 + yhat[0, 1] ** 2 + yhat[0, 2] ** 2)
        zhat = zhat / np.sqrt(zhat[0, 0] ** 2 + zhat[0, 1] ** 2 + zhat[0, 2] ** 2)

        rotmat[i, :, :] = np.reshape([[xhat], [yhat], [zhat]], [3, 3])

    S = np.full((ts_e.size, freq.size, 3), np.nan)

    for i in range(ts_e.size):
        for j in range(freq.size):
            S[i, j, :] = np.dot(
                np.array([rotmat[i, :, :]]), [Sx[i, j], Sy[i, j], Sz[i, j]]
            )

    theta = np.degrees(
        np.arccos(
            S[:, :, 2] / np.sqrt(S[:, :, 0] ** 2 + S[:, :, 1] ** 2 + S[:, :, 2] ** 2)
        )
    )

    # free allocated memory
    del Sx, Sy, Sz, rotmat
    gc.collect()

    update_callback(90)

    # TODO: must return those results
    # Please change the following dummy values to real values
    # ts_e = np.zeros((252,))
    # powspec_e = np.zeros((252, 2048))
    # freq = np.zeros((2048,))
    # ts_b = np.zeros((252,))
    # powspec_b = np.zeros((252, 2048))
    # wna = np.zeros((252, 2048))
    # polarization = np.zeros((252, 2048))
    # planarity = np.zeros((252, 2048))
    # theta = np.zeros((252, 2048))
    # fsamp = 65536
    scwlim = {"spec": 1, "zlog": 1, "ylog": 1, "yrange": [0, fsamp / 2], "ystyle": 1}

    # temp
    np.nan_to_num(powspec_e)
    np.nan_to_num(powspec_b)
    np.nan_to_num(wna)
    np.nan_to_num(polarization)
    np.nan_to_num(planarity)
    np.nan_to_num(theta)

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
    w: str = "Hanning",
    nfft: int = 4096,  # TODO: This value is the default of app, while 1024 is the real default of the corresponding function.
    stride: int = 2048,  # TODO: This value is the default of app, while 512 is the real default of the corresponding function.
    n_average: int = 3,
    cancel_callback: Callable[[], bool] = lambda: False,
    update_callback: Callable[[int], None] = lambda x: None,
    reload: bool = False,
    no_update: bool = False,
) -> Tuple[bool, Optional[Message]]:
    bw = 65536 / nfft

    if w == "Hamming":
        alpha = 0.54
    elif w == "Hanning":
        alpha = 0.5
    else:
        raise ValueError("w must be Hamming or Hanning")

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
    # (
    #     ts_e,
    #     powspec_e,
    #     freq,
    #     ts_b,
    #     powspec_b,
    #     wna,
    #     polarization,
    #     planarity,
    #     theta,
    #     scwlim,
    # ) = analysis_impl_dummy()

    # # TODO: NU implement here
    ret = analysis_impl(
        uname1,
        passwd1,
        trange,
        no_update,
        win,
        nfft,
        stride,
        n_average,
        e_waveform,
        b_waveform,
        cancel_callback,
        update_callback,
    )
    # This case ret is tuple of succeeded flag and message
    if len(ret) == 2:
        return ret
    # This case ret is data
    else:
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
        ) = ret

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
        w="Hanning",
        nfft=4096,
        stride=2048,
        n_average=3,
        reload=True,
        no_update=False,
    )
    print(f"{succeeded}")
