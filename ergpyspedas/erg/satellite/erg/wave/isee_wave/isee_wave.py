from PySide6 import QtWidgets

from .login.authentication_model import AuthenticationModel
from .login.login_presenter import LoginPresenter
from .login.login_view_controller import LoginViewController


def isee_wave():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    model = AuthenticationModel()
    view = LoginViewController()
    presenter = LoginPresenter(view, model)
    view.inject(presenter)
    view.show()
    app.exec()


if __name__ == "__main__":
    isee_wave()
