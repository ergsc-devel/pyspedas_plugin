import os

from pyspedas.erg.satellite.erg.config import CONFIG
from pyspedas.utilities.download import download

from .login_presenter import LoginPresenterModelInterface


class AuthenticationModel(LoginPresenterModelInterface):
    def __init__(self) -> None:
        super().__init__()

    def authenticate(self, uname: str, passwd: str) -> bool:
        """Return True if user name and password is valid else False"""
        local_dir = CONFIG["local_data_dir"]
        remote_dir = "http://ergsc.isee.nagoya-u.ac.jp/erg_socware/bleeding_edge/"
        local_file = "pw_connection"

        # Removing local file in Python is equivalent to forcing download in IDL
        local_path = local_dir + local_file
        if os.path.exists(local_path):
            os.remove(local_path)

        paths = download(
            remote_path=remote_dir,
            remote_file="note_ERG-SC_procedures_en.pdf",
            local_path=local_dir,
            local_file=local_file,
            no_download=False,
            username=uname,
            password=passwd,
            basic_auth=False,
            last_version=True,
        )

        # Maybe path existence check is verbose but follow convention in
        # for example idpw_login in spedas\projects\erg\satellite\erg\wave\isee_wave\idpw_login.pro
        all_paths_exists = (
            paths is not None
            and len(paths) > 0
            and all([os.path.exists(path) for path in paths])
        )
        return all_paths_exists
