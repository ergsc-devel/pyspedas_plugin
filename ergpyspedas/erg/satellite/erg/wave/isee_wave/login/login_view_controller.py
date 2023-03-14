from PySide6 import QtWidgets

from ..ofa.ofa_view_controller import OFAViewController
from ..options.ofa_view_option import OFAViewOption
from ..options.wfc_view_option import WFCViewOption
from ..wfc.wfc_view_controller import WFCViewController
from .login_presenter import LoginPresenter, LoginPresenterViewInterface
from .login_view import LoginView


class LoginViewController(LoginPresenterViewInterface):
    def __init__(self) -> None:
        super().__init__()
        self._view = LoginView()
        self._view._login_button.clicked.connect(self.login_button_clicked)  # type: ignore
        self._view._guest_button.clicked.connect(self.guest_button_clicked)  # type: ignore
        self._view._troubleshooting_button.clicked.connect(  # type: ignore
            self.troubleshooting_button_clicked
        )

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
            self._view, "Error", "X and Y sizes must be larger than 300 pixels."
        )

    def invalid_font_size_options(self) -> None:
        QtWidgets.QMessageBox.critical(
            self._view, "Error", "Font size must be larger than 0."
        )

    def invalid_uname_passwd(self) -> None:
        QtWidgets.QMessageBox.critical(self._view, "Error", "Authentication failed.")

    def troubleshooting_finished(self) -> None:
        QtWidgets.QMessageBox.information(
            self._view, "Information", "Successfully finished."
        )

    def transition_to_ofa_wfc(
        self, ofa_options: OFAViewOption, wfc_options: WFCViewOption
    ) -> None:
        self.ofa_vc = OFAViewController(ofa_options)
        self.wfc_vc = WFCViewController(wfc_options)
        self.ofa_vc.inject(self.wfc_vc)
        self.wfc_vc.inject(self.ofa_vc)
        self.ofa_vc.show()
        self.wfc_vc.show()
        self._view.close()

    def login_button_clicked(self) -> None:
        self._presenter.login()

    def guest_button_clicked(self) -> None:
        self._presenter.guest()

    def troubleshooting_button_clicked(self) -> None:
        self._presenter.troubleshooting()

    def update_views(self, option1, option2) -> None:
        self._view.update_views(option1, option2)

    def show(self) -> None:
        self._presenter.view_did_load()
        self._view.show()
