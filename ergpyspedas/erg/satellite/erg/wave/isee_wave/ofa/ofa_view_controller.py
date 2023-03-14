from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, List, Optional, Tuple

import matplotlib
import matplotlib.dates
from matplotlib.axes import Axes
from matplotlib.backend_bases import LocationEvent
from matplotlib.backend_tools import Cursors
from PySide6 import QtCore, QtWidgets
from pyspedas import time_double, time_string

from .load_ofa import load_ofa
from .ofa_view import OFAView, OFAViewOption
from .plot_ofa import plot_ofa

if TYPE_CHECKING:
    from ..wfc.wfc_view_controller import WFCViewControllerTlimitInterface


class _TlimitMode(Enum):
    no_data = auto()
    closed = auto()
    ofa = auto()
    wfc = auto()


class _PositionInXAxis(Enum):
    left = auto()
    inside = auto()
    right = auto()


class OFAViewControllerTlimitInterface(ABC):
    @abstractmethod
    def is_visible(self) -> bool:
        pass

    @abstractmethod
    def can_use_wfc_tlimit(self) -> bool:
        pass

    @abstractmethod
    def on_wfc_tlimit_button_clicked(self) -> None:
        pass


class OFAViewController(OFAViewControllerTlimitInterface):
    def __init__(self, options: OFAViewOption = OFAViewOption()) -> None:
        super().__init__()
        # View
        self._view = OFAView(options)
        self._view_options = options
        # Events
        self._view._display_button.clicked.connect(self.on_display_button_clicked)  # type: ignore
        self._view._one_day_before_button.clicked.connect(  # type: ignore
            self.on_one_day_before_button_clicked
        )
        self._view._one_hour_before_button.clicked.connect(  # type: ignore
            self.on_one_hour_before_button_clicked
        )
        self._view._one_hour_after_button.clicked.connect(  # type: ignore
            self.on_one_hour_after_button_clicked
        )
        self._view._one_day_after_button.clicked.connect(  # type: ignore
            self.on_one_day_after_button_clicked
        )
        self._view._tlimit_button.clicked.connect(self.on_tlimit_button_clicked)  # type: ignore
        # States
        self._has_plotted = False
        self._tlimit_mode = _TlimitMode.no_data
        self._is_tlimit_first_press = True
        self._trange: Optional[Tuple[float, float]] = None
        self._last_trange: Optional[Tuple[float, float]] = None
        self._tlimit_start: Optional[float] = None
        self._tlimit_start_x_axis_pos: Optional[_PositionInXAxis] = None
        # Other
        self._view._canvas.set_cursor(Cursors.SELECT_REGION)
        self._wfc_view_controller: "Optional[WFCViewControllerTlimitInterface]" = None

    def inject(self, wfc_view_controller: "WFCViewControllerTlimitInterface") -> None:
        # Used to cooperate with WFC panel
        self.wfc_view_controller = wfc_view_controller

    def show(self) -> None:
        self._view.show()

    def is_visible(self) -> bool:
        # If window is minimized by upper left button, this is True
        # If window is closed by upper left button, this is False
        return self._view.isVisible()

    def _get_trange_from_line_edit_text(self) -> Optional[Tuple[float, float]]:
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
        if start_time >= end_time:  # type: ignore
            QtWidgets.QMessageBox.warning(
                self._view, "Warning", "Invalid time interval was specified."
            )
            return

        return start_time, end_time  # type: ignore

    def _update_time(self, trange: Tuple[float, float]) -> bool:
        # Presentation logic
        # Check if there is new time that is not within last trange
        has_new_time = self._trange is None or (
            trange[0] < self._trange[0] or trange[1] > self._trange[1]
        )
        self._last_trange = self._trange
        self._trange = trange
        return has_new_time

    def on_display_button_clicked(self) -> None:
        trange = self._get_trange_from_line_edit_text()
        if trange is None:
            return
        has_new_time = self._update_time(trange)
        self._load_and_plot_with_dialog(has_new_time)

    def _scroll_time_button_clicked(self, diff_sec: int) -> None:
        trange = self._get_trange_from_line_edit_text()
        if trange is None:
            return
        trange = (trange[0] + diff_sec, trange[1] + diff_sec)
        self._view._start_line_edit.setText(
            time_string(trange[0], fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )
        self._view._end_line_edit.setText(
            time_string(trange[1], fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )

        has_new_time = self._update_time(trange)
        self._load_and_plot_with_dialog(has_new_time)

    def on_one_day_before_button_clicked(self) -> None:
        diff_sec = -24 * 60 * 60
        self._scroll_time_button_clicked(diff_sec)

    def on_one_hour_before_button_clicked(self) -> None:
        diff_sec = -60 * 60
        self._scroll_time_button_clicked(diff_sec)

    def on_one_hour_after_button_clicked(self) -> None:
        diff_sec = 60 * 60
        self._scroll_time_button_clicked(diff_sec)

    def on_one_day_after_button_clicked(self) -> None:
        diff_sec = 24 * 60 * 60
        self._scroll_time_button_clicked(diff_sec)

    def _load_and_plot_with_dialog(self, load: bool) -> None:
        # Dialog similar to IDL version
        dialog = QtWidgets.QDialog(self._view)
        dialog.setWindowTitle("OFA process")
        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel("Downloading/Importing data...")
        layout.addWidget(label)
        layout.addStretch()
        dialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        dialog.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, on=False)
        dialog.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, on=False)
        dialog.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, on=False)
        dialog.show()
        # Need to directly process event to show the dialog immediately
        QtWidgets.QApplication.processEvents()

        if load:
            self._load()
        self._plot()

        dialog.close()

    def _load(self) -> None:
        if self._trange is None:
            return
        # TODO: Only for development
        import os

        no_update = os.getenv("WAVE_NO_UPDATE") == "True"

        self._var_label_dict = load_ofa(trange=self._trange, no_update=no_update)
        self._n_plots = 4

    def _plot(self) -> None:
        if self._trange is None:
            return
        # Plot data
        fig = self._view._canvas.figure
        fig = plot_ofa(
            fig=fig,
            trange=self._trange,
            orb_dict=self._var_label_dict,
            font_size=self._view_options.font_size,
        )
        # Enable some GUI after initial plot
        if not self._has_plotted:
            self._view._canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
            self._view._canvas.mpl_connect("button_press_event", self.on_button_pressed)
            self._has_plotted = True
            self._tlimit_mode = _TlimitMode.closed
        # Must be before self._view.canvas.draw()
        self._initialize_crosshair()
        # Draw data
        self._view._canvas.draw()
        self.bg = self._view._canvas.copy_from_bbox(self._view._canvas.figure.bbox)

    def on_tlimit_button_clicked(self) -> None:
        if self._tlimit_mode in [_TlimitMode.no_data, _TlimitMode.wfc]:
            return

        self._tlimit_mode = _TlimitMode.ofa
        # Disable some GUIs
        self._view._start_line_edit.setEnabled(False)
        self._view._end_line_edit.setEnabled(False)
        self._view._display_button.setEnabled(False)
        self._view._one_day_before_button.setEnabled(False)
        self._view._one_hour_before_button.setEnabled(False)
        self._view._one_hour_after_button.setEnabled(False)
        self._view._one_day_after_button.setEnabled(False)
        self._view._tlimit_button.setEnabled(False)

    def can_use_wfc_tlimit(self) -> bool:
        return self._tlimit_mode == _TlimitMode.closed

    def on_wfc_tlimit_button_clicked(self) -> None:
        if self._tlimit_mode in [_TlimitMode.no_data, _TlimitMode.ofa]:
            return

        # Bring OFA to front
        self._view.setWindowState(
            self._view.windowState() & ~QtCore.Qt.WindowState.WindowMinimized
            | QtCore.Qt.WindowState.WindowActive
        )
        self._view.activateWindow()

        self._tlimit_mode = _TlimitMode.wfc
        # Disable some GUIs
        self._view._start_line_edit.setEnabled(False)
        self._view._end_line_edit.setEnabled(False)
        self._view._display_button.setEnabled(False)
        self._view._one_day_before_button.setEnabled(False)
        self._view._one_hour_before_button.setEnabled(False)
        self._view._one_hour_after_button.setEnabled(False)
        self._view._one_day_after_button.setEnabled(False)
        self._view._tlimit_button.setEnabled(False)

    def _initialize_crosshair(self) -> None:
        # Initialize horizontal and vertical line of crosshair for all data plot
        self.hlines = []
        self.vlines = []
        # Initialize vertical line used while tlimit mode
        self.tlimit_first_vlines = []
        self.tlimit_second_vlines = []
        for i in range(self._n_plots):
            ax: Axes = self._view._canvas.figure.axes[i]
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

    def _get_nearest_axes_and_coords(
        self, event: LocationEvent
    ) -> Optional[Tuple[Axes, float, float, _PositionInXAxis]]:
        axs: List[Axes] = self._view._canvas.figure.axes[: self._n_plots]
        if len(axs) == 0:
            return
        # Pixel coordinate of cursor
        x, y = event.x, event.y
        if x is None or y is None:
            return None

        # Get data x coordinate of cursor
        # Since tplot axs share x axis, using only one ax is sufficient
        ax = axs[0]
        # Get pixel x coordinate of ax
        # Assume transform has no rotation components
        trans = ax.transAxes
        x_left, _ = trans.transform((0, 0))
        x_right, _ = trans.transform((1, 0))
        # If cursor is outside ax in terms of x axis, move it inside ax virtually
        if x < x_left:
            x = x_left
            x_axis_pos = _PositionInXAxis.left
        elif x > x_right:
            x = x_right
            x_axis_pos = _PositionInXAxis.right
        else:
            x_axis_pos = _PositionInXAxis.inside
        # Pixel coordinate to data coordinate
        trans = ax.transData.inverted()
        xdata, _ = trans.transform((x, 0))

        # Get data y coordinate of cursor
        # Assume tplot subplots have only one columns
        # Get pixel y coordinate of axs
        y_bottoms = []
        y_tops = []
        for ax in axs:
            trans = ax.transAxes
            _, y_bottom = trans.transform((0, 0))
            _, y_top = trans.transform((0, 1))
            y_bottoms.append(y_bottom)
            y_tops.append(y_top)

        # If cursor is inside one of the axs in terms of y axis,
        # get data y coordinate using the ax
        ydata = None
        for ax, y_bottom, y_top in zip(axs, y_bottoms, y_tops):
            if y_bottom <= y <= y_top:
                ax_nearest = ax
                trans = ax.transData.inverted()
                _, ydata = trans.transform((0, y))
                return ax_nearest, xdata, ydata, x_axis_pos

        # If cursor is outside any of the axs in terms of y axis,
        # get data y coordinate using the nearest ax
        dy = float("inf")
        ax_nearest = None
        for ax, y_bottom, y_top in zip(axs, y_bottoms, y_tops):
            dy_bottom = abs(y - y_bottom)
            if dy_bottom < dy:
                dy = dy_bottom
                ax_nearest = ax
            dy_top = abs(y - y_top)
            if dy_top < dy:
                dy = dy_top
                ax_nearest = ax
        assert ax_nearest is not None
        trans = ax_nearest.transData.inverted()
        _, ydata = trans.transform((0, y))
        return ax_nearest, xdata, ydata, x_axis_pos

    def on_mouse_move(self, event: LocationEvent) -> None:
        ret = self._get_nearest_axes_and_coords(event)
        if ret is None:
            return
        ax_nearest, x, y, _ = ret

        # Always show time of corresponding cursor position
        self._view._time_label.setText(
            time_string(matplotlib.dates.num2date(x).timestamp(), fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )

        # Following occurs in tlimit mode only
        if self._tlimit_mode in [_TlimitMode.no_data, _TlimitMode.closed]:
            return

        # Use blitting for faster screen update
        # Reset background (without crosshair)
        self._view._canvas.restore_region(self.bg)
        # Add crosshair
        index = self._view._canvas.figure.axes.index(ax_nearest)
        for i in range(self._n_plots):
            ax = self._view._canvas.figure.axes[i]
            # Draw vertical line for all plot
            vline = self.vlines[i]
            vline.set_xdata([x])
            vline.set_visible(True)
            ax.draw_artist(vline)
            # Horizontal line should be only visible in event.inaxes
            hline = self.hlines[i]
            if i == index:
                hline.set_ydata([y])
                hline.set_visible(True)
            else:
                hline.set_visible(False)
            ax.draw_artist(hline)
        # Update
        self._view._canvas.blit()

    def _draw_tlimit_lines_background(
        self, x: float, is_tlimit_first_press: bool
    ) -> None:
        # Cases
        lines = []
        for i in range(self._n_plots):
            if is_tlimit_first_press:
                line = self.tlimit_first_vlines[i]
            else:
                line = self.tlimit_second_vlines[i]
            lines.append(line)
        # Reset background
        self._view._canvas.restore_region(self.bg)
        # Add tlimit first vlines to background
        for i in range(self._n_plots):
            ax = self._view._canvas.figure.axes[i]
            line = lines[i]
            line.set_xdata([x])
            line.set_visible(True)
            ax.draw_artist(line)
        # Update background
        self.bg = self._view._canvas.copy_from_bbox(self._view._canvas.figure.bbox)
        # Reset tlimit first vlines
        for line in lines:
            line.set_visible(False)
        # Update
        self._view._canvas.blit()

    def _on_tlimit_ofa_first_pressed(self, x: float, tlimit_start: float) -> None:
        self._view._start_line_edit.setText(
            time_string(tlimit_start, fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )
        self._draw_tlimit_lines_background(x, True)

    def _on_tlimit_ofa_second_pressed(
        self, x: float, needs_load: bool, trange: Tuple[float, float]
    ) -> None:
        self._draw_tlimit_lines_background(x, False)
        self._load_and_plot_with_dialog(needs_load)
        self._view._start_line_edit.setEnabled(True)
        self._view._end_line_edit.setEnabled(True)
        self._view._display_button.setEnabled(True)
        self._view._one_day_before_button.setEnabled(True)
        self._view._one_hour_before_button.setEnabled(True)
        self._view._one_hour_after_button.setEnabled(True)
        self._view._one_day_after_button.setEnabled(True)
        self._view._tlimit_button.setEnabled(True)
        self._view._start_line_edit.setText(
            time_string(trange[0], fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )
        self._view._end_line_edit.setText(
            time_string(trange[1], fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )

    def _on_tlimit_wfc_first_pressed(self, x: float) -> None:
        self._draw_tlimit_lines_background(x, True)

    def _on_tlimit_wfc_second_pressed(self, x: float) -> None:
        self._draw_tlimit_lines_background(x, False)
        self._plot()
        self._view._start_line_edit.setEnabled(True)
        self._view._end_line_edit.setEnabled(True)
        self._view._display_button.setEnabled(True)
        self._view._one_day_before_button.setEnabled(True)
        self._view._one_hour_before_button.setEnabled(True)
        self._view._one_hour_after_button.setEnabled(True)
        self._view._one_day_after_button.setEnabled(True)
        self._view._tlimit_button.setEnabled(True)

    def _on_tlimit_ofa_pressed(
        self,
        tlimit_time: float,
        x: float,
        x_axis_pos: _PositionInXAxis,
    ) -> None:
        if self._is_tlimit_first_press:
            # Presentation logic
            self._tlimit_start = tlimit_time
            self._tlimit_start_x_axis_pos = x_axis_pos
            self._is_tlimit_first_press = False

            # View
            self._on_tlimit_ofa_first_pressed(x, self._tlimit_start)
        else:
            # Presentation logic
            assert self._tlimit_start is not None
            assert self._tlimit_start_x_axis_pos is not None
            assert self._trange is not None
            tlimit_start = self._tlimit_start
            tlimit_start_x_axis_pos = self._tlimit_start_x_axis_pos
            tlimit_end = tlimit_time
            tlimit_end_x_axis_pos = x_axis_pos

            # tlimit previous
            current_start, current_end = self._trange
            diff = current_end - current_start
            if (
                tlimit_start_x_axis_pos == _PositionInXAxis.left
                and tlimit_end_x_axis_pos == _PositionInXAxis.left
            ):
                trange = (current_start - diff, current_end - diff)
            elif (
                tlimit_start_x_axis_pos == _PositionInXAxis.right
                and tlimit_end_x_axis_pos == _PositionInXAxis.right
            ):
                trange = (current_start + diff, current_end + diff)
            else:
                # tlimit normal
                if tlimit_end > tlimit_start:
                    trange = (tlimit_start, tlimit_end)
                elif tlimit_end == tlimit_start:
                    trange = (tlimit_start, tlimit_end + 1)
                # tlimit last
                else:
                    # If tlimit last done right after initial plot, dismiss
                    if self._last_trange is None:
                        trange = self._trange
                    else:
                        trange = self._last_trange

            self._is_tlimit_first_press = True
            self._tlimit_mode = _TlimitMode.closed
            needs_load = self._update_time(trange)
            self._tlimit_start = None

            # View
            self._on_tlimit_ofa_second_pressed(x, needs_load, trange)

    def _on_tlimit_wfc_pressed(
        self,
        tlimit_time: float,
        x: float,
    ) -> None:
        if self._is_tlimit_first_press:
            # Presentation logic
            self._tlimit_start = tlimit_time
            self._is_tlimit_first_press = False

            # View
            self._on_tlimit_wfc_first_pressed(x)
            if (
                self.wfc_view_controller is not None
                and self.wfc_view_controller.is_visible()
            ):
                self.wfc_view_controller.on_tlimit_wfc_first_pressed(self._tlimit_start)
        else:
            # Presentation logic
            assert self._tlimit_start is not None
            tlimit_start = self._tlimit_start
            tlimit_end = tlimit_time
            # tlimit normal
            if tlimit_end > tlimit_start:
                trange = (tlimit_start, tlimit_end)
            elif tlimit_end == tlimit_start:
                trange = (tlimit_start, tlimit_end + 1)
            else:
                trange = (tlimit_end, tlimit_start)

            self._is_tlimit_first_press = True
            self._tlimit_mode = _TlimitMode.closed
            self._tlimit_start = None

            # View
            self._on_tlimit_wfc_second_pressed(x)
            if (
                self.wfc_view_controller is not None
                and self.wfc_view_controller.is_visible()
            ):
                self.wfc_view_controller.on_tlimit_wfc_second_pressed(trange)

    def on_button_pressed(self, event) -> None:
        # View
        ret = self._get_nearest_axes_and_coords(event)
        if ret is None:
            return
        _, x, _, x_axis_pos = ret
        tlimit_time = matplotlib.dates.num2date(x).timestamp()

        # Presentation logic
        if self._tlimit_mode in [_TlimitMode.no_data, _TlimitMode.closed]:
            return
        elif self._tlimit_mode == _TlimitMode.ofa:
            self._on_tlimit_ofa_pressed(tlimit_time, x, x_axis_pos)
        elif self._tlimit_mode == _TlimitMode.wfc:
            self._on_tlimit_wfc_pressed(tlimit_time, x)
        else:
            raise ValueError


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    vc = OFAViewController()
    vc.show()
    app.exec()
