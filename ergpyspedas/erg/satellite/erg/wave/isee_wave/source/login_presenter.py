import os
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from pyspedas.erg.satellite.erg.config import CONFIG
from pytplot.store_data import store_data

from utils import str_to_float_or_none, str_to_int_or_none


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
    def close(self) -> None:
        pass


class LoginPresenterModelInterface(ABC):
    @abstractmethod
    def authenticate(self, idpw_uname: str, idpw_passwd: str) -> List[str]:
        pass


class LoginPresenter:
    def __init__(
        self, view: LoginPresenterViewInterface, model: LoginPresenterModelInterface
    ) -> None:
        # TODO: Check circular reference does not lead to memory leak or any other symptoms
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
        # TODO: check font_size = 0 is maybe not ok
        if font_size is None or font_size <= 0:
            return None
        else:
            return font_size

    def _validate_uname_passwd(self):
        # TODO: do I have to list up paths?
        paths = self._model.authenticate(self._view.uname, self._view.passwd)
        all_paths_exist = len(paths) > 0 and all(
            [os.path.exists(path) for path in paths]
        )
        if all_paths_exist:
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

        ofa_xsize, ofa_ysize, wfc_xsize, wfc_ysize = window_size_options
        uname, passwd = uname_passwd

        store_data("ofa_xsize", data={"x": [0], "y": [ofa_xsize]})
        store_data("ofa_ysize", data={"x": [0], "y": [ofa_ysize]})
        store_data("wfc_xsize", data={"x": [0], "y": [wfc_xsize]})
        store_data("wfc_ysize", data={"x": [0], "y": [wfc_ysize]})
        store_data("fontsize", data={"x": [0], "y": [font_size]})
        store_data("uname", data={"x": [0], "y": [uname]})
        store_data("passwd", data={"x": [0], "y": [passwd]})

        # TODO: if new main window is modeless, I assume this order won't be a problem
        # pw_main()
        self._view.close()

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

        store_data("ofa_xsize", data={"x": [0], "y": [ofa_xsize]})
        store_data("ofa_ysize", data={"x": [0], "y": [ofa_ysize]})
        store_data("wfc_xsize", data={"x": [0], "y": [wfc_xsize]})
        store_data("wfc_ysize", data={"x": [0], "y": [wfc_ysize]})
        store_data("fontsize", data={"x": [0], "y": [font_size]})

        # TODO: if new main window is modeless, I assume this order won't be a problem
        # pw_main()
        self._view.close()

    def troubleshooting(self):
        localdir = CONFIG["local_data_dir"]
        path = os.path.join(localdir, "default_config.json")
        if os.path.exists(path):
            os.remove(path)
        path = os.path.join(localdir, "user_config.json")
        if os.path.exists(path):
            os.remove(path)
        self._view.troubleshooting_finished()
