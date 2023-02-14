from enum import Enum, auto

import matplotlib as mpl
from matplotlib.backend_tools import Cursors
from PySide6 import QtCore, QtWidgets
from pyspedas import time_double, time_string
from pytplot import get_data, store_data, tplot_names

from ofa_view import OFAView
from plot_ofa import load_ofa, plot_ofa


class TlimitMode(Enum):
    no_data = auto()
    closed = auto()
    ofa = auto()
    wfc = auto()


class OFAViewController:
    def __init__(self) -> None:
        super().__init__()
        # TODO: settings
        tnames = tplot_names()
        if "ofa_xsize" in tnames:
            ofa_xsize = get_data("ofa_xsize")["y"][0]
            store_data("ofa_xsize", delete=True)
        else:
            ofa_xsize = 1280
        if "ofa_ysize" in tnames:
            ofa_ysize = get_data("ofa_ysize")["y"][0]
            store_data("ofa_ysize", delete=True)
        else:
            ofa_ysize = 600
        # TODO: no default value in IDL version
        if "font_size" in tnames:
            font_size = get_data("font_size")["y"][0]
        else:
            font_size = 1.0
        dpi = 100
        # View
        self._view = OFAView()
        # Events
        self._view._display_button.clicked.connect(self.display_button_clicked)
        self._view._one_day_before_button.clicked.connect(
            self.one_day_before_button_clicked
        )
        self._view._one_hour_before_button.clicked.connect(
            self.one_hour_before_button_clicked
        )
        self._view._one_hour_after_button.clicked.connect(
            self.one_hour_after_button_clicked
        )
        self._view._one_day_after_button.clicked.connect(
            self.one_day_after_button_clicked
        )
        self._view._tlimit_button.clicked.connect(self.tlimit_button_clicked)
        # States
        self._plotted = False
        self._tlimit_mode = TlimitMode.no_data
        self._click_flg = False
        self._start_time = time_double("2017-04-01/00:00:00")
        self._end_time = time_double("2017-04-01/23:59:59")
        self._view._canvas.set_cursor(Cursors.SELECT_REGION)

    def show(self) -> None:
        self._view.show()

    def one_day_before_button_clicked(self) -> None:
        delta = -24 * 60 * 60
        self._start_time += delta
        self._end_time += delta
        self._view._start_line_edit.setText(
            time_string(self._start_time, fmt="%Y-%m-%d/%H:%M:%S")
        )
        self._view._end_line_edit.setText(
            time_string(self._end_time, fmt="%Y-%m-%d/%H:%M:%S")
        )
        self._load_and_plot_with_dialog(True)

    def one_hour_before_button_clicked(self) -> None:
        delta = -60 * 60
        self._start_time += delta
        self._end_time += delta
        self._view._start_line_edit.setText(
            time_string(self._start_time, fmt="%Y-%m-%d/%H:%M:%S")
        )
        self._view._end_line_edit.setText(
            time_string(self._end_time, fmt="%Y-%m-%d/%H:%M:%S")
        )
        self._load_and_plot_with_dialog(True)

    def one_hour_after_button_clicked(self) -> None:
        delta = 60 * 60
        self._start_time += delta
        self._end_time += delta
        self._view._start_line_edit.setText(
            time_string(self._start_time, fmt="%Y-%m-%d/%H:%M:%S")
        )
        self._view._end_line_edit.setText(
            time_string(self._end_time, fmt="%Y-%m-%d/%H:%M:%S")
        )
        self._load_and_plot_with_dialog(True)

    def one_day_after_button_clicked(self) -> None:
        delta = 24 * 60 * 60
        self._start_time += delta
        self._end_time += delta
        self._view._start_line_edit.setText(
            time_string(self._start_time, fmt="%Y-%m-%d/%H:%M:%S")
        )
        self._view._end_line_edit.setText(
            time_string(self._end_time, fmt="%Y-%m-%d/%H:%M:%S")
        )
        self._load_and_plot_with_dialog(True)

    def display_button_clicked(self) -> None:
        # Input validation
        start_line_edit_text = self._view._start_line_edit.text()
        end_line_edit_text = self._view._end_line_edit.text()
        try:
            start_time = time_double(start_line_edit_text)
        except:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Invalid start time format. YYYY-MM-DD/hh:mm:ss is accepted.",
            )
            return
        try:
            end_time = time_double(end_line_edit_text)
        except:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Invalid end time format. YYYY-MM-DD/hh:mm:ss is accepted.",
            )
            return
        if start_time >= end_time:
            QtWidgets.QMessageBox.warning(
                self._view, "Warning", "Invalid time interval was specified."
            )
            return
        self._start_time = start_time
        self._end_time = end_time
        # Load and plot
        self._load_and_plot_with_dialog(True)

    def _load_and_plot_with_dialog(self, load: bool) -> None:
        # TODO: QDialog may show Not responding to window title if several seconds passed
        # TODO: Manage keyboard shortcut
        dialog = QtWidgets.QDialog(self._view)
        dialog.setWindowTitle("OFA process")
        dialog.layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel("Downloading/Importing data...")
        dialog.layout.addWidget(label)
        dialog.layout.addStretch()
        dialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        dialog.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, on=False)
        dialog.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, on=False)
        dialog.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, on=False)
        dialog.show()
        QtWidgets.QApplication.processEvents()
        if load:
            self._load()
        self._plot()
        dialog.close()

    def _load(self) -> None:
        # Load data
        import os

        no_update = os.getenv("WAVE_NO_UPDATE") == "True"

        self.ofa_tplotlist, self.var_label_list = load_ofa(
            trange=[self._start_time, self._end_time], no_update=no_update
        )
        self._n_plots = len(self.ofa_tplotlist)

    def _plot(self) -> None:
        # Plot data
        fig = self._view._canvas.figure
        fig = plot_ofa(
            fig,
            [self._start_time, self._end_time],
            self.ofa_tplotlist,
            self.var_label_list,
        )
        # TODO: needed in add new figure but not in update black current figure
        # TODO: Connect events only once when first plot is done
        if not self._plotted:
            self._view._canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
            self._view._canvas.mpl_connect("button_press_event", self.on_button_pressed)
            # self._view._canvas.mpl_connect("draw_event", self.on_draw)
            # TODO: two same states
            self._plotted = True
            self._tlimit_mode = TlimitMode.closed
        self.setup_cursor()
        # must be after self.setup_cursor()
        self._view._canvas.draw()
        self.bg = self._view._canvas.copy_from_bbox(self._view._canvas.figure.bbox)

    def tlimit_button_clicked(self) -> None:
        # TODO: is same as self._plotted
        if self._tlimit_mode == TlimitMode.no_data:
            return
        self._tlimit_mode = TlimitMode.ofa

    def setup_cursor(self) -> None:
        self.hlines = []
        self.vlines = []
        self.tlimit_first_vlines = []
        self.tlimit_second_vlines = []
        for i in range(self._n_plots):
            ax = self._view._canvas.figure.axes[i]
            hline = ax.axhline(0, visible=False, animated=True, color="black")
            vline = ax.axvline(0, visible=False, animated=True, color="black")
            tlimit_first_vline = ax.axvline(
                0, visible=False, animated=True, color="cyan"
            )
            tlimit_second_vline = ax.axvline(
                0, visible=False, animated=True, color="magenta"
            )
            self.vlines.append(vline)
            self.hlines.append(hline)
            self.tlimit_first_vlines.append(tlimit_first_vline)
            self.tlimit_second_vlines.append(tlimit_second_vline)

    def on_mouse_move(self, event) -> None:
        if event.inaxes not in self._view._canvas.figure.axes[: self._n_plots]:
            return
        x, y = event.xdata, event.ydata
        # This event is GUI but only available inside plot
        self._view._time_label.setText(
            time_string(mpl.dates.num2date(x).timestamp(), fmt="%Y-%m-%d/%H:%M:%S")
        )
        if self._tlimit_mode in [TlimitMode.no_data, TlimitMode.closed]:
            return
        # Reset background
        self._view._canvas.restore_region(self.bg)
        # Add cursor
        index = self._view._canvas.figure.axes.index(event.inaxes)
        for i in range(self._n_plots):
            ax = self._view._canvas.figure.axes[i]
            # vline
            vline = self.vlines[i]
            vline.set_xdata(x)
            vline.set_visible(True)
            ax.draw_artist(vline)
            # hline should be only visible in event.inaxes
            hline = self.hlines[i]
            if i == index:
                hline.set_ydata(y)
                hline.set_visible(True)
            else:
                hline.set_visible(False)
            ax.draw_artist(hline)
        # Update
        self._view._canvas.blit()

    def on_button_pressed(self, event) -> None:
        if event.inaxes not in self._view._canvas.figure.axes[: self._n_plots]:
            return

        if self._tlimit_mode in [TlimitMode.no_data, TlimitMode.closed]:
            return

        elif self._tlimit_mode == TlimitMode.ofa:
            x = event.xdata
            if not self._click_flg:
                # Presentation logic
                self._start_time = mpl.dates.num2date(x).timestamp()
                self._click_flg = True
                # View
                self._view._start_line_edit.setText(
                    time_string(self._start_time, fmt="%Y-%m-%d/%H:%M:%S")
                )
                # Reset background
                self._view._canvas.restore_region(self.bg)
                # Add tlimit first vlines to background
                for i in range(self._n_plots):
                    ax = self._view._canvas.figure.axes[i]
                    line = self.tlimit_first_vlines[i]
                    line.set_xdata(x)
                    line.set_visible(True)
                    ax.draw_artist(line)
                # Update background
                self.bg = self._view._canvas.copy_from_bbox(
                    self._view._canvas.figure.bbox
                )
                # Reset tlimit first vlines
                for line in self.tlimit_first_vlines:
                    line.set_visible(False)
                # Update
                self._view._canvas.blit()
            else:
                # TODO: what happens if equal?
                # Presentation logic
                t = mpl.dates.num2date(x).timestamp()
                if t <= self._start_time:
                    self._end_time = self._start_time
                    self._start_time = t
                else:
                    self._end_time = t
                self._click_flg = False
                self._tlimit_mode = TlimitMode.closed
                # View
                self._view._end_line_edit.setText(
                    time_string(self._end_time, fmt="%Y-%m-%d/%H:%M:%S")
                )
                # Reset background
                self._view._canvas.restore_region(self.bg)
                # Add tlimit second vlines to background
                for i in range(self._n_plots):
                    ax = self._view._canvas.figure.axes[i]
                    line = self.tlimit_second_vlines[i]
                    line.set_xdata(x)
                    line.set_visible(True)
                    ax.draw_artist(line)
                # Update background
                self.bg = self._view._canvas.copy_from_bbox(
                    self._view._canvas.figure.bbox
                )
                # Reset tlimit second vlines
                for line in self.tlimit_second_vlines:
                    line.set_visible(False)
                # Update
                self._view._canvas.blit()
                # Model
                # TODO: Do not need load here
                self._load_and_plot_with_dialog(False)

        elif self._tlimit_mode == TlimitMode.wfc:
            pass
            # TODO: wfc
            # Need this for wfc
            # QtWidgets.QMessageBox.information(
            #     self._view,
            #     "Information",
            #     "New time interval has been set successfully.",
            # )

        else:
            raise ValueError


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    vc = OFAViewController()
    vc.show()
    app.exec()
