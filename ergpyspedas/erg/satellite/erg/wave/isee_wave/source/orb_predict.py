from typing import Sequence, Union

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
    trange=["2017-04-01/00:00:00", "2017-04-01/23:59:59"],
    datatype: Union[str, Sequence[str]] = "pre",
    level: str = "l2",
    get_support_data=False,
    downloadonly=False,
    no_download=False,
    uname=None,
    passwd=None,
):
    # NOTE: "l2" is only checked

    # Use only supported datatype
    supported_suffixes = ["pre", "spre", "mpre", "lpre"]
    suffixes = [d for d in datatype if d in supported_suffixes]

    for suffix in suffixes:
        # Download data
        remote_dir = CONFIG["remote_data_dir"] + "satellite/erg/orb/" + suffix + "/"
        local_dir = CONFIG["local_data_dir"] + "satellite/erg/orb/" + suffix + "/"
        relfpathfmt = "%Y/erg_orb_" + suffix + "_" + level + "_%Y%m%d_v??.cdf"
        relfpaths = dailynames(file_format=relfpathfmt, trange=trange)
        datfiles = download(
            remote_file=relfpaths,
            remote_path=remote_dir,
            local_path=local_dir,
            no_download=no_download,
            basic_auth=False,
            username=uname,
            password=passwd,
            last_version=True,
        )
        # Populate tplot variables
        prefix = "erg_orb_" + suffix + "_" + level + "_"
        if not downloadonly:
            cdf_to_tplot(datfiles, prefix=prefix, get_support_data=get_support_data)
        pytplot.data_quants[prefix + "pos_" + "gsm"].attrs["DATA_ATT"] = {
            "COORD_SYS": "gsm"
        }

        # Remove duplicates in time of time series data
        remove_duplicated_tframe(tnames("erg_orb_" + suffix + "_l2_*"))

        # options
        for s in ["gse", "gsm", "sm"]:
            options(prefix + "pos_" + s, "labels", ["X", "Y", "Z"])
            # TODO: is this original spedas color applies to python?
            options(prefix + "pos_" + s, "colors", [2, 4, 6])
        options(prefix + "pos_" + "rmlatmlt", "labels", ["Re", "MLAT", "MLT"])
        options(prefix + "pos_" + "rmlatmlt", "colors", [2, 4, 6])
        options(prefix + "pos_" + "eq", "labels", ["Req", "MLT"])
        for s in ["north", "south"]:
            options(prefix + "pos_iono_" + s, "labels", ["GLAT", "GLON"])
        options(prefix + "pos_blocal", "labels", ["X", "Y", "Z"])
        options(prefix + "pos_blocal", "colors", [2, 4, 6])
        # TODO: "B(model)!C_at_ERG" in SPEDAS and "!C" seems "\n" in Python
        options(prefix + "pos_blocal_mag", "labels", "B(model)\n_at_ERG")
        options(prefix + "pos_beq", "labels", ["X", "Y", "Z"])
        options(prefix + "pos_beq", "colors", [2, 4, 6])
        options(prefix + "pos_beq_mag", "labels", "B(model)\n_at_equator")
        for s in ["local", "eq"]:
            options(prefix + "pos_b" + s + "_mag", "ylog", 1)
        options(prefix + "pos_" + "Lm", "labels", ["90deg", "60deg", "30deg"])
        options(prefix + "pos_" + "Lm", "colors", [2, 4, 6])
        for s in ["gse", "gsm", "sm"]:
            options(prefix + "vel_" + s, "labels", ["X[km/s]", "Y[km/s]", "Z[km/s]"])
            options(prefix + "vel_" + s, "colors", [2, 4, 6])


if __name__ == "__main__":
    orb_predict()
