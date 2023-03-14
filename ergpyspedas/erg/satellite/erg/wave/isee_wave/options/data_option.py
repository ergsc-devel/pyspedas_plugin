from __future__ import annotations

from collections import UserDict
from enum import Enum
from typing import Any, Dict, Optional

from ..utils.utils import epsilon

# Default options
_data_option_dict = {
    "espec": {
        "ytitle": "E-Spec",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": True,
        "ztitle": "$\\rm{[mV^2/m^2/Hz]}$",
        "zmin": 1e-9,
        "zmax": 1e0,
        "zlog": True,
        "mask": False,
        "plot": True,
        "mask_label": "E-Spec",
    },
    "bspec": {
        "ytitle": "B-Spec",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": True,
        "ztitle": "$\\rm{[pT^2/Hz]}$",
        "zmin": 1e-4,
        "zmax": 1e2,
        "zlog": True,
        "mask": False,
        "plot": True,
        "mask_label": "B-Spec",
    },
    "wna": {
        "ytitle": "Wave normal angle",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": True,
        "ztitle": "[degree]",
        "zmin": 0.0,
        "zmax": 90.0,
        "zlog": False,
        "mask": False,
        "plot": True,
        "mask_label": "Wave normal angle",
    },
    "polarization": {
        "ytitle": "Polarization",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": True,
        "ztitle": "",
        "zmin": -1.0,
        "zmax": 1.0,
        "zlog": False,
        "mask": False,
        "plot": True,
        "mask_label": "Polarization",
    },
    "planarity": {
        "ytitle": "Planarity",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": True,
        "ztitle": "",
        "zmin": 0.0,
        "zmax": 1.0,
        "zlog": False,
        "mask": False,
        "plot": True,
        "mask_label": "Planarity",
    },
    "poyntingvec": {
        "ytitle": "Poynting vector angle",
        "ysubtitle": "Frequency[Hz]",
        "ymin": 32,
        "ymax": 20000,
        "ylog": True,
        "ztitle": "[degree]",
        "zmin": 0.0,
        "zmax": 180.0,
        "zlog": False,
        "mask": False,
        "plot": True,
        "mask_label": "Poynting vector",
    },
}


class DataName(Enum):
    """WFC analyzed data. DataName.<property>.value is their tplot name."""

    espec = "espec"
    bspec = "bspec"
    wna = "wna"
    polarization = "polarization"
    planarity = "planarity"
    poyntingvec = "poyntingvec"


class DataOption:
    def __init__(
        self,
        ytitle: str,
        ysubtitle: str,
        ymin: float,
        ymax: float,
        ylog: bool,
        ztitle: str,
        zmin: float,
        zmax: float,
        zlog: bool,
        mask: bool,
        plot: bool,
        mask_label: str,
    ) -> None:
        """Options for WFC analyzed data.

        You can get / set valid value to each option using this class.

        (ex1.) if zlog is True, even if you try to set by the setter
        from zmin > 0 to zmin <= 0, you get from the getter
        old zmin > 0 that does not reflect the setting you just did.

        (ex2.) if zmin <= 0, if you changed zlog from False to True,
        you get from the getter small zmin > 0. Then if you changed zlog
        to False again, you get from the getter previous zmin <= 0.
        """
        self._keys = [
            "ytitle",
            "ysubtitle",
            "ymin",
            "ymax",
            "ylog",
            "ztitle",
            "zmin",
            "zmax",
            "zlog",
            "mask",
            "plot",
            "mask_label",
        ]
        self.ytitle = ytitle
        self.ysubtitle = ysubtitle
        self.ztitle = ztitle
        self.mask = mask
        self.plot = plot
        self.set_mask_label(mask_label)
        # Limit values must be initialized after log values
        self.ylog = ylog
        self.zlog = zlog
        self.set_ymin(float(ymin), error_if_invalid=True)
        self.set_ymax(float(ymax), error_if_invalid=True)
        self.set_zmin(float(zmin), error_if_invalid=True)
        self.set_zmax(float(zmax), error_if_invalid=True)

    def _is_valid_as_ylim(self, ylim: float) -> bool:
        return not (self.ylog and ylim <= 0)

    @property
    def ymin(self) -> float:
        if self._is_valid_as_ylim(self._ymin_real):
            return self._ymin_real
        else:
            return epsilon

    def set_ymin(self, ymin: float, error_if_invalid: bool = False) -> None:
        if self._is_valid_as_ylim(ymin):
            self._ymin_real = ymin
        else:
            if error_if_invalid:
                raise ValueError("if ylog == True, ymin should be > 0")

    @property
    def ymax(self) -> float:
        if self._is_valid_as_ylim(self._ymax_real):
            return self._ymax_real
        else:
            return epsilon

    def set_ymax(self, ymax: float, error_if_invalid: bool = False) -> None:
        if self._is_valid_as_ylim(ymax):
            self._ymax_real = ymax
        else:
            if error_if_invalid:
                raise ValueError("if ylog == True, ymax should be > 0")

    def _is_valid_as_zlim(self, zlim: float) -> bool:
        return not (self.zlog and zlim <= 0)

    @property
    def zmin(self) -> float:
        if self._is_valid_as_zlim(self._zmin_real):
            return self._zmin_real
        else:
            return epsilon

    def set_zmin(self, zmin: float, error_if_invalid: bool = False) -> None:
        if self._is_valid_as_zlim(zmin):
            self._zmin_real = zmin
        else:
            if error_if_invalid:
                raise ValueError("if zlog == True, zmin should be > 0")

    @property
    def zmax(self) -> float:
        if self._is_valid_as_zlim(self._zmax_real):
            return self._zmax_real
        else:
            return epsilon

    def set_zmax(self, zmax: float, error_if_invalid: bool = False) -> None:
        if self._is_valid_as_zlim(zmax):
            self._zmax_real = zmax
        else:
            if error_if_invalid:
                raise ValueError("if zlog == True, zmax should be > 0")

    @property
    def mask_label(self) -> str:
        ret = self._mask_label
        if self.zlog:
            ret += " (Exponential)"
        ret += ":"
        return ret

    def set_mask_label(self, mask_label: str) -> None:
        self._mask_label = mask_label

    def to_dict(self) -> Dict[str, Any]:
        return {key: getattr(self, key) for key in self._keys}


# Used to get type hint during development
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Need to be place after definition of DataOption
    _DataOptionsBase = UserDict[DataName, DataOption]
else:
    _DataOptionsBase = UserDict


class DataOptions(_DataOptionsBase):
    """Group DataOption for each different WFC analyzed data."""

    @classmethod
    def from_dict(
        cls, dict_: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> DataOptions:
        if dict_ is None:
            dict_ = _data_option_dict
        dict_name_vs_opt = {name: DataOption(**dict_[name.value]) for name in DataName}
        return cls(dict_name_vs_opt)

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {name.value: self[name].to_dict() for name in DataName}


if __name__ == "__main__":
    data_options = DataOptions.from_dict(_data_option_dict)
    assert all([d1 == d2 for d1, d2 in zip(_data_option_dict, data_options.to_dict())])
