from datetime import datetime
from typing import Any, List, Optional, Sequence, Union

import pytplot
from pyspedas.erg.satellite.erg.config import CONFIG
from pyspedas.erg.satellite.erg.orb.remove_duplicated_tframe import (
    remove_duplicated_tframe,
)
from pyspedas.utilities.dailynames import dailynames
from pyspedas.utilities.download import download
from pyspedas.utilities.tnames import tnames
from pytplot import cdf_to_tplot, options


def orb_predict(
    trange: Union[Sequence[str], Sequence[float], Sequence[datetime]] = [
        "2017-04-01/00:00:00",
        "2017-04-01/23:59:59",
    ],
    datatype: Union[str, Sequence[str]] = "pre",
    level: str = "l2",
    get_support_data: bool = False,
    downloadonly: bool = False,
    no_download: bool = False,
    uname: Optional[str] = None,
    passwd: Optional[str] = None,
) -> None:
    """The data read script for ERG Predicted Orbit data.

    Parameters
    ----------
    trange : Union[Sequence[str], Sequence[float], Sequence[datetime]], optional
        Set a time range to load data explicitly for the specified time range,
        by default [ "2017-04-01/00:00:00", "2017-04-01/23:59:59", ]
    datatype : Union[str, Sequence[str]], optional
        "spre": short-term predicted orbit,
        "mpre": middle-term predicted orbit,
        "lpre": long-term predicted orbit,
        "pre": short-term or long-term predicted orbit,
        by default "pre"
    level : str, optional
        "l2": Level-2, only "l2" is tested, by default "l2"
    get_support_data : bool, optional
        Set to load support data in CDF data files, by default False
    downloadonly : bool, optional
        Dwonload only, by default False
    no_download : bool, optional
        Set to prevent the program from searching in the remote server for data files,
        by default False
    uname : Optional[str], optional
        user ID to be passed to the remote server for authentication,
        by default None
    passwd : Optional[str], optional
        password to be passed to the remote server for authentication,
        by default None
    """
    # Used orb.py as reference

    # Use supported datatype only
    if isinstance(datatype, str):
        datatype = [datatype]
    supported_suffixes = ["pre", "spre", "mpre", "lpre"]
    suffixes = [d for d in datatype if d in supported_suffixes]

    for suffix in suffixes:
        # Download data
        remote_dir = CONFIG["remote_data_dir"] + "satellite/erg/orb/" + suffix + "/"
        local_dir = CONFIG["local_data_dir"] + "satellite/erg/orb/" + suffix + "/"
        relfpathfmt = "%Y/erg_orb_" + suffix + "_" + level + "_%Y%m%d_v??.cdf"
        relfpaths = dailynames(file_format=relfpathfmt, trange=trange)
        if relfpaths is None:
            continue
        datfiles: Optional[List[Any]] = download(
            remote_file=relfpaths,  # type: ignore
            remote_path=remote_dir,
            local_path=local_dir,
            no_download=no_download,
            basic_auth=False,
            username=uname,
            password=passwd,
            last_version=True,
        )
        if datfiles is None:
            continue
        # Populate tplot variables
        prefix = "erg_orb_" + suffix + "_" + level + "_"
        if not downloadonly:
            cdf_to_tplot(datfiles, prefix=prefix, get_support_data=get_support_data)
        data = pytplot.data_quants.get(prefix + "pos_gsm")
        if data is not None:
            data.attrs["data_att"] = {"coord_sys": "gsm"}

        # Remove time duplicates in data
        remove_duplicated_tframe(tnames("erg_orb_" + suffix + "_l2_*"))

        # Options
        for s in ["gse", "gsm", "sm"]:
            options(prefix + "pos_" + s, "legend_names", ["X", "Y", "Z"])
            options(prefix + "pos_" + s, "Color", ["b", "g", "r"])
        options(prefix + "pos_rmlatmlt", "legend_names", ["Re", "MLAT", "MLT"])
        options(prefix + "pos_rmlatmlt", "Color", ["b", "g", "r"])
        options(prefix + "pos_eq", "legend_names", ["Req", "MLT"])
        for s in ["north", "south"]:
            options(prefix + "pos_iono_" + s, "legend_names", ["GLAT", "GLON"])
        options(prefix + "pos_blocal", "legend_names", ["X", "Y", "Z"])
        options(prefix + "pos_blocal", "Color", ["b", "g", "r"])
        options(prefix + "pos_blocal_mag", "legend_names", "B(model)_at_ERG")
        options(prefix + "pos_beq", "legend_names", ["X", "Y", "Z"])
        options(prefix + "pos_beq", "Color", ["b", "g", "r"])
        options(prefix + "pos_beq_mag", "legend_names", "B(model)_at_equator")
        for s in ["local", "eq"]:
            options(prefix + "pos_b" + s + "_mag", "ylog", 1)
        options(prefix + "pos_Lm", "legend_names", ["90deg", "60deg", "30deg"])
        options(prefix + "pos_Lm", "Color", ["b", "g", "r"])
        for s in ["gse", "gsm", "sm"]:
            options(
                prefix + "vel_" + s, "legend_names", ["X[km/s]", "Y[km/s]", "Z[km/s]"]
            )
            options(prefix + "vel_" + s, "Color", ["b", "g", "r"])


if __name__ == "__main__":
    orb_predict()
