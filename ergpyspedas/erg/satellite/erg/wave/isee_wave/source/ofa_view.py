import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from PySide6 import QtCore, QtGui, QtWidgets

from plot_ofa import plot_ofa_init


class OFAView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ISEE_Wave (OFA)")
        self._layout = QtWidgets.QVBoxLayout(self)
        self._input_layout = QtWidgets.QHBoxLayout()
        self._start_label = QtWidgets.QLabel("Start:")
        self._start_line_edit = QtWidgets.QLineEdit("2017-04-01/00:00:00")
        # self._start_line_edit.setFixedWidth(60)
        self._end_label = QtWidgets.QLabel("End:")
        self._end_line_edit = QtWidgets.QLineEdit("2017-04-01/23:59:59")
        # self._end_line_edit.setFixedWidth(60)
        self._display_button = QtWidgets.QPushButton("Display Data")
        self._input_layout.addWidget(self._start_label)
        self._input_layout.addWidget(self._start_line_edit)
        self._input_layout.addWidget(self._end_label)
        self._input_layout.addWidget(self._end_line_edit)
        self._input_layout.addWidget(self._display_button)
        self._input_layout.addStretch()
        self._one_day_before_button = QtWidgets.QPushButton("1 day <<")
        self._one_hour_before_button = QtWidgets.QPushButton("1 h <")
        self._input_layout.addWidget(self._one_day_before_button)
        self._input_layout.addWidget(self._one_hour_before_button)
        self._input_layout.addStretch()
        self._one_hour_after_button = QtWidgets.QPushButton("> 1 h")
        self._one_day_after_button = QtWidgets.QPushButton(">> 1 day")
        self._input_layout.addWidget(self._one_hour_after_button)
        self._input_layout.addWidget(self._one_day_after_button)
        self._input_layout.addStretch()
        self._tlimit_button = QtWidgets.QPushButton("tlimit")
        self._input_layout.addWidget(self._tlimit_button)
        self._input_layout.addStretch()
        self._input_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self._layout.addLayout(self._input_layout)
        fig = plot_ofa_init()
        self._canvas = FigureCanvas(fig)
        self._layout.addWidget(self._canvas)
        self._time_label = QtWidgets.QLabel("")
        self._layout.addWidget(self._time_label)
        self._layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        plt.clf()
        plt.close()
