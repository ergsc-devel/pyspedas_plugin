import os

from pyspedas.erg.satellite.erg.config import CONFIG
from pyspedas.utilities.download import download

from .login_presenter import LoginPresenterModelInterface


class AuthenticationModel(LoginPresenterModelInterface):
    def __init__(self) -> None:
        super().__init__()

    def authenticate(self, idpw_uname: str, idpw_passwd: str) -> bool:
        localdir = CONFIG["local_data_dir"]
        remotedir = "http://ergsc.isee.nagoya-u.ac.jp/erg_socware/bleeding_edge/"
        path = localdir + "pw_connection"
        # Removing local file is equivalent to force download
        if os.path.exists(path):
            os.remove(path)
        # TODO: check last_version is same in pyspedas (however not necassary for this function)
        paths = download(
            remote_path=remotedir,
            remote_file="note_ERG-SC_procedures_en.pdf",
            local_path=localdir,
            local_file="pw_connection",
            no_download=False,
            username=idpw_uname,
            password=idpw_passwd,
            basic_auth=False,
            last_version=True,
        )
        all_paths_exists = len(paths) > 0 and all(
            [os.path.exists(path) for path in paths]
        )
        return all_paths_exists
