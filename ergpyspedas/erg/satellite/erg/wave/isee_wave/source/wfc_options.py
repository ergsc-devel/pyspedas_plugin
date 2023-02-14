from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

data_option_dict_dict = {
    "espec": {
        "ytitle": "E-Spec",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": 1,
        "ztitle": r"$\rm{[mV^2/m^2/Hz]}$",
        "zmin": 1e-9,
        "zmax": 1e0,
        "zlog": 1,
        "mask": 1,
        "plot": 1,
        "mask_label": "E-Spec (Exponential)",
    },
    "bspec": {
        "ytitle": "B-Spec",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": 1,
        "ztitle": r"$\rm{[pT^2/Hz]}$",
        "zmin": 1e-4,
        "zmax": 1e2,
        "zlog": 1,
        "mask": 1,
        "plot": 1,
        "mask_label": "B-Spec (Exponential)",
    },
    "wna": {
        "ytitle": "Wave normal angle",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": 1,
        "ztitle": "[degree]",
        "zmin": 0.0,
        "zmax": 90.0,
        "zlog": 0,
        "mask": 1,
        "plot": 1,
        "mask_label": "Wave normal angle",
    },
    "polarization": {
        "ytitle": "Polarization",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": 1,
        "ztitle": "",
        "zmin": -1.0,
        "zmax": 1.0,
        "zlog": 0,
        "mask": 1,
        "plot": 1,
        "mask_label": "Polarization",
    },
    "planarity": {
        "ytitle": "Planarity",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": 1,
        "ztitle": "",
        "zmin": 0.0,
        "zmax": 1.0,
        "zlog": 0,
        "mask": 1,
        "plot": 1,
        "mask_label": "Planarity",
    },
    "poyntingvec": {
        "ytitle": "Poynting vector angle",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": 1,
        "ztitle": "[degree]",
        "zmin": 0.0,
        "zmax": 180.0,
        "zlog": 0,
        "mask": 1,
        "plot": 1,
        "mask_label": "Poynting vector",
    },
}

orbital_information_option_dict = {"mlt": 1, "mlat": 1, "altitude": 1, "lshell": 1}


params = {
    "ofa_starttime": ["2017-04-01/00:00:00"],
    "ofa_endtime": ["2017-04-01/23:59:59"],
    "ofa_drawwindow": None,
    "ofa_xs": 1280,
    "ofa_ys": 600,
    "ofa_tplotlist": [
        "ofae",
        "ofab",
        "erg_pwe_wfc_l2_info_stat_chorus",
        "erg_pwe_wfc_l2_info_stat_swpia",
    ],
    "wfc_starttime": "2017-04-01/13:57:45",
    "wfc_endtime": "2017-04-01/13:57:53",
    "wfc_xs": 650,
    "wfc_ys": 900,
    "fce": 0,
    "fcH": 0,
    "fce05": 0,
    "fcH05": 0,
    "fcHe": 0,
    "fcO": 0,
    "tb_sel_top": 0,
    "tb_sel_bottom": 0,
    "draw_support_line_cb": 1,
    "filter": "BPF",
    "drawline": 0,
    "rgb_table": 33,
    "mask_flg": 0,
    "UVW": "GEO",
    "xdeg": 0,
    "ydeg": 0,
    "zdeg": 0,
    "mask_apply_01": 1,
    "mask_apply_02": 1,
    "mask_apply_03": 1,
    "mask_apply_04": 1,
    "mask_apply_05": 1,
    "mask_apply_06": 1,
    "ylog_01": 0,
    "ylog_02": 0,
    "ylog_03": 0,
    "ylog_04": 0,
    "ylog_05": 0,
    "ylog_06": 0,
    "zlog_01": 0,
    "zlog_02": 0,
    "zlog_03": 0,
    "zlog_04": 0,
    "zlog_05": 0,
    "zlog_06": 0,
}


@dataclass
class OrbitalInformationOption:
    mlt: int
    mlat: int
    altitude: int
    lshell: int


@dataclass
class DataOption:
    ytitle: str  # y label first column
    ysubtitle: str  # ylabel second column
    ymin: float
    ymax: float
    ylog: int  # 0: linear, 1: log
    ztitle: str  # label of color bar
    zmin: float
    zmax: float
    zlog: int  # 0: linear, 1: log
    mask: int  # 0: false, 1: true
    plot: int  # 0: false, 1: true
    mask_label: str


@dataclass
class DataInfo:
    min: Optional[float] = None
    max: Optional[float] = None
    mask: Optional[float] = None


class DataName(Enum):
    espec = "espec"
    bspec = "bspec"
    wna = "wna"
    polarization = "polarization"
    planarity = "planarity"
    poyntingvec = "poyntingvec"


def create_data_options() -> Dict[DataName, DataOption]:
    data_options = {}
    for name in DataName:
        dic = data_option_dict_dict[name.value]
        data_options[name] = DataOption(**dic)
    return data_options


def create_data_infos() -> Dict[DataName, DataInfo]:
    data_infos = {}
    for name in DataName:
        data_infos[name] = DataInfo()
    return data_infos
