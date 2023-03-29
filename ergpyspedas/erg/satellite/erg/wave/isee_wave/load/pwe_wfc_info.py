import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

import cdflib
import pytplot
from pyspedas.analysis.yclip import yclip
from pyspedas.erg.satellite.erg.config import CONFIG
from pyspedas.utilities.dailynames import dailynames
from pyspedas.utilities.download import download
from pyspedas.utilities.tnames import tnames
from pytplot import cdf_to_tplot, options, store_data


def _cdf_var_atts(path: str) -> Dict[str, Any]:
    cdf_file = cdflib.CDF(path)
    gatt = cdf_file.globalattsget()
    return gatt


def _make_group_data(wfi: str, group_type: str, nums: Sequence[int]) -> None:
    names = [wfi + f"0x{num}" for num in nums]
    group_name = wfi + group_type
    if any([tnames(name) for name in names]):
        store_data(group_name, data=names)
    else:
        store_data(group_name, data={"x": [0], "y": [0]})


def _print_ror(gatt: Dict[str, Any]) -> None:
    # Copied from pwe_wfc.py
    print(" ")
    print(" ")
    print("**************************************************************************")
    print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
    print("")
    print("Information about ERG PWE WFC")
    print("")
    print("PI: ", gatt["PI_NAME"])
    print("Affiliation: " + gatt["PI_AFFILIATION"])
    print("")
    print(
        "RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en"
    )
    print(
        "RoR of PWE/WFC: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Pwe/Wfc"
    )
    print("")
    print("Contact: erg_pwe_info at isee.nagoya-u.ac.jp")
    print("**************************************************************************")


def pwe_wfc_info(
    trange: Union[Sequence[str], Sequence[float], Sequence[datetime]] = [
        "2017-04-01/00:00:00",
        "2017-04-01/23:59:59",
    ],
    level: str = "l2",
    get_support_data: bool = False,
    no_download: bool = False,
    uname: Optional[str] = None,
    passwd: Optional[str] = None,
    ror: bool = True,
) -> List[str]:
    """The read program for Level-2 PWE/WFC-info data.

    Parameters
    ----------
    trange : Union[Sequence[str], Sequence[float], Sequence[datetime]], optional
        Set a time range to load data explicitly for the specified time range,
        by default [ "2017-04-01/00:00:00", "2017-04-01/23:59:59", ]
    level : str, optional
        Level of data products, only "l2" is tested, by default "l2"
    get_support_data : bool, optional
        Set to load support data in CDF data files, by default False
    no_download : bool, optional
        Set to prevent the program from searching in the remote server for data files,
        by default False
    uname : Optional[str], optional
        user ID to be passed to the remote server for authentication,
        by default None
    passwd : Optional[str], optional
        password to be passed to the remote server for authentication,
        by default None
    ror : bool, optional
        If set a string, rules of the road (RoR) for data products are
        displayed at your terminal, by default True

    Returns
    -------
    List[str]
        Downloaded tplot variables
    """
    # Download preparation
    relfpathfmt = "%Y/%m/erg_pwe_wfc_" + level + "_info_%Y%m%d_v??_??.cdf"
    relfpaths = dailynames(file_format=relfpathfmt, trange=trange)

    local_dir = CONFIG["local_data_dir"] + "satellite/erg/pwe/wfc/ancillary/info/"
    remote_dir = CONFIG["remote_data_dir"] + "satellite/erg/pwe/wfc/ancillary/info/"

    # Download data
    paths = download(
        remote_file=relfpaths,  # type: ignore
        remote_path=remote_dir,
        local_path=local_dir,
        no_download=no_download,
        basic_auth=False,
        username=uname,
        password=passwd,
        last_version=True,
    )
    datfiles = [path for path in paths if os.path.exists(path)]
    if len(datfiles) == 0:
        return []

    # Convert data to tplot variables
    prefix = "erg_pwe_wfc_l2_info"
    tvars = cdf_to_tplot(datfiles, prefix=prefix, get_support_data=get_support_data)

    # Note that wfi is different from IDL's erg_pwe_wfc_l2_info_stat_ (under bar between info and stat)
    wfi = "erg_pwe_wfc_l2_infostat_"
    nums = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 34, 35]
    names = [wfi + f"0x{num}" for num in nums]

    # Set options for each data
    for name in names:
        # NOTE: data_gap option is not yet available in PyTplot Matplotlib version
        # But is set for future support
        options(name, "data_gap", 10)
        # No lines but only markers
        options(name, "symbols", True)
        yclip(name, 0, 3, overwrite=True)
        # Remove zero value
        data_quant = pytplot.data_quants[name]
        mask = data_quant > 0
        pytplot.data_quants[name] = data_quant[mask]

    _make_group_data(wfi, "chorus", [20, 21, 24, 25])
    _make_group_data(wfi, "emic", [22, 23, 26, 27])
    _make_group_data(wfi, "efd", [28, 29])
    _make_group_data(wfi, "swpia", [34, 35])

    # Set options for each group of data
    options(wfi + "chorus", "yrange", [1.5, 2.5])
    options(wfi + "emic", "yrange", [1.5, 2.5])
    options(wfi + "efd", "yrange", [1.5, 2.5])
    options(wfi + "swpia", "yrange", [0.5, 1.5])

    kinds = ["chorus", "emic", "efd", "swpia"]
    names = [wfi + kind for kind in kinds]
    for name in names:
        # Means asterisk-shaped marker
        options(name, "marker", (6, 2, 0))
        # No lines but only markers
        options(name, "symbols", True)
        options(name, "panel_size", 0.1)
        # Option on ticks is generally not implemented in PyTplot Matplotlib version
        # So you have to specify equivalent option for Matplotlib methods
        # When you construct plot, not here
        # By the way, yticks means number of major yticks
        # options, wfi+'stat_*', yticks=2
        options(name, "ytitle", " ")

    # Print ror
    if ror:
        gatt = _cdf_var_atts(datfiles[0])
        _print_ror(gatt)

    # The next line is never used in IDL ISEE_Wave so ignored
    # erg_export_filever, datfiles
    return tvars


if __name__ == "__main__":
    pwe_wfc_info()
