from __future__ import annotations

import copy
import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from functools import partial
from queue import Empty, Queue
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple, Union

from PySide6 import QtCore, QtWidgets
from pyspedas import time_double, time_string
from pyspedas.erg.satellite.erg.config import CONFIG
from pytplot import tplot_save

from ..options.data_option import DataName, DataOptions
from ..options.orbital_info_option import OrbitalInfoName, OrbitalInfoOption
from ..options.support_line_option import SupportLineOptions
from ..options.wfc_view_option import WFCViewOption, WFCViewOptionOther
from ..plot.common import plot_init
from ..utils.progress_manager import (
    ProgressManager,
    ProgressManagerForThreadController,
    WorkerInterface,
)
from ..utils.utils import round_down, round_up, str_to_float_or_none, str_to_int_or_none
from .add_fc import add_fc
from .load_wfc import load_wfc
from .mask import MaskManagers
from .plot_wfc import plot_wfc
from .wfc_view import WFCView

if TYPE_CHECKING:
    from ..ofa.ofa_view_controller import OFAViewControllerTlimitInterface


class Worker(WorkerInterface):
    def __init__(
        self,
        queue: Queue,
        trange: Union[Sequence[str], Sequence[float], Sequence[datetime]] = [
            "2017-04-01/13:57:45",
            "2017-04-01/13:57:53",
        ],
        w: str = "Hanning",
        nfft: int = 4096,
        stride: int = 2048,
        n_average: int = 3,
        no_update: bool = False,
    ) -> None:
        super().__init__()
        self.queue = queue
        self.trange = trange
        self.w = w
        self.nfft = nfft
        self.stride = stride
        self.n_average = n_average
        self.no_update = no_update

    def run(self) -> None:
        result = load_wfc(
            trange=self.trange,
            w=self.w,
            nfft=self.nfft,
            stride=self.stride,
            n_average=self.n_average,
            no_update=self.no_update,
            worker=self,
            progress_manager=self.progress_manager,
        )
        self.queue.put(result)


class WFCViewControllerTlimitInterface(ABC):
    @abstractmethod
    def is_visible(self) -> bool:
        pass

    @abstractmethod
    def on_tlimit_wfc_first_pressed(self, tlimit_start: float) -> None:
        pass

    @abstractmethod
    def on_tlimit_wfc_second_pressed(self, trange: Tuple[float, float]) -> None:
        pass


class WFCViewController(
    WFCViewControllerTlimitInterface, ProgressManagerForThreadController
):
    def __init__(
        self,
        view_options: WFCViewOption = WFCViewOption(),
        view_options_other: WFCViewOptionOther = WFCViewOptionOther(),
    ) -> None:
        # Settings
        self._view_options = view_options
        self._view_options_other = view_options_other
        self._data_options = DataOptions.from_dict()
        self._load_config()
        # Backup settings used in resetting
        self._data_options_bak = copy.deepcopy(self._data_options)
        self._support_line_options_bak = copy.deepcopy(self._support_line_options)
        self._orbital_info_options_bak = copy.deepcopy(self._orbital_info_options)

        # Data
        self._trange: Optional[Tuple[float, float]] = None
        self._orbital_infos: Dict[OrbitalInfoName, str] = {}
        self._species: List[str] = []
        self._ofa_view_controller: "Optional[OFAViewControllerTlimitInterface]" = None
        self._has_plotted = False

        # View
        self._view = WFCView(
            data_options=self._data_options,
            orbital_info_options=self._orbital_info_options,
            support_line_options=self._support_line_options,
            view_options=self._view_options,
        )

        # Events
        # General
        self._view._tlimit_button.clicked.connect(self.on_tlimit_button_clicked)  # type: ignore
        self._view._fft_calc_button.clicked.connect(self.on_fft_calc_button_clicked)  # type: ignore
        self._view._fft_revert_button.clicked.connect(self.on_fft_revert_button_clicked)  # type: ignore
        # Options tab
        self._view._options_tab._support_lines_apply_button.clicked.connect(  # type: ignore
            self.on_support_lines_apply_button_clicked
        )
        self._view._options_tab._support_lines_add_button.clicked.connect(  # type: ignore
            self.on_support_lines_add_button_clicked
        )
        self._view._options_tab._support_lines_delete_button.clicked.connect(  # type: ignore
            self.on_support_lines_delete_button_clicked
        )
        self._view._options_tab._support_lines_reset_button.clicked.connect(  # type: ignore
            self.on_support_lines_reset_button_clicked
        )
        self._view._options_tab._xyzaxis_apply_button.clicked.connect(  # type: ignore
            self.on_xyz_apply_button_clicked
        )
        self._view._options_tab._xyzaxis_reset_button.clicked.connect(  # type: ignore
            self.on_xyz_reset_button_clicked
        )
        # Event to sync information with mask tab is raised on limit and log button
        self._view._options_tab.yaxis_widgets.title.editingFinished.connect(  # type: ignore
            self.on_yaxis_title_editing_finished
        )
        self._view._options_tab.yaxis_widgets.ymin.editingFinished.connect(  # type: ignore
            self.on_yaxis_ymin_editing_finished
        )
        self._view._options_tab.yaxis_widgets.ymax.editingFinished.connect(  # type: ignore
            self.on_yaxis_ymax_editing_finished
        )
        self._view._options_tab.yaxis_widgets.ylog.stateChanged.connect(  # type: ignore
            self.on_yaxis_log_state_changed
        )
        for name, zaxis_widgets in self._view._options_tab._zaxis_widgets.items():
            zaxis_widgets.title.editingFinished.connect(  # type: ignore
                partial(self.on_zaxis_title_editing_finished, name)
            )
            zaxis_widgets.zmin.editingFinished.connect(  # type: ignore
                partial(self.on_zaxis_zmin_editing_finished, name)
            )
            zaxis_widgets.zmax.editingFinished.connect(  # type: ignore
                partial(self.on_zaxis_zmax_editing_finished, name)
            )
            zaxis_widgets.zlog.stateChanged.connect(  # type: ignore
                partial(self.on_zaxis_zlog_state_changed, name)
            )
            zaxis_widgets.mask.stateChanged.connect(  # type: ignore
                partial(self.on_zaxis_mask_state_changed, name)
            )
            zaxis_widgets.plot.stateChanged.connect(  # type: ignore
                partial(self.on_zaxis_plot_state_changed, name)
            )
        # Mask tab
        for name, group in self._view._mask_tab._slider_groups.items():
            group._slider.valueChanged.connect(  # type: ignore
                partial(self.on_mask_tab_slider_value_changed, name)
            )
            group._line_edit.editingFinished.connect(  # type: ignore
                partial(self.on_mask_tab_line_edit_editing_finished, name)
            )

        self._view._mask_tab._apply_button.clicked.connect(  # type: ignore
            self.on_mask_tab_apply_button_clicked
        )
        self._view._mask_tab._reset_button.clicked.connect(  # type: ignore
            self.on_mask_tab_reset_button_clicked
        )
        # Output tab
        self._view._output_tab._eps_button.clicked.connect(  # type: ignore
            self.on_output_tab_eps_button_clicked
        )
        self._view._output_tab._png_button.clicked.connect(  # type: ignore
            self.on_output_tab_png_button_clicked
        )
        self._view._output_tab._tplot_button.clicked.connect(  # type: ignore
            self.on_output_tab_tplot_button_clicked
        )

    def inject(self, ofa_view_controller: "OFAViewControllerTlimitInterface") -> None:
        # Used to cooperate with OFA panel
        self._ofa_view_controller = ofa_view_controller

    def show(self) -> None:
        self._view.show()

    def is_visible(self) -> bool:
        # If window is minimized by upper left button, this is True
        # If window is closed by upper left button, this is False
        return self._view.isVisible()

    # GUI
    def on_tlimit_button_clicked(self) -> None:
        # Input
        if (
            self._ofa_view_controller is None
            or not self._ofa_view_controller.is_visible()
            or not self._ofa_view_controller.can_use_wfc_tlimit()
        ):
            return
        # View
        # Disable any input in WFC
        self._view.setEnabled(False)
        # Presentation logic
        self._ofa_view_controller.on_wfc_tlimit_button_clicked()

    def on_tlimit_wfc_first_pressed(self, tlimit_start: float) -> None:
        self._view._start_line_edit.setText(
            time_string(round_down(tlimit_start, ndigits=3), fmt="%Y-%m-%d/%H:%M:%S.%f")[:-3]  # type: ignore
        )

    def on_tlimit_wfc_second_pressed(self, trange: Tuple[float, float]) -> None:
        self._view._start_line_edit.setText(
            time_string(round_down(trange[0], ndigits=3), fmt="%Y-%m-%d/%H:%M:%S.%f")[:-3]  # type: ignore
        )
        self._view._end_line_edit.setText(
            time_string(round_up(trange[1], ndigits=3), fmt="%Y-%m-%d/%H:%M:%S.%f")[:-3]  # type: ignore
        )
        # Focus on WFC window
        view = self._view
        view.setWindowState(
            view.windowState() & ~QtCore.Qt.WindowState.WindowMinimized
            | QtCore.Qt.WindowState.WindowActive
        )
        view.activateWindow()
        # Enable any input in WFC
        view.setEnabled(True)
        QtWidgets.QMessageBox.information(
            view,
            "Information",
            "New time interval has been set successfully.",
        )

    def _get_trange_from_line_edit_text(self) -> Optional[Tuple[float, float]]:
        start_line_edit_text = self._view._start_line_edit.text()
        end_line_edit_text = self._view._end_line_edit.text()

        try:
            start_time: float = time_double(start_line_edit_text)  # type: ignore
        except:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Invalid start time format. YYYY-MM-DD/hh:mm:ss is accepted.",
            )
            return None

        try:
            end_time: float = time_double(end_line_edit_text)  # type: ignore
        except:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Invalid end time format. YYYY-MM-DD/hh:mm:ss is accepted.",
            )
            return None

        if start_time >= end_time:
            QtWidgets.QMessageBox.warning(
                self._view, "Warning", "Invalid time interval was specified."
            )
            return None

        return start_time, end_time  # type: ignore

    def on_fft_revert_button_clicked(self) -> None:
        self._view.setup_fft_options()

    # def on_fft_calc_button_clicked_single_thread(self) -> None:
    #     # Input
    #     trange = self._get_trange_from_line_edit_text()
    #     if trange is None:
    #         return

    #     fft_window = self._view._fft_window_box.currentText()

    #     window_size_text = self._view._window_size_line_edit.text()
    #     window_size = str_to_int_or_none(window_size_text)
    #     if window_size is None or window_size <= 0:
    #         QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "Warning",
    #             "Invalid FFT window size was specified. FFT window size should be a positive value.",
    #         )
    #         return
    #     elif window_size >= 32768:
    #         ret = QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "Question",
    #             "Too large FFT window size was specified. Do you want to continue anyway?",
    #             QtWidgets.QMessageBox.StandardButton.Yes,
    #             QtWidgets.QMessageBox.StandardButton.No,
    #         )
    #         if ret != QtWidgets.QMessageBox.StandardButton.Yes:
    #             return

    #     stride_text = self._view._stride_line_edit.text()
    #     stride = str_to_int_or_none(stride_text)
    #     if stride is None or stride <= 0:
    #         QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "Warning",
    #             "Invalid stride size was specified. Stride size should be a positive value.",
    #         )
    #         return
    #     elif stride >= window_size:
    #         QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "Warning",
    #             "Invalid stride size was specified. Stride size should be equal to or less than FFT window size.",
    #         )
    #         return
    #     elif stride < 128:
    #         ret = QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "Question",
    #             "Too small stride size was specified. Do you want to continue anyway?",
    #             QtWidgets.QMessageBox.StandardButton.Yes,
    #             QtWidgets.QMessageBox.StandardButton.No,
    #         )
    #         if ret != QtWidgets.QMessageBox.StandardButton.Yes:
    #             return

    #     n_average_text = self._view._n_average_line_edit.text()
    #     n_average = str_to_int_or_none(n_average_text)
    #     if n_average is None or n_average <= 0:
    #         QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "Warning",
    #             "Invalid N_average was specified. N_average should be a positive value.",
    #         )
    #         return

    #     progress_manager = ProgressManager(self._view)

    #     # Model
    #     ret = load_wfc(
    #         trange=trange,
    #         w=fft_window,
    #         nfft=window_size,
    #         stride=stride,
    #         n_average=n_average,
    #         progress_manager=progress_manager,
    #     )
    #     if ret is None:
    #         progress_manager.close()
    #         return
    #     (
    #         self._orbital_infos,
    #         self._trange,
    #     ) = ret
    #     self._mask_managers = MaskManagers(self._data_options)
    #     self._plot()

    #     # View
    #     self._view._start_line_edit.setText(
    #         time_string(round_down(self._trange[0], ndigits=3), fmt="%Y-%m-%d/%H:%M:%S.%f")[:-3]  # type: ignore
    #     )
    #     self._view._end_line_edit.setText(
    #         time_string(round_up(self._trange[1], ndigits=3), fmt="%Y-%m-%d/%H:%M:%S.%f")[:-3]  # type: ignore
    #     )
    #     self._update_mask_tab()
    #     for group in self._view._mask_tab._slider_groups.values():
    #         group._slider.setEnabled(True)
    #         group._line_edit.setEnabled(True)

    #     progress_manager.complete()

    def on_fft_calc_button_clicked(self) -> None:
        # Input
        trange = self._get_trange_from_line_edit_text()
        if trange is None:
            return

        fft_window = self._view._fft_window_box.currentText()

        window_size_text = self._view._window_size_line_edit.text()
        window_size = str_to_int_or_none(window_size_text)
        if window_size is None or window_size <= 0:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Invalid FFT window size was specified. FFT window size should be a positive value.",
            )
            return
        elif window_size >= 32768:
            ret = QtWidgets.QMessageBox.warning(
                self._view,
                "Question",
                "Too large FFT window size was specified. Do you want to continue anyway?",
                QtWidgets.QMessageBox.StandardButton.Yes,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if ret != QtWidgets.QMessageBox.StandardButton.Yes:
                return

        stride_text = self._view._stride_line_edit.text()
        stride = str_to_int_or_none(stride_text)
        if stride is None or stride <= 0:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Invalid stride size was specified. Stride size should be a positive value.",
            )
            return
        elif stride >= window_size:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Invalid stride size was specified. Stride size should be equal to or less than FFT window size.",
            )
            return
        elif stride < 128:
            ret = QtWidgets.QMessageBox.warning(
                self._view,
                "Question",
                "Too small stride size was specified. Do you want to continue anyway?",
                QtWidgets.QMessageBox.StandardButton.Yes,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if ret != QtWidgets.QMessageBox.StandardButton.Yes:
                return

        n_average_text = self._view._n_average_line_edit.text()
        n_average = str_to_int_or_none(n_average_text)
        if n_average is None or n_average <= 0:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Invalid N_average was specified. N_average should be a positive value.",
            )
            return

        # To save result of calculation
        self.queue = Queue()
        # Setup worker thread with progress dialog for calculation
        worker = Worker(
            queue=self.queue,
            trange=trange,
            w=fft_window,
            nfft=window_size,
            stride=stride,
            n_average=n_average,
        )
        self._setup_worker(worker)
        self._setup_thread()
        self._setup_progress_manager(self._view)
        # Start calculation in worker thread
        # If calculation ended successfully, self.on_worker_succeeded succeeds this function
        # Note that self.on_worker_succeeded is done in GUI main thread because
        # plotting is related to GUI
        self._start_thread()

    def on_worker_succeeded(self) -> None:
        # Overwrite super method
        # We want to keep the progress dialog open while plotting to
        # prohibit user input
        self._progress_dialog.setLabelText("Plotting...")
        self._progress_dialog.setValue(0)
        # Get result from calculation
        try:
            result = self.queue.get(block=False)
        except Empty:
            result = None
        if result is None:
            return
        self._orbital_infos: Dict[OrbitalInfoName, str] = result[0]
        self._trange: Optional[Tuple[float, float]] = result[1]
        assert self._trange is not None
        # Setup mask manager
        self._mask_managers = MaskManagers(self._data_options)
        # Plot
        self._plot()

        # View
        self._view._start_line_edit.setText(
            time_string(round_down(self._trange[0], ndigits=3), fmt="%Y-%m-%d/%H:%M:%S.%f")[:-3]  # type: ignore
        )
        self._view._end_line_edit.setText(
            time_string(round_up(self._trange[1], ndigits=3), fmt="%Y-%m-%d/%H:%M:%S.%f")[:-3]  # type: ignore
        )
        self._update_mask_tab()
        for group in self._view._mask_tab._slider_groups.values():
            group._slider.setEnabled(True)
            group._line_edit.setEnabled(True)

        # Notice that since plotting must be done in the main GUI loop unlike
        # downloading or calculating, the progress bar will not update
        # while plotting.
        self._progress_dialog.setValue(100)
        self._progress_dialog.hide()

    def _plot(self):
        assert self._trange is not None

        self._support_lines_apply()
        self._orbital_info_apply()
        self._mask_apply()
        self._save_config()

        fig = self._view._canvas.figure
        fig = plot_wfc(
            fig=fig,
            trange=self._trange,
            orb_dict=self._orbital_infos,
            species=self._species,
            data_options=self._data_options,
            orbital_info_options=self._orbital_info_options,
            font_size=self._view_options.font_size,
        )
        self._view._canvas.draw()

        # This makes some GUIs operate on the plot effective
        self._has_plotted = True

    # Options tab
    def on_support_lines_apply_button_clicked(self) -> None:
        if not self._has_plotted:
            return
        self._plot()

    def _support_lines_apply(self) -> None:
        assert self._trange is not None

        # Fetch input
        opts = self._view._options_tab.support_lines_model._data
        species, m, q, lsty, lcol = [], [], [], [], []
        for opt in opts:
            if opt.enable_typed:
                species.append(opt.species_typed)
                m.append(opt.m_typed)
                q.append(opt.q_typed)
                lsty.append(opt.lsty_typed)
                lcol.append(opt.lcol_typed)

        # Presentation logic
        names = [name.value for name in DataName]
        actual_species = add_fc(
            names, species=species, m=m, q=q, lsty=lsty, lcol=lcol, trange=self._trange
        )
        self._species = actual_species

    def on_support_lines_add_button_clicked(self) -> None:
        options_tab = self._view._options_tab
        model = options_tab.support_lines_model
        row = model.rowCount()
        model.insertRow(row)

    def on_support_lines_delete_button_clicked(self) -> None:
        options_tab = self._view._options_tab
        model = options_tab.support_lines_model
        indexes = (
            options_tab._support_lines_table_view.selectionModel().selectedIndexes()
        )
        if len(indexes) == 0:
            return
        # Reduce rows when multiple cell with same row and different columns are selected
        rows = list(set([index.row() for index in indexes]))
        # Must remove from bottom to up so that index shift during iteration does not matter
        for row in sorted(rows, reverse=True):
            model.removeRow(row)

    def on_support_lines_reset_button_clicked(self) -> None:
        options_tab = self._view._options_tab
        model = options_tab.support_lines_model
        model.reset()

    def _orbital_info_apply(self) -> None:
        for name in OrbitalInfoName:
            is_checked = self._view._options_tab._orbital_info_boxes[name].isChecked()
            setattr(self._orbital_info_options, name.value, is_checked)

    def on_xyz_apply_button_clicked(self) -> None:
        if not self._has_plotted:
            return
        self._plot()

    def on_xyz_reset_button_clicked(self) -> None:
        # Data
        self._data_options = copy.deepcopy(self._data_options_bak)
        self._orbital_info_options = copy.deepcopy(self._orbital_info_options_bak)
        # View
        self._view._options_tab.update_xyzaxis_value(self._data_options)
        self._view._options_tab.update_orbital_info_boxes_value(
            self._orbital_info_options
        )
        # Update mask tab only if plot (and thus data) exists
        if not self._has_plotted:
            return
        self._mask_managers = MaskManagers(self._data_options)
        self._update_mask_tab()

    def on_yaxis_log_state_changed(self, state: int) -> None:
        if state == QtCore.Qt.CheckState.Checked.value:
            ylog = True
        elif state == QtCore.Qt.CheckState.Unchecked.value:
            ylog = False
        else:
            return
        for name in DataName:
            self._data_options[name].ylog = ylog
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    def on_yaxis_title_editing_finished(self) -> None:
        text = self._view._options_tab.yaxis_widgets.title.text()
        for name in DataName:
            self._data_options[name].ysubtitle = text
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    def on_yaxis_ymin_editing_finished(self) -> None:
        # When ylog is changed from False to True,
        # ylim <= 0 will change to small ylim > 0.
        # Then when ylog is changed from True to False,
        # it feels nicer for ylog to go back to <= 0 instead of small ylim > 0
        # if user does not explicitly edit ylim
        ymin_edit = float(self._view._options_tab.yaxis_widgets.ymin.text())
        for name in DataName:
            ymin = self._data_options[name].ymin
            # Since QLineEdit.editingFinished event will occur when
            # user does not change content but just move cursor in and out of line edit,
            # it seems better to consider that case "not edited".
            if ymin_edit == ymin:
                continue
            self._data_options[name].set_ymin(ymin_edit)
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    def on_yaxis_ymax_editing_finished(self) -> None:
        ymax_edit = float(self._view._options_tab.yaxis_widgets.ymax.text())
        for name in DataName:
            ymax = self._data_options[name].ymax
            if ymax_edit == ymax:
                continue
            self._data_options[name].set_ymax(ymax_edit)
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    def on_zaxis_zlog_state_changed(self, name: DataName, state: int) -> None:
        if state == QtCore.Qt.CheckState.Checked.value:
            zlog = True
        elif state == QtCore.Qt.CheckState.Unchecked.value:
            zlog = False
        else:
            raise ValueError(f"Check state is invalid: {state}")
        self._data_options[name].zlog = zlog
        self._view._options_tab.update_xyzaxis_value(self._data_options)
        self._update_slider_group_label(name)
        self._update_slider_group_slider(name)
        self._update_slider_group_line_edit(name)

    def on_zaxis_mask_state_changed(self, name: DataName, state: int) -> None:
        if state == QtCore.Qt.CheckState.Checked.value:
            mask = True
        elif state == QtCore.Qt.CheckState.Unchecked.value:
            mask = False
        else:
            raise ValueError(f"Check state is invalid: {state}")
        self._data_options[name].mask = mask
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    def on_zaxis_plot_state_changed(self, name: DataName, state: int) -> None:
        if state == QtCore.Qt.CheckState.Checked.value:
            plot = True
        elif state == QtCore.Qt.CheckState.Unchecked.value:
            plot = False
        else:
            raise ValueError(f"Check state is invalid: {state}")
        self._data_options[name].plot = plot
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    def on_zaxis_title_editing_finished(self, name: DataName) -> None:
        text = self._view._options_tab._zaxis_widgets[name].title.text()
        self._data_options[name].ytitle = text
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    def on_zaxis_zmin_editing_finished(self, name: DataName) -> None:
        zmin_edit = float(self._view._options_tab._zaxis_widgets[name].zmin.text())
        zmin = self._data_options[name].zmin
        if zmin_edit == zmin:
            return
        self._data_options[name].set_zmin(zmin_edit)
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    def on_zaxis_zmax_editing_finished(self, name: DataName) -> None:
        zmax_edit = float(self._view._options_tab._zaxis_widgets[name].zmax.text())
        zmax = self._data_options[name].zmax
        if zmax_edit == zmax:
            return
        self._data_options[name].set_zmax(zmax_edit)
        self._view._options_tab.update_xyzaxis_value(self._data_options)

    # Mask tab
    def _mask_apply(self):
        self._mask_managers.apply_mask()

    def on_mask_tab_apply_button_clicked(self) -> None:
        if not self._has_plotted:
            return
        self._plot()

    def on_mask_tab_reset_button_clicked(self) -> None:
        if not self._has_plotted:
            return
        self._mask_managers = MaskManagers(self._data_options)
        self._update_mask_tab()

    def _update_mask_tab(self) -> None:
        for name in DataName:
            self._update_slider_group_label(name)
            self._update_slider_group_slider(name)
            self._update_slider_group_line_edit(name)

    def _update_slider_group_label(self, name: DataName) -> None:
        opt = self._data_options[name]
        mask_label = opt.mask_label
        group = self._view._mask_tab._slider_groups[name]
        group._label.setText(mask_label)

    def _update_slider_group_slider(self, name: DataName) -> None:
        assert self._has_plotted
        info = self._mask_managers[name]

        # Convert data value to slider value
        imin = info.min_scaled
        imax = info.max_scaled
        imask = info.mask_scaled

        if info.log and info.ndigits == 0:
            smin = int(imin)
            smax = int(imax)
            slider_value = int(imask)
        else:
            smin = 0
            smax = 100
            slider_value = int((smax - smin) / (imax - imin) * (imask - imin) + smin)

        # Update view
        slider = self._view._mask_tab._slider_groups[name]._slider
        slider.blockSignals(True)
        slider.setMinimum(smin)
        slider.setMaximum(smax)
        slider.setValue(slider_value)
        slider.blockSignals(False)

    def _update_slider_group_line_edit(self, name: DataName) -> None:
        assert self._has_plotted
        info = self._mask_managers[name]

        # Convert data value to line edit value
        imask = info.mask_scaled
        ndigits = info.ndigits
        formatter = "{{:.{:}f}}".format(ndigits)
        text = formatter.format(imask)

        # Update view
        line_edit = self._view._mask_tab._slider_groups[name]._line_edit
        line_edit.blockSignals(True)
        line_edit.setText(text)
        line_edit.blockSignals(False)

    def on_mask_tab_slider_value_changed(
        self, name: DataName, slider_value: int
    ) -> None:
        info = self._mask_managers[name]

        # Convert slider value to data value
        if info.log and info.ndigits == 0:
            imask = slider_value
        else:
            smin = 0
            smax = 100
            imin = info.min_scaled
            imax = info.max_scaled
            imask = (imax - imin) / (smax - smin) * (slider_value - smin) + imin
        info.set_mask_scaled(imask)

        # Update view
        self._update_slider_group_slider(name)
        self._update_slider_group_line_edit(name)

    def on_mask_tab_line_edit_editing_finished(self, name: DataName) -> None:
        info = self._mask_managers[name]

        # Convert line edit value to data value
        group = self._view._mask_tab._slider_groups[name]
        text = group._line_edit.text()
        imask = float(text)
        info.set_mask_scaled(imask)

        # Update view
        self._update_slider_group_slider(name)
        self._update_slider_group_line_edit(name)

    # Output tab
    def on_output_tab_eps_button_clicked(self) -> None:
        # Validate state
        if not self._has_plotted:
            return

        trange = self._trange
        if trange is None:
            return

        # Validate input
        x_cm = self._view._output_tab._eps_width_line_edit.text()
        x_cm = str_to_float_or_none(x_cm)
        if x_cm is None or x_cm < 2:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Xsize must be larger than 2 cm.",
            )
            return
        y_cm = self._view._output_tab._eps_height_line_edit.text()
        y_cm = str_to_float_or_none(y_cm)
        if y_cm is None or y_cm < 3:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Ysize must be larger than 3 cm.",
            )
            return
        font_size = self._view._output_tab._eps_font_size_line_edit.text()
        font_size = str_to_float_or_none(font_size)
        if font_size is None or font_size <= 0:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Font size must be larger than 0.",
            )
            return

        start_time_str = time_string(round_down(trange[0], ndigits=3), fmt="%Y%m%d%H%M%S%f")[:-3]  # type: ignore
        end_time_str = time_string(round_up(trange[1], ndigits=3), fmt="%Y%m%d%H%M%S%f")[:-3]  # type: ignore
        file_name = "erg_pwe_wfc_" + start_time_str + "_" + end_time_str + ".eps"  # type: ignore
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self._view, dir=file_name, filter="*.eps"
        )
        if file_path == "":
            return

        cm_per_inch = 2.54
        x_inch = x_cm / cm_per_inch
        y_inch = y_cm / cm_per_inch
        dpi = 100
        x_px = x_inch * dpi
        y_px = y_inch * dpi

        fig = plot_init(x_px, y_px, dpi=dpi)
        fig = plot_wfc(
            fig=fig,
            trange=trange,
            orb_dict=self._orbital_infos,
            species=self._species,
            data_options=self._data_options,
            font_size=font_size,
            orbital_info_options=self._orbital_info_options,
            rasterized=True,
        )
        fig.savefig(file_path, dpi=dpi)

    def on_output_tab_png_button_clicked(self) -> None:
        # Validate state
        if not self._has_plotted:
            return

        trange = self._trange
        if trange is None:
            return

        # Validate input
        x_px = self._view._output_tab._png_width_line_edit.text()
        x_px = str_to_int_or_none(x_px)
        if x_px is None or x_px < 300:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Xsize must be larger than 300 px.",
            )
            return
        y_px = self._view._output_tab._png_height_line_edit.text()
        y_px = str_to_int_or_none(y_px)
        if y_px is None or y_px < 500:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Ysize must be larger than 500 px.",
            )
            return
        font_size = self._view._output_tab._png_font_size_line_edit.text()
        font_size = str_to_float_or_none(font_size)
        if font_size is None or font_size <= 0:
            QtWidgets.QMessageBox.warning(
                self._view,
                "Warning",
                "Font size must be larger than 0.",
            )
            return

        start_time_str = time_string(round_down(trange[0], ndigits=3), fmt="%Y%m%d%H%M%S%f")[:-3]  # type: ignore
        end_time_str = time_string(round_up(trange[1], ndigits=3), fmt="%Y%m%d%H%M%S%f")[:-3]  # type: ignore
        file_name = "erg_pwe_wfc_" + start_time_str + "_" + end_time_str + ".png"  # type: ignore
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self._view, dir=file_name, filter="*.png"
        )
        if file_path == "":
            return

        dpi = 100
        fig = plot_init(x_px, y_px, dpi=dpi)
        fig = plot_wfc(
            fig=fig,
            trange=trange,
            orb_dict=self._orbital_infos,
            species=self._species,
            data_options=self._data_options,
            font_size=font_size,
            orbital_info_options=self._orbital_info_options,
        )
        fig.savefig(file_path, dpi=dpi)

    def on_output_tab_tplot_button_clicked(self) -> None:
        if not self._has_plotted:
            return

        # Validate state
        trange = self._trange
        if trange is None:
            return
        data_names = [name.value for name in DataName]

        start_time_str = time_string(round_down(trange[0], ndigits=3), fmt="%Y%m%d%H%M%S%f")[:-3]  # type: ignore
        end_time_str = time_string(round_up(trange[1], ndigits=3), fmt="%Y%m%d%H%M%S%f")[:-3]  # type: ignore
        file_name = "erg_pwe_wfc_" + start_time_str + "_" + end_time_str + ".tplot"  # type: ignore
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self._view, dir=file_name, filter="*.tplot"
        )
        if file_path == "":
            return
        tplot_save(data_names, file_path)

    def _load_config(self) -> None:
        localdir = CONFIG["local_data_dir"]

        # Prefer user config if exists.
        path_user = os.path.join(localdir, "user_config.json")
        if os.path.exists(path_user):
            with open(path_user, "r") as f:
                json_data = json.load(f)
            support_line_options_dict_load = json_data.get("support_line_list")
            orbital_information_option_dict_load = json_data.get("orbital_information")
            if (
                support_line_options_dict_load is not None
                and orbital_information_option_dict_load is not None
            ):
                self._support_line_options = SupportLineOptions.from_list_of_dict(
                    support_line_options_dict_load
                )
                self._orbital_info_options = OrbitalInfoOption(
                    **orbital_information_option_dict_load
                )
                return

        # Else prefer default config if exists.
        path_default = os.path.join(localdir, "default_config.json")
        if os.path.exists(path_default):
            with open(path_default, "r") as f:
                json_data = json.load(f)
            support_line_options_dict_load = json_data.get("support_line_list")
            orbital_information_option_dict_load = json_data.get("orbital_information")
            if (
                support_line_options_dict_load is not None
                and orbital_information_option_dict_load is not None
            ):
                self._support_line_options = SupportLineOptions.from_list_of_dict(
                    support_line_options_dict_load
                )
                self._orbital_info_options = OrbitalInfoOption(
                    **orbital_information_option_dict_load
                )
                return

        # Else use config embedded in source and save as user and default configs.
        self._support_line_options = SupportLineOptions.from_list_of_dict()
        self._orbital_info_options = OrbitalInfoOption()
        for path in [path_user, path_default]:
            if os.path.exists(path):
                with open(path, "r") as f:
                    json_data = json.load(f)
            else:
                json_data = {}

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json_data[
                    "support_line_list"
                ] = self._support_line_options.to_list_of_dict()
                json_data["orbital_information"] = asdict(self._orbital_info_options)
                json.dump(json_data, f, indent=4)

        return

    def _save_config(self) -> None:
        # Save user config.
        localdir = CONFIG["local_data_dir"]

        path = os.path.join(localdir, "user_config.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                json_data = json.load(f)
        else:
            json_data = {}

        json_data["support_line_list"] = self._support_line_options.to_list_of_dict()
        json_data["orbital_information"] = asdict(self._orbital_info_options)
        with open(path, "w") as f:
            json.dump(json_data, f, indent=4)


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    vc = WFCViewController()
    vc.show()
    app.exec()
