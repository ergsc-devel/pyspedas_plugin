import copy
import json
import os
from functools import partial
from typing import List, Optional, Tuple

import numpy as np
from PySide6 import QtCore, QtWidgets
from pyspedas import time_double, time_string
from pyspedas.erg.satellite.erg.config import CONFIG
from pytplot import tplot_save

from ..load.add_fc import add_fc
from ..options.options import (
    DataName,
    OrbitalInfoName,
    SupportLineOptionName,
    create_data_options,
    create_orbital_informations,
    create_support_line_options,
    data_option_dict_dict,
    orbital_information_option_dict,
    support_line_option_list,
)
from ..utils.utils import safe_eval_formula, str_to_float_or_none, str_to_int_or_none
from .plot_wfc import _get_info, _mask, _update_info, load_wfc, plot_wfc, plot_wfc_init
from .wfc_view import WFCView, WFCViewOptions


class WFCViewController:
    def __init__(self, view_options: WFCViewOptions = WFCViewOptions()) -> None:
        # State
        self.view_options = view_options
        self.data_options = create_data_options(data_option_dict_dict)
        self._load_config()
        self.data_options_bak = copy.deepcopy(self.data_options)
        self.support_line_options_bak = copy.deepcopy(self.support_line_options)
        self.orbital_info_options_bak = copy.deepcopy(self.orbital_info_options)
        self.trange: Optional[Tuple[float, float]] = None
        self.species: Optional[List[str]] = None
        self._has_plotted = False
        self.ofa_view_controller = None

        # View
        self._view = WFCView(
            data_options=self.data_options,
            orbital_info_options=self.orbital_info_options,
            support_line_options=self.support_line_options,
            view_options=self.view_options,
        )
        for name, group in self._view._mask_tab._slider_groups.items():
            group._slider.setEnabled(False)
            group._line_edit.setEnabled(False)

        # Events
        # General
        self._view._tlimit_button.clicked.connect(self.on_tlimit_button_clicked)  # type: ignore
        self._view._fft_calc_button.clicked.connect(self.on_fft_calc_button_clicked)  # type: ignore
        self._view._fft_revert_button.clicked.connect(self.on_fft_revert_button_clicked)  # type: ignore
        # Options tab
        self._view._options_tab._support_lines_apply_button.clicked.connect(  # type: ignore
            self.on_options_tab_support_lines_apply_button_clicked
        )
        self._view._options_tab._support_lines_add_button.clicked.connect(  # type: ignore
            self.on_options_tab_support_lines_add_button_clicked
        )
        self._view._options_tab._support_lines_delete_button.clicked.connect(  # type: ignore
            self.on_options_tab_support_lines_delete_button_clicked
        )
        self._view._options_tab._support_lines_reset_button.clicked.connect(  # type: ignore
            self.on_options_tab_support_lines_reset_button_clicked
        )
        self._view._options_tab._xyzaxis_apply_button.clicked.connect(  # type: ignore
            self.options_tab_xyz_apply_button_clicked
        )
        self._view._options_tab._xyzaxis_reset_button.clicked.connect(  # type: ignore
            self.options_tab_xyz_reset_button_clicked
        )
        self._view._options_tab._yaxis_widgets.ylog.stateChanged.connect(  # type: ignore
            self.on_options_tab_ylog_checkbox_state_changed
        )
        for name, zaxis_widgets in self._view._options_tab._zaxis_widgets.items():
            widget = zaxis_widgets.zlog
            widget.stateChanged.connect(  # type: ignore
                partial(self.on_options_tab_zlog_checkbox_state_changed, name)
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
            self.mask_tab_apply_button_clicked
        )
        self._view._mask_tab._reset_button.clicked.connect(  # type: ignore
            self.mask_tab_reset_button_clicked
        )
        # Output tab
        self._view._output_tab._eps_button.clicked.connect(  # type: ignore
            self.output_tab_eps_button_clicked
        )
        self._view._output_tab._png_button.clicked.connect(  # type: ignore
            self.output_tab_png_button_clicked
        )
        self._view._output_tab._tplot_button.clicked.connect(  # type: ignore
            self.output_tab_tplot_button_clicked
        )

    def inject(self, ofa_view_controller) -> None:
        # TODO: type of ofa_view_controller is OFAViewController but cannot import due to circular import
        # You can avoid circular import by specifying protocol (interface)
        self.ofa_view_controller = ofa_view_controller

    def show(self) -> None:
        self._view.show()

    # GUI
    def on_tlimit_button_clicked(self) -> None:
        if (
            self.ofa_view_controller is None
            or not self.ofa_view_controller.can_use_wfc_tlimit()
        ):
            return
        # Disable any input in WFC
        self._view.setEnabled(False)
        # Bring OFA to front
        view = self.ofa_view_controller._view
        view.setWindowState(
            view.windowState() & ~QtCore.Qt.WindowState.WindowMinimized
            | QtCore.Qt.WindowState.WindowActive
        )
        view.activateWindow()
        # Presentation logic
        self.ofa_view_controller.on_wfc_tlimit_button_clicked()

    def on_tlimit_wfc_first_pressed(self, tlimit_start: float) -> None:
        self._view._start_line_edit.setText(
            time_string(tlimit_start, fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )

    def on_tlimit_wfc_second_pressed(self, trange: Tuple[float, float]) -> None:
        self._view._start_line_edit.setText(
            time_string(trange[0], fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )
        self._view._end_line_edit.setText(
            time_string(trange[1], fmt="%Y-%m-%d/%H:%M:%S")  # type: ignore
        )
        view = self._view
        view.setWindowState(
            view.windowState() & ~QtCore.Qt.WindowState.WindowMinimized
            | QtCore.Qt.WindowState.WindowActive
        )
        view.activateWindow()
        view.setEnabled(True)
        QtWidgets.QMessageBox.information(
            view,
            "Information",
            "New time interval has been set successfully.",
        )

    def _get_trange_from_line_edit_text(self) -> Optional[Tuple[float, float]]:
        # View controller
        # Input validation
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
            return
        if start_time >= end_time:
            QtWidgets.QMessageBox.warning(
                self._view, "Warning", "Invalid time interval was specified."
            )
            return

        return start_time, end_time  # type: ignore

    def on_fft_revert_button_clicked(self) -> None:
        self._view.setup_fft_options()

    def on_fft_calc_button_clicked(self) -> None:
        # TODO: Only for development
        no_update = os.getenv("WAVE_NO_UPDATE") == "True"

        # Validation
        trange = self._get_trange_from_line_edit_text()
        if trange is None:
            return

        fft_window_box = self._view._fft_window_box.currentText()

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

        # Presentation logic
        # TODO: maybe trange will be saved after completion of loading and plotting
        self.trange = trange

        ret = load_wfc(
            trange=self.trange,
            data_options=self.data_options,
            no_update=no_update,
        )
        if ret is None:
            return
        (
            self.tplot_names_for_plot,
            self.var_label_dict,
            self.data_infos,
            self.trange,
        ) = ret

        self._plot()

    def _plot(self):
        self._support_lines_apply()
        self._xyz_apply()
        self._save_config()

        if self.trange is None:
            return

        fig = self._view._canvas.figure
        fig = plot_wfc(
            fig=fig,
            trange=self.trange,
            tplot_names_for_plot=self.tplot_names_for_plot,
            var_label_dict=self.var_label_dict,
            species=self.species,
            data_options=self.data_options,
            font_size=self.view_options.font_size,
            orbital_info_options=self.orbital_info_options,
        )
        self._view._canvas.draw()

        self._update_mask_tab()
        self._has_plotted = True
        self._view._mask_tab
        # self._view._tabs.setTabEnabled(1, True)
        # self._view._tabs.setTabEnabled(2, True)
        for name, group in self._view._mask_tab._slider_groups.items():
            group._slider.setEnabled(True)
            group._line_edit.setEnabled(True)

    # Options tab
    def on_options_tab_support_lines_apply_button_clicked(self) -> None:
        if not self._has_plotted:
            return
        self._plot()

    def _support_lines_apply(self) -> None:
        if not self._has_plotted:
            return
        # View controller
        options_tab = self._view._options_tab
        model = options_tab._support_lines_model
        data = model._data
        species = []
        m = []
        q = []
        lsty = []
        lcol = []
        for row in data:
            if row[SupportLineOptionName.enable] == "ON":
                species.append(row[SupportLineOptionName.species])
                m.append(safe_eval_formula(row[SupportLineOptionName.m]))
                q.append(safe_eval_formula(row[SupportLineOptionName.q]))
                lsty.append(int(row[SupportLineOptionName.lsty]))
                lcol.append(int(row[SupportLineOptionName.lcol]))

        # Presentation logic
        # TODO: make it better
        names = [name.value for name in DataName]
        add_fc(
            names, species=species, m=m, q=q, lsty=lsty, lcol=lcol, trange=self.trange
        )
        self.species = species

    def on_options_tab_support_lines_add_button_clicked(self) -> None:
        options_tab = self._view._options_tab
        model = options_tab._support_lines_model
        row = model._row_count
        model.insertRow(row)

    def on_options_tab_support_lines_delete_button_clicked(self) -> None:
        options_tab = self._view._options_tab
        model = options_tab._support_lines_model
        indexes = (
            options_tab._support_lines_table_view.selectionModel().selectedIndexes()
        )
        if len(indexes) == 0:
            return
        rows = [index.row() for index in indexes]
        # Must remove from bottom to up so that index shift during iteration does not matter
        for row in sorted(rows, reverse=True):
            model.removeRow(row)

    def on_options_tab_support_lines_reset_button_clicked(self) -> None:
        options_tab = self._view._options_tab
        model = options_tab._support_lines_model
        model.reset()

    def _xyz_apply(self) -> None:
        for name in OrbitalInfoName:
            is_checked = self._view._options_tab._orbital_info_boxes[name].isChecked()
            self.orbital_info_options[name] = is_checked

        yaxis_widgets = self._view._options_tab._yaxis_widgets
        zaxis_widgets = self._view._options_tab._zaxis_widgets

        for name in DataName:
            self.data_options[name].ysubtitle = yaxis_widgets.title.text()
            self.data_options[name].ymin = float(yaxis_widgets.ymin.text())
            self.data_options[name].ymax = float(yaxis_widgets.ymax.text())
            self.data_options[name].ylog = yaxis_widgets.ylog.isChecked()
            self.data_options[name].ytitle = zaxis_widgets[name].title.text()
            self.data_options[name].zmin = float(zaxis_widgets[name].zmin.text())
            self.data_options[name].zmax = float(zaxis_widgets[name].zmax.text())
            self.data_options[name].zlog = zaxis_widgets[name].zlog.isChecked()
            self.data_options[name].mask = zaxis_widgets[name].mask.isChecked()
            self.data_options[name].plot = zaxis_widgets[name].plot.isChecked()

        _mask(self.data_options, self.data_infos)

    def options_tab_xyz_apply_button_clicked(self) -> None:
        if not self._has_plotted:
            return
        self._plot()

    def options_tab_xyz_reset_button_clicked(self) -> None:
        self.data_options = copy.deepcopy(self.data_options_bak)
        self.orbital_info_options = copy.deepcopy(self.orbital_info_options_bak)
        self._view._options_tab.setup_xyzaxis_value(self.data_options)
        self._view._options_tab.setup_orbital_info_boxes_value(
            self.orbital_info_options
        )

    def on_options_tab_ylog_checkbox_state_changed(self, state: int) -> None:
        if state == QtCore.Qt.CheckState.Checked.value:
            ylog = True
        elif state == QtCore.Qt.CheckState.Unchecked.value:
            ylog = False
        # QtCore.Qt.CheckState.PartiallyChecked does not occur in this case
        else:
            return
        for name in DataName:
            opt = self.data_options[name]
            opt.ylog = ylog
        self._view._options_tab.setup_xyzaxis_value(self.data_options)

    # Sync option tab zlog checkbox and mask tab sliders
    def on_options_tab_zlog_checkbox_state_changed(
        self, name: DataName, state: int
    ) -> None:
        if state == QtCore.Qt.CheckState.Checked.value:
            zlog = True
        elif state == QtCore.Qt.CheckState.Unchecked.value:
            zlog = False
        # QtCore.Qt.CheckState.PartiallyChecked does not occur in this case
        else:
            return
        opt = self.data_options[name]
        opt.zlog = zlog
        self._update_slider_group_label(name)
        self._view._options_tab.setup_xyzaxis_value(self.data_options)
        if not self._has_plotted:
            return
        _update_info(name, self.data_options, self.data_infos)
        self._update_slider_group_slider(name)
        self._update_slider_group_line_edit(name)

    # Mask tab
    def mask_tab_apply_button_clicked(self) -> None:
        if not self._has_plotted:
            return
        _mask(self.data_options, self.data_infos)
        self._plot()

    def mask_tab_reset_button_clicked(self) -> None:
        self.data_infos = _get_info(self.data_options)
        _mask(self.data_options, self.data_infos)
        self._update_mask_tab()

    def _update_mask_tab(self) -> None:
        for name in DataName:
            self._update_slider_group_label(name)
            self._update_slider_group_slider(name)
            self._update_slider_group_line_edit(name)

    def _update_slider_group_label(self, name: DataName) -> None:
        # Irrelevant to data
        opt = self.data_options[name]
        mask_label = opt.mask_label
        if opt.zlog:
            label = mask_label + " (Exponential):"
        else:
            label = mask_label + ":"
        group = self._view._mask_tab._slider_groups[name]
        group._label.setText(label)

    def _update_slider_group_slider(self, name: DataName) -> None:
        # Get value
        info = self.data_infos[name]
        real_value = info.mask

        # Conversion
        group = self._view._mask_tab._slider_groups[name]
        smin = group._slider.minimum()
        smax = group._slider.maximum()
        rmin = info.min
        rmax = info.max
        # TODO: is it ok to convert zlog everywhere, using same logic many times?
        opt = self.data_options[name]
        scaled_value = real_value
        if opt.zlog:
            # TOOD: temporarily machine epsilon
            if rmin <= 0:
                rmin = np.finfo(float).eps
            if rmax <= 0:
                rmax = np.finfo(float).eps
            if scaled_value <= 0:
                scaled_value = np.finfo(float).eps
            rmin = np.log10(rmin)
            rmax = np.log10(rmax)
            scaled_value = np.log10(scaled_value)

        slider_value = int((smax - smin) / (rmax - rmin) * (scaled_value - rmin) + smin)

        # Update
        slider = group._slider
        slider.blockSignals(True)
        slider.setValue(slider_value)
        slider.blockSignals(False)

    def _update_slider_group_line_edit(self, name: DataName) -> None:
        # Get value
        info = self.data_infos[name]
        real_value = info.mask

        # Conversion
        opt = self.data_options[name]
        if opt.zlog:
            if real_value <= 0:
                real_value = np.finfo(float).eps
            scaled_value = np.log10(real_value)
        else:
            scaled_value = real_value

        # Update
        line_edit = self._view._mask_tab._slider_groups[name]._line_edit
        line_edit.blockSignals(True)
        line_edit.setText(str(scaled_value))
        line_edit.blockSignals(False)

    def on_mask_tab_slider_value_changed(
        self, name: DataName, slider_value: int
    ) -> None:
        # Get value
        group = self._view._mask_tab._slider_groups[name]
        slider_value = group._slider.value()

        # Conversion
        smin = group._slider.minimum()
        smax = group._slider.maximum()
        info = self.data_infos[name]
        rmin = info.min
        rmax = info.max
        opt = self.data_options[name]
        if opt.zlog:
            # TOOD: temporarily machine epsilon
            if rmin <= 0:
                rmin = np.finfo(float).eps
            if rmax <= 0:
                rmax = np.finfo(float).eps
            rmin = np.log10(rmin)
            rmax = np.log10(rmax)
        scaled_value = (rmax - rmin) / (smax - smin) * (slider_value - smin) + rmin

        if opt.zlog:
            info.mask = 10**scaled_value
        else:
            info.mask = scaled_value

        # Update
        self._update_slider_group_line_edit(name)

    def on_mask_tab_line_edit_editing_finished(self, name: DataName) -> None:
        # Get value
        group = self._view._mask_tab._slider_groups[name]
        text = group._line_edit.text()
        scaled_value = float(text)

        # Conversion
        info = self.data_infos[name]
        opt = self.data_options[name]
        if opt.zlog:
            info.mask = 10**scaled_value
        else:
            info.mask = scaled_value

        # Update
        self._update_slider_group_slider(name)

    # Output tab
    def output_tab_eps_button_clicked(self) -> None:
        # Validate state
        if not self._has_plotted:
            return

        trange = self.trange
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

        start_time_str = time_string(trange[0], fmt="%Y%m%d%H%M%S")  # type: ignore
        end_time_str = time_string(trange[1], fmt="%Y%m%d%H%M%S")  # type: ignore
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

        fig = plot_wfc_init(x_px, y_px)
        fig = plot_wfc(
            fig=fig,
            trange=trange,
            tplot_names_for_plot=self.tplot_names_for_plot,
            var_label_dict=self.var_label_dict,
            species=self.species,
            data_options=self.data_options,
            font_size=font_size,
            orbital_info_options=self.orbital_info_options,
            rasterized=True,
        )
        fig.savefig(file_path + ".eps", dpi=dpi)

    def output_tab_png_button_clicked(self) -> None:
        # Validate state
        if not self._has_plotted:
            return

        trange = self.trange
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

        start_time_str = time_string(trange[0], fmt="%Y%m%d%H%M%S")  # type: ignore
        end_time_str = time_string(trange[1], fmt="%Y%m%d%H%M%S")  # type: ignore
        file_name = "erg_pwe_wfc_" + start_time_str + "_" + end_time_str + ".png"  # type: ignore
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self._view, dir=file_name, filter="*.png"
        )
        if file_path == "":
            return

        dpi = 100
        fig = plot_wfc_init(x_px, y_px)
        fig = plot_wfc(
            fig=fig,
            trange=trange,
            tplot_names_for_plot=self.tplot_names_for_plot,
            var_label_dict=self.var_label_dict,
            species=self.species,
            data_options=self.data_options,
            font_size=font_size,
            orbital_info_options=self.orbital_info_options,
        )
        fig.savefig(file_path, dpi=dpi)

    def output_tab_tplot_button_clicked(self) -> None:
        if not self._has_plotted:
            return

        # Validate state
        trange = self.trange
        if trange is None:
            return
        data_names = [name.value for name in DataName]

        start_time_str = time_string(trange[0], fmt="%Y%m%d%H%M%S")  # type: ignore
        end_time_str = time_string(trange[1], fmt="%Y%m%d%H%M%S")  # type: ignore
        file_name = "erg_pwe_wfc_" + start_time_str + "_" + end_time_str + ".tplot"  # type: ignore
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self._view, dir=file_name, filter="*.tplot"
        )
        if file_path == "":
            return
        tplot_save(data_names, file_path)

    def _load_config(self) -> None:
        # TODO: overwriting is better
        localdir = CONFIG["local_data_dir"]
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
                self.support_line_options = create_support_line_options(
                    support_line_options_dict_load
                )
                self.orbital_info_options = create_orbital_informations(
                    orbital_information_option_dict_load
                )
                return

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
                self.support_line_options = create_support_line_options(
                    support_line_options_dict_load
                )
                self.orbital_info_options = create_orbital_informations(
                    orbital_information_option_dict_load
                )
                return

        self.support_line_options = create_support_line_options(
            support_line_option_list
        )
        self.orbital_info_options = create_orbital_informations(
            orbital_information_option_dict
        )
        for path in [path_user, path_default]:
            if os.path.exists(path):
                with open(path, "r") as f:
                    json_data = json.load(f)
            else:
                json_data = {}

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                support_line_options = self.support_line_options
                support_line_options_list = []
                for line in support_line_options:
                    support_line_options_list.append(
                        {name.value: line[name] for name in SupportLineOptionName}
                    )
                json_data["support_line_list"] = support_line_options_list

                orbital_info_options = self.orbital_info_options
                orbital_info_options_dict = {
                    name.value: orbital_info_options[name] for name in OrbitalInfoName
                }
                json_data["orbital_information"] = orbital_info_options_dict
                json.dump(json_data, f, indent=4)

        return

    def _save_config(self) -> None:
        localdir = CONFIG["local_data_dir"]

        path = os.path.join(localdir, "user_config.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                json_data = json.load(f)
        else:
            json_data = {}

        support_line_options = self.support_line_options
        support_line_options_list = []
        for line in support_line_options:
            support_line_options_list.append(
                {name.value: line[name] for name in SupportLineOptionName}
            )
        json_data["support_line_list"] = support_line_options_list

        orbital_info_options = self.orbital_info_options
        orbital_info_options_dict = {
            name.value: orbital_info_options[name] for name in OrbitalInfoName
        }
        json_data["orbital_information"] = orbital_info_options_dict
        with open(path, "w") as f:
            json.dump(json_data, f, indent=4)


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    vc = WFCViewController()
    vc.show()
    app.exec()
