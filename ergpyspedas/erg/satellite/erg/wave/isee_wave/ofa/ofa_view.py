import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6 import QtCore, QtGui, QtWidgets

from ..options.ofa_view_option import OFAViewOption
from ..plot.common import plot_init


class OFAView(QtWidgets.QWidget):
    def __init__(self, options: OFAViewOption = OFAViewOption()) -> None:
        super().__init__()
        self.setWindowTitle("ISEE_Wave (OFA)")
        self._layout = QtWidgets.QVBoxLayout(self)
        self._input_layout = QtWidgets.QHBoxLayout()
        self._start_label = QtWidgets.QLabel("Start:")
        self._start_line_edit = QtWidgets.QLineEdit("2017-04-01/00:00:00")
        self._start_line_edit.setFixedWidth(140)
        self._end_label = QtWidgets.QLabel("End:")
        self._end_line_edit = QtWidgets.QLineEdit("2017-04-01/23:59:59")
        self._end_line_edit.setFixedWidth(140)
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
        # HACK: Put single figure in nested layout with stretch
        # in order not the figure to stretch but spacings around the figure to stretch
        self._canvas_vlayout = QtWidgets.QVBoxLayout()
        self._layout.addLayout(self._canvas_vlayout)
        self._canvas_hlayout = QtWidgets.QHBoxLayout()
        self._canvas_vlayout.addLayout(self._canvas_hlayout)
        fig = plot_init(options.xsize, options.ysize)
        self._canvas = FigureCanvasQTAgg(fig)
        self._canvas_hlayout.addWidget(self._canvas)
        self._canvas_hlayout.addStretch()
        self._canvas_vlayout.addStretch()
        self._time_label = QtWidgets.QLabel("")
        self._layout.addWidget(self._time_label)
        self._layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        plt.clf()
        plt.close()

    def widgets_set_enabled(self, enabled: bool) -> None:
        self._start_line_edit.setEnabled(enabled)
        self._end_line_edit.setEnabled(enabled)
        self._display_button.setEnabled(enabled)
        self._one_day_before_button.setEnabled(enabled)
        self._one_hour_before_button.setEnabled(enabled)
        self._one_hour_after_button.setEnabled(enabled)
        self._one_day_after_button.setEnabled(enabled)
        self._tlimit_button.setEnabled(enabled)
