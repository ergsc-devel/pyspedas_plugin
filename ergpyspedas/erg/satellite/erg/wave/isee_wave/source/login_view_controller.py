from PySide6 import QtWidgets

from login_presenter import LoginPresenter, LoginPresenterViewInterface
from login_view import LoginView


class LoginViewController(LoginPresenterViewInterface):
    def __init__(self) -> None:
        super().__init__()
        self._view = LoginView()
        self._view._login_button.clicked.connect(self.login_button_clicked)
        self._view._guest_button.clicked.connect(self.guest_button_clicked)
        self._view._troubleshooting_button.clicked.connect(
            self.troubleshooting_button_clicked)

    def inject(self, presenter: LoginPresenter) -> None:
        self._presenter = presenter

    @property
    def ofa_xsize(self) -> str:
        return self._view._ofa_xsize_line_edit.text()

    @property
    def ofa_ysize(self) -> str:
        return self._view._ofa_ysize_line_edit.text()

    @property
    def wfc_xsize(self) -> str:
        return self._view._wfc_xsize_line_edit.text()

    @property
    def wfc_ysize(self) -> str:
        return self._view._wfc_ysize_line_edit.text()

    @property
    def font_size(self) -> str:
        return self._view._font_size_line_edit.text()

    @property
    def uname(self) -> str:
        return self._view._id_line_edit.text()

    @property
    def passwd(self) -> str:
        return self._view._pw_line_edit.text()

    def invalid_window_size_options(self) -> None:
        QtWidgets.QMessageBox.critical(
            self._view, "Error", "X and Y sizes must be larger than 300 pixels.")

    def invalid_font_size_options(self) -> None:
        QtWidgets.QMessageBox.critical(
            self._view, "Error", "Font size must be larger than 0.")

    def invalid_uname_passwd(self) -> None:
        QtWidgets.QMessageBox.critical(
            self._view, "Error", "Authentication failed.")
        # TODO: maybe logging?
        print("Authentication failed.")

    def troubleshooting_finished(self) -> None:
        QtWidgets.QMessageBox.information(
            self._view, "Information", "Successfully finished.")

    def close(self) -> None:
        self._view.close()

    def login_button_clicked(self) -> None:
        self._presenter.login()

    def guest_button_clicked(self) -> None:
        self._presenter.guest()

    def troubleshooting_button_clicked(self) -> None:
        self._presenter.troubleshooting()

    def show(self) -> None:
        self._view.show()
