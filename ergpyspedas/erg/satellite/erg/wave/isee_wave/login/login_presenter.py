import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Optional, Tuple

from pyspedas.erg.satellite.erg.config import CONFIG
from pytplot.store_data import store_data

from ..options.ofa_view_option import OFAViewOption
from ..options.wfc_view_option import WFCViewOption
from ..utils.utils import str_to_float_or_none, str_to_int_or_none


class LoginPresenterViewInterface(ABC):
    @property
    @abstractmethod
    def ofa_xsize(self) -> str:
        pass

    @property
    @abstractmethod
    def ofa_ysize(self) -> str:
        pass

    @property
    @abstractmethod
    def wfc_xsize(self) -> str:
        pass

    @property
    @abstractmethod
    def wfc_ysize(self) -> str:
        pass

    @property
    @abstractmethod
    def font_size(self) -> str:
        pass

    @property
    @abstractmethod
    def uname(self) -> str:
        pass

    @property
    @abstractmethod
    def passwd(self) -> str:
        pass

    @abstractmethod
    def invalid_window_size_options(self) -> None:
        pass

    @abstractmethod
    def invalid_font_size_options(self) -> None:
        pass

    @abstractmethod
    def invalid_uname_passwd(self) -> None:
        pass

    @abstractmethod
    def troubleshooting_finished(self) -> None:
        pass

    @abstractmethod
    def transition_to_ofa_wfc(
        self, ofa_options: OFAViewOption, wfc_options: WFCViewOption
    ) -> None:
        pass

    @abstractmethod
    def update_views(self, option1, option2) -> None:
        pass


class LoginPresenterModelInterface(ABC):
    @abstractmethod
    def authenticate(self, idpw_uname: str, idpw_passwd: str) -> bool:
        pass


class LoginPresenter:
    def __init__(
        self, view: LoginPresenterViewInterface, model: LoginPresenterModelInterface
    ) -> None:
        self._view = view
        self._model = model

    def _validate_window_size_options(self) -> Optional[Tuple[int, int, int, int]]:
        ofa_xsize = str_to_int_or_none(self._view.ofa_xsize)
        ofa_ysize = str_to_int_or_none(self._view.ofa_ysize)
        wfc_xsize = str_to_int_or_none(self._view.wfc_xsize)
        wfc_ysize = str_to_int_or_none(self._view.wfc_ysize)
        if (
            (ofa_xsize is None or ofa_xsize < 300)
            or (ofa_ysize is None or ofa_ysize < 300)
            or (wfc_xsize is None or wfc_xsize < 300)
            or (wfc_ysize is None or wfc_ysize < 300)
        ):
            return None
        else:
            return (ofa_xsize, ofa_ysize, wfc_xsize, wfc_ysize)

    def _validate_font_size_options(self) -> Optional[float]:
        font_size = str_to_float_or_none(self._view.font_size)
        if font_size is None or font_size <= 0:
            return None
        else:
            return font_size

    def _validate_uname_passwd(self) -> Optional[Tuple[str, str]]:
        is_authenticated = self._model.authenticate(self._view.uname, self._view.passwd)
        if is_authenticated:
            return (self._view.uname, self._view.passwd)
        else:
            return None

    def login(self):
        window_size_options = self._validate_window_size_options()
        if window_size_options is None:
            self._view.invalid_window_size_options()
            return

        font_size = self._validate_font_size_options()
        if font_size is None:
            self._view.invalid_font_size_options()
            return

        uname_passwd = self._validate_uname_passwd()
        if uname_passwd is None:
            self._view.invalid_uname_passwd()
            return

        uname, passwd = uname_passwd
        store_data("uname", data={"x": [0], "y": [uname]})
        store_data("passwd", data={"x": [0], "y": [passwd]})

        ofa_xsize, ofa_ysize, wfc_xsize, wfc_ysize = window_size_options
        ofa_options = OFAViewOption(ofa_xsize, ofa_ysize, font_size)
        wfc_options = WFCViewOption(wfc_xsize, wfc_ysize, font_size)

        self._save_config(ofa_options, wfc_options)
        self._view.transition_to_ofa_wfc(ofa_options, wfc_options)

    def guest(self):
        window_size_options = self._validate_window_size_options()
        if window_size_options is None:
            self._view.invalid_window_size_options()
            return

        font_size = self._validate_font_size_options()
        if font_size is None:
            self._view.invalid_font_size_options()
            return

        ofa_xsize, ofa_ysize, wfc_xsize, wfc_ysize = window_size_options
        ofa_options = OFAViewOption(ofa_xsize, ofa_ysize, font_size)
        wfc_options = WFCViewOption(wfc_xsize, wfc_ysize, font_size)

        self._save_config(ofa_options, wfc_options)
        self._view.transition_to_ofa_wfc(ofa_options, wfc_options)

    def troubleshooting(self):
        localdir = CONFIG["local_data_dir"]
        path = os.path.join(localdir, "default_config.json")
        if os.path.exists(path):
            os.remove(path)
        path = os.path.join(localdir, "user_config.json")
        if os.path.exists(path):
            os.remove(path)
        self._view.troubleshooting_finished()
        self.view_did_load()

    def view_did_load(self) -> None:
        ofa_options, wfc_options = self._load_config()
        self._view.update_views(ofa_options, wfc_options)

    def _load_config(self):
        ofa_options = self._load_ofa_config()
        wfc_options = self._load_wfc_config()
        return ofa_options, wfc_options

    def _load_ofa_config(self) -> OFAViewOption:
        localdir = CONFIG["local_data_dir"]

        path_user = os.path.join(localdir, "user_config.json")
        if os.path.exists(path_user):
            with open(path_user, "r") as f:
                json_data = json.load(f)
            view_option_dict = json_data.get("ofa_view")
            if view_option_dict is not None:
                options_user = OFAViewOption(**view_option_dict)
                return options_user

        path_default = os.path.join(localdir, "default_config.json")
        if os.path.exists(path_default):
            with open(path_default, "r") as f:
                json_data = json.load(f)
            view_option_dict = json_data.get("ofa_view")
            if view_option_dict is not None:
                options_default = OFAViewOption(**view_option_dict)
                return options_default

        options = OFAViewOption()
        for path in [path_user, path_default]:
            if os.path.exists(path):
                with open(path, "r") as f:
                    json_data = json.load(f)
            else:
                json_data = {}

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json_data["ofa_view"] = asdict(options)
                json.dump(json_data, f, indent=4)
        return options

    def _load_wfc_config(self) -> WFCViewOption:
        localdir = CONFIG["local_data_dir"]

        path_user = os.path.join(localdir, "user_config.json")
        if os.path.exists(path_user):
            with open(path_user, "r") as f:
                json_data = json.load(f)
            view_option_dict = json_data.get("wfc_view")
            if view_option_dict is not None:
                options_user = WFCViewOption(**view_option_dict)
                return options_user

        path_default = os.path.join(localdir, "default_config.json")
        if os.path.exists(path_default):
            with open(path_default, "r") as f:
                json_data = json.load(f)
            view_option_dict = json_data.get("wfc_view")
            if view_option_dict is not None:
                options_default = WFCViewOption(**view_option_dict)
                return options_default

        options = WFCViewOption()
        for path in [path_user, path_default]:
            if os.path.exists(path):
                with open(path, "r") as f:
                    json_data = json.load(f)
            else:
                json_data = {}

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json_data["wfc_view"] = asdict(options)
                json.dump(json_data, f, indent=4)
        return options

    def _save_config(
        self, ofa_options: OFAViewOption, wfc_options: WFCViewOption
    ) -> None:
        localdir = CONFIG["local_data_dir"]

        path = os.path.join(localdir, "user_config.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            with open(path, "r") as f:
                json_data = json.load(f)
        else:
            json_data = {}
        json_data["ofa_view"] = asdict(ofa_options)
        json_data["wfc_view"] = asdict(wfc_options)
        with open(path, "w") as f:
            json.dump(json_data, f, indent=4)
