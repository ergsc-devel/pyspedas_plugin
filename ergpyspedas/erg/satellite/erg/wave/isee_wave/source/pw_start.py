import sys

from PySide6 import QtWidgets

from authentication_model import AuthenticationModel
from login_presenter import LoginPresenter
from login_view_controller import LoginViewController


def pw_start():
    app = QtWidgets.QApplication([])

    model = AuthenticationModel()
    view = LoginViewController()
    presenter = LoginPresenter(view, model)
    view.inject(presenter)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    pw_start()
