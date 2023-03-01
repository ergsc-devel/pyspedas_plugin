from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

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
        "mask_label": "E-Spec",
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
        "mask_label": "B-Spec",
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

orbital_information_option_dict = {
    "mlt": True,
    "mlat": True,
    "altitude": True,
    "lshell": True,
}

support_line_option_list = [
    {
        "species": "fc",
        "M": "1/1837",
        "Q": "1",
        "LSTY": "0",
        "LCOL": "5",
        "enable": "OFF",
    },
    {
        "species": "0.5fc",
        "M": "2/1837",
        "Q": "1",
        "LSTY": "0",
        "LCOL": "1",
        "enable": "OFF",
    },
    {
        "species": "0.1fc",
        "M": "10/1837",
        "Q": "1",
        "LSTY": "0",
        "LCOL": "3",
        "enable": "OFF",
    },
    {
        "species": "fcH",
        "M": "1",
        "Q": "1",
        "LSTY": "0",
        "LCOL": "255",
        "enable": "OFF",
    },
    {
        "species": "fcHe",
        "M": "4",
        "Q": "1",
        "LSTY": "0",
        "LCOL": "255",
        "enable": "OFF",
    },
    {
        "species": "fcO",
        "M": "16",
        "Q": "1",
        "LSTY": "0",
        "LCOL": "255",
        "enable": "OFF",
    },
]


@dataclass
class DataOption:
    ytitle: str  # y label first column
    ysubtitle: str  # ylabel second column
    ymin: float
    ymax: float
    ylog: bool
    ztitle: str  # label of color bar
    zmin: float
    zmax: float
    zlog: bool
    mask: bool
    plot: bool
    mask_label: str


@dataclass
class DataInfo:
    min: float
    max: float
    mask: float


class DataName(Enum):
    espec = "espec"
    bspec = "bspec"
    wna = "wna"
    polarization = "polarization"
    planarity = "planarity"
    poyntingvec = "poyntingvec"


class OrbitalInfoName(Enum):
    mlt = "mlt"
    mlat = "mlat"
    alt = "altitude"
    l = "lshell"


class SupportLineOptionName(Enum):
    species = "species"
    m = "M"
    q = "Q"
    lsty = "LSTY"
    lcol = "LCOL"
    enable = "enable"


def create_data_options(data_option_dict_dict) -> Dict[DataName, DataOption]:
    data_options = {}
    for name in DataName:
        dic = data_option_dict_dict[name.value]
        data_options[name] = DataOption(**dic)
    return data_options


def create_orbital_informations(
    orbital_information_option_dict,
) -> Dict[OrbitalInfoName, bool]:
    return {id_: orbital_information_option_dict[id_.value] for id_ in OrbitalInfoName}


def create_support_line_options(
    support_line_option_list,
) -> List[Dict[SupportLineOptionName, str]]:
    list_ = []
    for dict_ in support_line_option_list:
        list_.append({name: dict_[name.value] for name in SupportLineOptionName})
    return list_
