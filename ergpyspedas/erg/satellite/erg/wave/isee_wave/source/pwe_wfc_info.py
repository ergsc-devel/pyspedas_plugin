import os
from typing import Any, Dict, Sequence

import cdflib
import pytplot
from pyspedas.analysis.yclip import yclip
from pyspedas.erg.satellite.erg.config import CONFIG
from pyspedas.utilities.dailynames import dailynames
from pyspedas.utilities.download import download
from pyspedas.utilities.tnames import tnames
from pytplot import cdf_to_tplot, options, store_data, ylim


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
        # TODO: do you really need this?
        store_data(group_name, data={"x": [0], "y": [0]})


def _print_ror(gatt: Dict[str, Any]) -> None:
    # NOTE: copied from pwe_wfc.py
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
    trange=["2017-04-01/00:00:00", "2017-04-01/23:59:59"],
    level="l2",
    get_support_data=False,
    no_download=False,
    uname=None,
    passwd=None,
    ror=True,
) -> None:
    # Download preparation
    relfpathfmt = "%Y/%m/erg_pwe_wfc_" + level + "_info_%Y%m%d_v??_??.cdf"
    relfpaths = dailynames(file_format=relfpathfmt, trange=trange)

    local_dir = CONFIG["local_data_dir"] + "satellite/erg/pwe/wfc/ancillary/info/"
    remote_dir = CONFIG["remote_data_dir"] + "satellite/erg/pwe/wfc/ancillary/info/"

    # Download data
    paths = download(
        remote_file=relfpaths,
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
        print("No file is loaded.")
        return

    # Convert data to tplot variables
    prefix = "erg_pwe_wfc_l2_info"
    cdf_to_tplot(datfiles, prefix=prefix, get_support_data=get_support_data)

    wfi = "erg_pwe_wfc_l2_infostat_"
    nums = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 34, 35]
    names = [wfi + f"0x{num}" for num in nums]
    for name in names:
        # TODO: datagap is not yet in python -> data_gap exists!
        # スペクトルプロットでのデータ欠損埋めの制御 (datagap)
        # https://github.com/spedas-j/member_contrib/wiki/spedas_tips#section13
        # seems only in Bokeh
        options(name, "data_gap", 10)
        options(name, "symbols", True)
        yclip(name, 0, 3, overwrite=True)
        # remove zero value
        data_quant = pytplot.data_quants[name]
        mask = data_quant > 0
        pytplot.data_quants[name] = data_quant[mask]

    _make_group_data(wfi, "chorus", [20, 21, 24, 25])
    _make_group_data(wfi, "emic", [22, 23, 26, 27])
    _make_group_data(wfi, "efd", [28, 29])
    _make_group_data(wfi, "swpia", [34, 35])

    options(wfi + "chorus", "yrange", [1.5, 2.5])
    options(wfi + "emic", "yrange", [1.5, 2.5])
    options(wfi + "efd", "yrange", [1.5, 2.5])
    options(wfi + "swpia", "yrange", [0.5, 1.5])

    # TODO: check maybe tickname option is not implemented
    # options(wfi + "chorus", "ytickname", [" ", "65k", " "])
    # TODO: panel_size etc options also be not existing
    # names = tnames(wfi + "*")
    # tnames of group results in "group data from element1, ...""
    # do you have to option all 0xXX values as well?
    kinds = ["chorus", "emic", "efd", "swpia"]
    names = [wfi + kind for kind in kinds]
    for name in names:
        # asterisk-shaped marker
        options(name, "marker", (6, 2, 0))
        # no lines but only markers
        options(name, "symbols", True)
        options(name, "panel_size", 0.1)
        # TODO: tick thing are generally not in python
        # yticks is number of major yticks, which seems to be 3
        # options(name, "yticks", 2)
        options(name, "ytitle", " ")

    # Miscellaneous
    if ror:
        gatt = _cdf_var_atts(datfiles[0])
        _print_ror(gatt)

    # TODO: erg_export_filever add "erg_load_datalist" to tplot variable,
    # but this value seems not to be used
    # erg_export_filever(datfiles)


if __name__ == "__main__":
    pwe_wfc_info(
        trange=["2017-04-01/00:00:00", "2017-04-01/23:59:59"],
        level="l2",
        get_support_data=False,
        no_download=False,
        uname=None,
        passwd=None,
        ror=True,
    )
