
from PySide6 import QtCore, QtGui, QtWidgets


class LoginView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISEE_Wave")
        self._layout = QtWidgets.QVBoxLayout(self)

        pixmap = QtGui.QPixmap("assets/images/arase_logo.png")
        pixmap = pixmap.scaled(200, 200)
        self._image_label = QtWidgets.QLabel()
        self._image_label.setPixmap(pixmap)
        self._image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._image_label)

        self._idpw_loginguest_layout = QtWidgets.QVBoxLayout()

        self._idpw_layout = QtWidgets.QHBoxLayout()
        self._id_label = QtWidgets.QLabel("ID:")
        self._id_line_edit = QtWidgets.QLineEdit()
        self._pw_label = QtWidgets.QLabel("PW:")
        self._pw_line_edit = QtWidgets.QLineEdit()
        self._idpw_layout.addWidget(self._id_label)
        self._idpw_layout.addWidget(self._id_line_edit)
        self._idpw_layout.addWidget(self._pw_label)
        self._idpw_layout.addWidget(self._pw_line_edit)
        self._idpw_loginguest_layout.addLayout(self._idpw_layout)

        self._loginguest_layout = QtWidgets.QHBoxLayout()
        self._login_button = QtWidgets.QPushButton("Login")
        self._or_label = QtWidgets.QLabel("or")
        self._guest_button = QtWidgets.QPushButton("Guest")
        self._loginguest_layout.addWidget(self._login_button)
        self._loginguest_layout.addWidget(self._or_label)
        self._loginguest_layout.addWidget(self._guest_button)
        self._loginguest_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        self._idpw_loginguest_layout.addLayout(self._loginguest_layout)

        self._layout.addLayout(self._idpw_loginguest_layout)
        self._layout.addStretch()

        self._advanced_options_layout = QtWidgets.QVBoxLayout()
        self._advanced_options_label = QtWidgets.QLabel("[Advanced options]")
        self._advanced_options_layout.addWidget(self._advanced_options_label)

        self._ofa_layout = QtWidgets.QHBoxLayout()
        self._ofa_label = QtWidgets.QLabel("[OFA]")
        self._ofa_xsize_label = QtWidgets.QLabel("X size:")
        self._ofa_xsize_line_edit = QtWidgets.QLineEdit("1280")
        # TODO: only setFixedWidth can really control width
        # but it is not aligned against above or below lines
        # maybe grid layout is better
        self._ofa_xsize_line_edit.setFixedWidth(40)
        self._ofa_xsize_px_label = QtWidgets.QLabel("px")
        self._ofa_ysize_label = QtWidgets.QLabel("Y size:")
        self._ofa_ysize_line_edit = QtWidgets.QLineEdit("600")
        self._ofa_ysize_line_edit.setFixedWidth(40)
        self._ofa_ysize_px_label = QtWidgets.QLabel("px")
        self._ofa_layout.addWidget(self._ofa_label)
        self._ofa_layout.addWidget(self._ofa_xsize_label)
        self._ofa_layout.addWidget(self._ofa_xsize_line_edit)
        self._ofa_layout.addWidget(self._ofa_xsize_px_label)
        self._ofa_layout.addWidget(self._ofa_ysize_label)
        self._ofa_layout.addWidget(self._ofa_ysize_line_edit)
        self._ofa_layout.addWidget(self._ofa_ysize_px_label)
        self._ofa_layout.addStretch()
        self._ofa_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft)
        self._advanced_options_layout.addLayout(self._ofa_layout)

        self._wfc_layout = QtWidgets.QHBoxLayout()
        self._wfc_label = QtWidgets.QLabel("[WFC]")
        self._wfc_xsize_label = QtWidgets.QLabel("X size:")
        self._wfc_xsize_line_edit = QtWidgets.QLineEdit("650")
        self._wfc_xsize_line_edit.setFixedWidth(40)
        self._wfc_xsize_px_label = QtWidgets.QLabel("px")
        self._wfc_ysize_label = QtWidgets.QLabel("Y size:")
        self._wfc_ysize_line_edit = QtWidgets.QLineEdit("900")
        self._wfc_ysize_line_edit.setFixedWidth(40)
        self._wfc_ysize_px_label = QtWidgets.QLabel("px")
        self._wfc_layout.addWidget(self._wfc_label)
        self._wfc_layout.addWidget(self._wfc_xsize_label)
        self._wfc_layout.addWidget(self._wfc_xsize_line_edit)
        self._wfc_layout.addWidget(self._wfc_xsize_px_label)
        self._wfc_layout.addWidget(self._wfc_ysize_label)
        self._wfc_layout.addWidget(self._wfc_ysize_line_edit)
        self._wfc_layout.addWidget(self._wfc_ysize_px_label)
        self._wfc_layout.addStretch()
        self._wfc_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft)
        self._advanced_options_layout.addLayout(self._wfc_layout)

        self._font_size_layout = QtWidgets.QHBoxLayout()
        self._font_size_label = QtWidgets.QLabel("[Font size]")
        self._font_size_line_edit = QtWidgets.QLineEdit("1.0")
        self._font_size_line_edit.setFixedWidth(40)
        self._font_size_layout.addWidget(self._font_size_label)
        self._font_size_layout.addWidget(self._font_size_line_edit)
        self._font_size_layout.addStretch()
        self._font_size_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft)
        self._advanced_options_layout.addLayout(self._font_size_layout)

        self._troubleshooting_layout = QtWidgets.QHBoxLayout()
        self._troubleshooting_label = QtWidgets.QLabel("[Troubleshooting]")
        self._troubleshooting_button = QtWidgets.QPushButton(
            "Temporary file reset")
        self._troubleshooting_layout.addWidget(self._troubleshooting_label)
        self._troubleshooting_layout.addWidget(self._troubleshooting_button)
        self._troubleshooting_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft)
        self._advanced_options_layout.addLayout(self._troubleshooting_layout)

        self._layout.addLayout(self._advanced_options_layout)
        self._layout.addStretch()
        # TODO: What version should it be?
        self._version_label = QtWidgets.QLabel("Version: 1.1.0")
        self._layout.addWidget(self._version_label)

        # TODO: is it ok to be here?
        self.resize(329, 510)
