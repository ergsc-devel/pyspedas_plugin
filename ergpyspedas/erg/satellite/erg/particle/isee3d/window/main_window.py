import os
import sys
from datetime import datetime

import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui

from .ui_main_window import Ui_MainWindow
from ..vtk_widget.vtk_widget import VtkWidget
from ..colorbar.build_lookup_table import validate_colormap_name


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, dists, mag_vn, vel_vn, config, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self._message_timeout_msec = 10000

        self._save_image_dir = config['save_image_dir']
        self._check_save_image_dir()

        self._colormap_name = config['colormap_name']
        self._check_colormap_name()

        self.vtkWidget = VtkWidget(self.centralwidget, dists, mag_vn, vel_vn, self._colormap_name)
        self.vtkWidget.resize(768,768)
        self.verticalLayout_viewer.addWidget(self.vtkWidget)

        self._set_data_text()
        self._set_start_time_text()
        self._set_end_time_text()
        self._set_coordinates_text()
        self._set_value_text()

        self._set_on_off_panel_widgets()
        self._set_save_panel_widgets()
        self._set_data_change_panel_widgets(dists)
        self._set_2d_slice_tab_widgets()
        self._set_color_setting_tab_widgets()
        self._set_isosurface_tab_widgets()
        self._set_vectors_tab_widgets()
        self._set_view_tab_widgets()

        self.statusBar.showMessage('Initialized', timeout=self._message_timeout_msec)
    
    def _check_save_image_dir(self):
        if not os.path.isdir(self._save_image_dir):
            current_dir = os.path.abspath(os.curdir)
            msgBox = QtWidgets.QMessageBox()
            message = f'Save image directory "{self._save_image_dir}" not found.\n'
            message += f'Save image to "{current_dir}".'
            msgBox.setText(message)
            msgBox.setWindowTitle('ISEE_3D')
            msgBox.exec()
            self._save_image_dir = current_dir
    
    def _check_colormap_name(self):
        if not validate_colormap_name(self._colormap_name):
            msgBox = QtWidgets.QMessageBox()
            message = f'Colormap name "{self._colormap_name}" is not available.\n'
            message += f'Use colormap "jet".'
            msgBox.setText(message)
            msgBox.setWindowTitle('ISEE_3D')
            msgBox.exec()
            self._colormap_name = 'jet'

    def _set_data_text(self):
        first_datetime = datetime.strptime(self.vtkWidget.first_data_time, '%Y-%m-%d %H:%M:%S.%f')
        first_date_txt = first_datetime.strftime('%Y-%m-%d')
        first_time_txt = first_datetime.strftime('%H:%M:%S') + f'.{round(first_datetime.microsecond/1000)}'
        self.label_firstTime_slider.setText(first_time_txt)

        last_datetime = datetime.strptime(self.vtkWidget.last_data_time, '%Y-%m-%d %H:%M:%S.%f')
        last_date_txt = last_datetime.strftime('%Y-%m-%d')
        last_time_txt = last_datetime.strftime('%H:%M:%S') + f'.{round(last_datetime.microsecond/1000)}'
        self.label_lastTime_slider.setText(last_time_txt)

        axis_units_txt = self.vtkWidget.draw_property.data.axis_units

        self.label_data.setText(f'{first_date_txt}/{first_time_txt} - {last_date_txt}/{last_time_txt} ({axis_units_txt})')
    
    def _set_start_time_text(self):
        start_datetime = datetime.strptime(self.vtkWidget.draw_data.start_data_time, '%Y-%m-%d %H:%M:%S.%f')
        start_date_txt = start_datetime.strftime('%Y-%m-%d')
        start_time_txt = start_datetime.strftime('%H:%M:%S') + f'.{round(start_datetime.microsecond/1000)}'
        self.label_startTime.setText(f'{start_date_txt} {start_time_txt}')

    def _set_end_time_text(self):
        if self.vtkWidget.draw_data.end_data_time is None:
            self.label_endTime.setText(f'')
        else:
            end_datetime = datetime.strptime(self.vtkWidget.draw_data.end_data_time, '%Y-%m-%d %H:%M:%S.%f')
            end_date_txt = end_datetime.strftime('%Y-%m-%d')
            end_time_txt = end_datetime.strftime('%H:%M:%S') + f'.{round(end_datetime.microsecond/1000)}'
            self.label_endTime.setText(f'{end_date_txt} {end_time_txt}')

    def _set_coordinates_text(self):
        outline = self.vtkWidget.draw_property.outline

        self.label_xy_minValue.setText(f'{outline.x_min:.1e}')
        self.label_xy_maxValue.setText(f'{outline.x_max:.1e}')

        self.label_yz_minValue.setText(f'{outline.y_min:.1e}')
        self.label_yz_maxValue.setText(f'{outline.y_max:.1e}')

        self.label_xz_minValue.setText(f'{outline.z_min:.1e}')
        self.label_xz_maxValue.setText(f'{outline.z_max:.1e}')

    def _set_value_text(self):
        draw_data = self.vtkWidget.draw_data

        value_min = draw_data.value.min()
        self.label_isosurface1_minValue.setText(f'{value_min:.1e}')
        self.label_isosurface2_minValue.setText(f'{value_min:.1e}')

        value_max = draw_data.value.max()
        self.label_isosurface1_maxValue.setText(f'{value_max:.1e}')
        self.label_isosurface2_maxValue.setText(f'{value_max:.1e}')

    # -------------------------------------------------------------------
    # PANEL FOR OBJECT ON/OFF
    # -------------------------------------------------------------------
    def _set_on_off_panel_widgets(self):
        self.checkBox_isosurface1.setChecked(self.vtkWidget.draw_property.isosurface1.show)
        self.checkBox_isosurface2.setChecked(self.vtkWidget.draw_property.isosurface2.show)

    def change_show_isosurface1(self):
        is_checked = self.checkBox_isosurface1.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.isosurface1.show = True
        else:
            self.vtkWidget.draw_property.isosurface1.show = False
        self.vtkWidget.update_draw()

    def change_show_isosurface2(self):
        is_checked = self.checkBox_isosurface2.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.isosurface2.show = True
        else:
            self.vtkWidget.draw_property.isosurface2.show = False
        self.vtkWidget.update_draw()

    # -------------------------------------------------------------------
    # PANEL FOR "SAVE"
    # -------------------------------------------------------------------
    def _set_save_panel_widgets(self):
        self.comboBox_coordinates.setCurrentText(self.vtkWidget.draw_property.data.coordinates)
        self.comboBox_axisUnits.setCurrentText(self.vtkWidget.draw_property.data.axis_units)
        self.comboBox_units.setCurrentText(self.vtkWidget.draw_property.data.units)

    def click_save_button(self):
        save_dir = os.path.abspath(self._save_image_dir)
        if not os.path.isdir(save_dir):
            current_dir = os.path.abspath(os.curdir)
            msgBox = QtWidgets.QMessageBox()
            message = f'Save image directory "{save_dir}" not found.\n'
            message += f'Save image to "{current_dir}".'
            msgBox.setText(message)
            msgBox.setWindowTitle('ISEE_3D')
            msgBox.exec()
            save_dir = current_dir

        current_time_txt = datetime.now().strftime('%Y%m%d%H%M%S')
        if self.comboBox_saveType.currentText() == 'PNG':
            save_fn = f'isee3d_screen_{current_time_txt}.png'
            save_path = os.path.join(save_dir, save_fn)
            self.statusBar.showMessage(f'Save PNG Image: {save_path}', timeout=self._message_timeout_msec)
            self.vtkWidget.save_png_image(save_path)
        elif self.comboBox_saveType.currentText() == 'EPS':
            save_fn = f'isee3d_screen_{current_time_txt}.eps'
            save_path = os.path.join(save_dir, save_fn)
            self.statusBar.showMessage(f'Save EPS Image: {save_path}', timeout=self._message_timeout_msec)
            self.vtkWidget.save_eps_image(save_path)

    # -------------------------------------------------------------------
    # PANEL FOR DATA CHANGE
    # -------------------------------------------------------------------
    def _set_data_change_panel_widgets(self, dists):
        self.horizontalSlider_dataStartTime.setTracking(False)
        self.horizontalSlider_dataStartTime.setMinimum(0)
        self.horizontalSlider_dataStartTime.setMaximum(len(dists['time'])-1)

    def change_coordinates(self):
        current_text = self.comboBox_coordinates.currentText()
        self.vtkWidget.draw_property.data.coordinates = current_text
        self.vtkWidget.update_data()
        self.vtkWidget.update_draw()

    def change_axisUnits(self):
        current_text = self.comboBox_axisUnits.currentText()
        self.vtkWidget.draw_property.data.axis_units = current_text
        self.vtkWidget.draw_property.outline.axis_units = current_text
        self.vtkWidget.update_data()
        self.vtkWidget.update_draw()
        self._set_data_text()
        self._set_coordinates_text()

    def change_units(self):
        current_text = self.comboBox_units.currentText()
        self.vtkWidget.draw_property.data.units = current_text
        self.vtkWidget.draw_property.colorbar.units = current_text
        self.vtkWidget.update_data()
        self.vtkWidget.update_draw()
        self._set_value_text()

    def change_data(self):
        value = self.horizontalSlider_dataStartTime.value()
        self.vtkWidget.draw_property.data.show_data_index = value

        try:
            edit_min = float(self.lineEdit_color_minValue.text())
            edit_max = float(self.lineEdit_color_maxValue.text())
            colorbar_min = self.vtkWidget.draw_property.colorbar.min
            colorbar_max = self.vtkWidget.draw_property.colorbar.max
            if (edit_min != colorbar_min) or (edit_max != colorbar_max):
                self.vtkWidget.draw_property.colorbar.reset()
        except:
            self.vtkWidget.draw_property.colorbar.reset()

        self.vtkWidget.update_data()
        self.vtkWidget.update_draw()
        self._set_start_time_text()
        self._set_end_time_text()
        self._set_value_text()
        self.lineEdit_xyPlane.validator().setRange(self.vtkWidget.draw_property.outline.z_min, self.vtkWidget.draw_property.outline.z_max)
        self.lineEdit_yzPlane.validator().setRange(self.vtkWidget.draw_property.outline.x_min, self.vtkWidget.draw_property.outline.x_max)
        self.lineEdit_xzPlane.validator().setRange(self.vtkWidget.draw_property.outline.y_min, self.vtkWidget.draw_property.outline.y_max)

    # -------------------------------------------------------------------
    # TAB FOR 2D SLICE
    # -------------------------------------------------------------------
    def _set_2d_slice_tab_widgets(self):
        self.checkBox_xy_contour.setChecked(self.vtkWidget.draw_property.xy_plane.show_contour)
        self.checkBox_xy_image.setChecked(self.vtkWidget.draw_property.xy_plane.show_image)
        self._xyPlane_slider_value = None
        self.horizontalSlider_xy.setTracking(False)
        dim = self.vtkWidget.draw_data.image_data.GetDimensions()[2]
        slider_value = 0
        self.horizontalSlider_xy.setValue(slider_value)
        self.horizontalSlider_xy.setMinimum(0)
        self.horizontalSlider_xy.setMaximum(dim - 1)
        axis_value = self._plane_slider_value_to_axis_value(slider_value, axis='z_axis')
        self.lineEdit_xyPlane.setText(f'{axis_value:.3e}')
        self.lineEdit_xyPlane.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_xyPlane.validator().setRange(self.vtkWidget.draw_property.outline.z_min, self.vtkWidget.draw_property.outline.z_max)

        self.checkBox_yz_contour.setChecked(self.vtkWidget.draw_property.yz_plane.show_contour)
        self.checkBox_yz_image.setChecked(self.vtkWidget.draw_property.yz_plane.show_image)
        self._yzPlane_slider_value = None
        self.horizontalSlider_yz.setTracking(False)
        dim = self.vtkWidget.draw_data.image_data.GetDimensions()[0]
        slider_value = 0
        self.horizontalSlider_yz.setValue(slider_value)
        self.horizontalSlider_yz.setMinimum(0)
        self.horizontalSlider_yz.setMaximum(dim - 1)
        axis_value = self._plane_slider_value_to_axis_value(slider_value, axis='x_axis')
        self.lineEdit_yzPlane.setText(f'{axis_value:.3e}')
        self.lineEdit_yzPlane.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_yzPlane.validator().setRange(self.vtkWidget.draw_property.outline.x_min, self.vtkWidget.draw_property.outline.x_max)

        self.checkBox_xz_contour.setChecked(self.vtkWidget.draw_property.xz_plane.show_contour)
        self.checkBox_xz_image.setChecked(self.vtkWidget.draw_property.xz_plane.show_image)
        self._xzPlane_slider_value = None
        self.horizontalSlider_xz.setTracking(False)
        dim = self.vtkWidget.draw_data.image_data.GetDimensions()[1]
        slider_value = 0
        self.horizontalSlider_xz.setValue(slider_value)
        self.horizontalSlider_xz.setMinimum(0)
        self.horizontalSlider_xz.setMaximum(dim - 1)
        axis_value = self._plane_slider_value_to_axis_value(slider_value, axis='y_axis')
        self.lineEdit_xzPlane.setText(f'{axis_value:.3e}')
        self.lineEdit_xzPlane.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_xzPlane.validator().setRange(self.vtkWidget.draw_property.outline.y_min, self.vtkWidget.draw_property.outline.y_max)

    def change_show_xyPlane_contour(self):
        is_checked = self.checkBox_xy_contour.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.xy_plane.show_contour = True
        else:
            self.vtkWidget.draw_property.xy_plane.show_contour = False
        self.vtkWidget.update_draw()

    def change_show_xyPlane_image(self):
        is_checked = self.checkBox_xy_image.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.xy_plane.show_image = True
        else:
            self.vtkWidget.draw_property.xy_plane.show_image = False
        self.vtkWidget.update_draw()

    def change_show_yzPlane_contour(self):
        is_checked = self.checkBox_yz_contour.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.yz_plane.show_contour = True
        else:
            self.vtkWidget.draw_property.yz_plane.show_contour = False
        self.vtkWidget.update_draw()

    def change_show_yzPlane_image(self):
        is_checked = self.checkBox_yz_image.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.yz_plane.show_image = True
        else:
            self.vtkWidget.draw_property.yz_plane.show_image = False
        self.vtkWidget.update_draw()

    def change_show_xzPlane_contour(self):
        is_checked = self.checkBox_xz_contour.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.xz_plane.show_contour = True
        else:
            self.vtkWidget.draw_property.xz_plane.show_contour = False
        self.vtkWidget.update_draw()

    def change_show_xzPlane_image(self):
        is_checked = self.checkBox_xz_image.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.xz_plane.show_image = True
        else:
            self.vtkWidget.draw_property.xz_plane.show_image = False
        self.vtkWidget.update_draw()

    def change_xyPlane_value_slider(self):
        slider_value = self.horizontalSlider_xy.value()
        if slider_value == self._xyPlane_slider_value:
            return

        axis_value = self._plane_slider_value_to_axis_value(slider_value, axis='z_axis')
        self.vtkWidget.draw_property.xy_plane.cut_value = axis_value
        self.vtkWidget.update_draw()

        self._xyPlane_slider_value = slider_value
        self.lineEdit_xyPlane.setText(f'{axis_value:.3e}')

    def edit_xyPlane_value_text(self):
        axis_value = self.lineEdit_xyPlane.text()
        axis_value = float(axis_value)
        slider_value = self._plane_axis_value_to_slider_value(axis_value, axis='z_axis')

        if slider_value == self._xyPlane_slider_value:
            return

        self.vtkWidget.draw_property.xy_plane.cut_value = axis_value
        self.vtkWidget.update_draw()

        self._xyPlane_slider_value = slider_value
        self.horizontalSlider_xy.setValue(slider_value)

    def change_yzPlane_value_slider(self):
        slider_value = self.horizontalSlider_yz.value()
        if slider_value == self._yzPlane_slider_value:
            return

        axis_value = self._plane_slider_value_to_axis_value(slider_value, axis='x_axis')
        self.vtkWidget.draw_property.yz_plane.cut_value = axis_value
        self.vtkWidget.update_draw()

        self._yzPlane_slider_value = slider_value
        self.lineEdit_yzPlane.setText(f'{axis_value:.3e}')

    def edit_yzPlane_value_text(self):
        axis_value = self.lineEdit_yzPlane.text()
        axis_value = float(axis_value)
        slider_value = self._plane_axis_value_to_slider_value(axis_value, axis='x_axis')

        if slider_value == self._yzPlane_slider_value:
            return

        self.vtkWidget.draw_property.yz_plane.cut_value = axis_value
        self.vtkWidget.update_draw()

        self._yzPlane_slider_value = slider_value
        self.horizontalSlider_yz.setValue(slider_value)

    def change_xzPlane_value_slider(self):
        slider_value = self.horizontalSlider_xz.value()
        if slider_value == self._xzPlane_slider_value:
            return

        axis_value = self._plane_slider_value_to_axis_value(slider_value, axis='y_axis')
        self.vtkWidget.draw_property.xz_plane.cut_value = axis_value
        self.vtkWidget.update_draw()

        self._xzPlane_slider_value = slider_value
        self.lineEdit_xzPlane.setText(f'{axis_value:.3e}')

    def edit_xzPlane_value_text(self):
        axis_value = self.lineEdit_xzPlane.text()
        axis_value = float(axis_value)
        slider_value = self._plane_axis_value_to_slider_value(axis_value, axis='y_axis')

        if slider_value == self._xzPlane_slider_value:
            return

        self.vtkWidget.draw_property.xz_plane.cut_value = axis_value
        self.vtkWidget.update_draw()

        self._xzPlane_slider_value = slider_value
        self.horizontalSlider_xz.setValue(slider_value)

    def _plane_slider_value_to_axis_value(self, slider_value, axis, eps=1e-10):
        image_data = self.vtkWidget.draw_data.image_data
        scale = self.vtkWidget.draw_data.scale
        if axis == 'x_axis':
            index = 0
        elif axis == 'y_axis':
            index = 1
        elif axis == 'z_axis':
            index = 2

        origin = image_data.GetOrigin()[index]
        step = image_data.GetSpacing()[index]

        axis_value = (origin + step * slider_value) * scale
        if slider_value == 0:
            # Minimum value is not displayed in slice, so make it slightly larger than the minimum value.
            axis_value = axis_value + abs(axis_value) * eps
        return axis_value

    def _plane_axis_value_to_slider_value(self, axis_value, axis):
        image_data = self.vtkWidget.draw_data.image_data
        scale = self.vtkWidget.draw_data.scale
        if axis == 'x_axis':
            index = 0
        elif axis == 'y_axis':
            index = 1
        elif axis == 'z_axis':
            index = 2

        scaled = axis_value / scale
        origin = image_data.GetOrigin()[index]
        step = image_data.GetSpacing()[index]
        dim = image_data.GetDimensions()[index]
        
        for i in range(dim - 1):
            low = origin + step * i
            high = origin + step * (i+1)

            if high < scaled:
                continue

            if abs(low - scaled) < abs(high - scaled):
                return i
            else:
                return i + 1

    # -------------------------------------------------------------------
    # TAB FOR COLOR SETTING
    # -------------------------------------------------------------------
    def _set_color_setting_tab_widgets(self):
        self.lineEdit_color_minValue.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_color_maxValue.setValidator(QtGui.QDoubleValidator())

    def edit_color_values(self):
        try:
            min_value = float(self.lineEdit_color_minValue.text())
            max_value = float(self.lineEdit_color_maxValue.text())
            if min_value >= max_value:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setText('"Max Value" must be greater than "Min Value".')
                msgBox.setWindowTitle('ISEE_3D')
                msgBox.exec()
                return
        except:
            min_value = self.vtkWidget.draw_data.value.min()
            max_value = self.vtkWidget.draw_data.value.max()
        
        self.vtkWidget.draw_property.colorbar.min = min_value
        self.vtkWidget.draw_property.colorbar.max = max_value
        self.vtkWidget.update_draw()
    
    def color_reset(self):
        min_value = self.vtkWidget.draw_data.value.min()
        max_value = self.vtkWidget.draw_data.value.max()
        
        self.vtkWidget.draw_property.colorbar.min = min_value
        self.vtkWidget.draw_property.colorbar.max = max_value
        self.vtkWidget.update_draw()

    # -------------------------------------------------------------------
    # TAB FOR ISOSURFACE
    # -------------------------------------------------------------------
    def _set_isosurface_tab_widgets(self):
        self._value_divide_num = 100

        self.comboBox_isosurface1_color.setCurrentText(self.vtkWidget.draw_property.isosurface1.color)
        self.checkBox_isosurface1_mesh.setChecked(self.vtkWidget.draw_property.isosurface1.mesh)
        self._isosurface1_slider_value = None
        slider_value = 0
        self.horizontalSlider_isosurface1.setValue(slider_value)
        self.horizontalSlider_isosurface1.setTracking(False)
        self.horizontalSlider_isosurface1.setMinimum(0)
        self.horizontalSlider_isosurface1.setMaximum(self._value_divide_num)
        isosurface_value = self._slider_value_to_isosurface_value(slider_value)
        self.lineEdit_isosurface1.setText(f'{isosurface_value:.3e}')
        self.lineEdit_isosurface1.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_isosurface1.validator().setRange(self.vtkWidget.draw_data.value.min(), self.vtkWidget.draw_data.value.max())

        self.comboBox_isosurface2_color.setCurrentText(self.vtkWidget.draw_property.isosurface2.color)
        self.checkBox_isosurface2_mesh.setChecked(self.vtkWidget.draw_property.isosurface2.mesh)
        self._isosurface2_slider_value = None
        slider_value = 0
        self.horizontalSlider_isosurface2.setValue(slider_value)
        self.horizontalSlider_isosurface2.setTracking(False)
        self.horizontalSlider_isosurface2.setMinimum(0)
        self.horizontalSlider_isosurface2.setMaximum(self._value_divide_num)
        isosurface_value = self._slider_value_to_isosurface_value(slider_value)
        self.lineEdit_isosurface2.setText(f'{isosurface_value:.3e}')
        self.lineEdit_isosurface2.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_isosurface2.validator().setRange(self.vtkWidget.draw_data.value.min(), self.vtkWidget.draw_data.value.max())

    def change_isosurface1_mesh(self):
        is_checked = self.checkBox_isosurface1_mesh.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.isosurface1.mesh = True
        else:
            self.vtkWidget.draw_property.isosurface1.mesh = False
        self.vtkWidget.update_draw()

    def change_isosurface1_color(self):
        color = self.comboBox_isosurface1_color.currentText()
        self.vtkWidget.draw_property.isosurface1.color = color
        self.vtkWidget.update_draw()

    def change_isosurface1_value_text(self):
        isosurface_value = self.lineEdit_isosurface1.text()
        isosurface_value = float(isosurface_value)
        slider_value = self._isosurface_value_to_slider_value(isosurface_value)

        if slider_value == self._isosurface1_slider_value:
            return

        self.vtkWidget.draw_property.isosurface1.value = isosurface_value
        self.vtkWidget.update_draw()

        self._isosurface1_slider_value = slider_value
        self.horizontalSlider_isosurface1.setValue(slider_value)

    def change_isosurface1_value_slider(self):
        slider_value = self.horizontalSlider_isosurface1.value()
        if slider_value == self._isosurface1_slider_value:
            return

        isosurface_value = self._slider_value_to_isosurface_value(slider_value)
        self.vtkWidget.draw_property.isosurface1.value = isosurface_value
        self.vtkWidget.update_draw()

        self._isosurface1_slider_value = slider_value
        self.lineEdit_isosurface1.setText(f'{isosurface_value:.3e}')


    def change_isosurface2_mesh(self):
        is_checked = self.checkBox_isosurface2_mesh.isChecked()
        if is_checked:
            self.vtkWidget.draw_property.isosurface2.mesh = True
        else:
            self.vtkWidget.draw_property.isosurface2.mesh = False
        self.vtkWidget.update_draw()

    def change_isosurface2_color(self):
        color = self.comboBox_isosurface2_color.currentText()
        self.vtkWidget.draw_property.isosurface2.color = color
        self.vtkWidget.update_draw()

    def change_isosurface2_value_text(self):
        isosurface_value = self.lineEdit_isosurface2.text()
        isosurface_value = float(isosurface_value)
        slider_value = self._isosurface_value_to_slider_value(isosurface_value)

        if slider_value == self._isosurface2_slider_value:
            return

        self.vtkWidget.draw_property.isosurface2.value = isosurface_value
        self.vtkWidget.update_draw()

        self._isosurface2_slider_value = slider_value
        self.horizontalSlider_isosurface2.setValue(slider_value)

    def change_isosurface2_value_slider(self):
        slider_value = self.horizontalSlider_isosurface2.value()
        if slider_value == self._isosurface2_slider_value:
            return

        isosurface_value = self._slider_value_to_isosurface_value(slider_value)
        self.vtkWidget.draw_property.isosurface2.value = isosurface_value
        self.vtkWidget.update_draw()

        self._isosurface2_slider_value = slider_value
        self.lineEdit_isosurface2.setText(f'{isosurface_value:.3e}')

    def _slider_value_to_isosurface_value(self, slider_value):
        log_min_value = np.log10(self.vtkWidget.draw_data.value.min())
        log_max_value = np.log10(self.vtkWidget.draw_data.value.max())
        step = (log_max_value - log_min_value) / self._value_divide_num

        log_isosurface_value = log_min_value + step * slider_value
        isosurface_value = np.power(10, log_isosurface_value)
        return isosurface_value

    def _isosurface_value_to_slider_value(self, isosurface_value):
        log_isosurface_value = np.log10(isosurface_value)
        log_min_value = np.log10(self.vtkWidget.draw_data.value.min())
        log_max_value = np.log10(self.vtkWidget.draw_data.value.max())
        step = (log_max_value - log_min_value) / self._value_divide_num
        max_slider_value = self.horizontalSlider_isosurface1.maximum()
        for i in range(max_slider_value):
            low = log_min_value + step * i
            high = log_min_value + step * (i+1)

            if high < log_isosurface_value:
                continue

            if abs(low - log_isosurface_value) < abs(high - log_isosurface_value):
                return i
            else:
                return i + 1
        
    # -------------------------------------------------------------------
    # TAB FOR VECTORS
    # -------------------------------------------------------------------
    def _set_vectors_tab_widgets(self):
        self.checkBox_vector_mag.setChecked(self.vtkWidget.draw_property.mag_vec.show)
        self.comboBox_vector_mag_color.setCurrentText(self.vtkWidget.draw_property.mag_vec.color)
        self.comboBox_vector_mag_scale.setCurrentText(self.vtkWidget.draw_property.mag_vec.length_scale)
        self.comboBox_vector_mag_thick.setCurrentText(str(self.vtkWidget.draw_property.mag_vec.thick))

        self.checkBox_vector_vel.setChecked(self.vtkWidget.draw_property.vel_vec.show)
        self.comboBox_vector_vel_color.setCurrentText(self.vtkWidget.draw_property.vel_vec.color)
        self.comboBox_vector_vel_scale.setCurrentText(self.vtkWidget.draw_property.vel_vec.length_scale)
        self.comboBox_vector_vel_thick.setCurrentText(str(self.vtkWidget.draw_property.vel_vec.thick))

        self.checkBox_vector_user.setChecked(self.vtkWidget.draw_property.user_vec.show)
        self.comboBox_vector_user_color.setCurrentText(self.vtkWidget.draw_property.user_vec.color)
        self.comboBox_vector_user_scale.setCurrentText(self.vtkWidget.draw_property.user_vec.length_scale)
        self.comboBox_vector_user_thick.setCurrentText(str(self.vtkWidget.draw_property.user_vec.thick))
        self.lineEdit_vector_user_x.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_vector_user_y.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_vector_user_z.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_vector_user_x.setText(str(self.vtkWidget.draw_property.user_vec.vector[0]))
        self.lineEdit_vector_user_y.setText(str(self.vtkWidget.draw_property.user_vec.vector[1]))
        self.lineEdit_vector_user_z.setText(str(self.vtkWidget.draw_property.user_vec.vector[2]))

    def change_show_vector_mag(self):
        is_checked = self.checkBox_vector_mag.isChecked()
        self.vtkWidget.draw_property.mag_vec.show = is_checked
        self.vtkWidget.update_draw()
    
    def change_vector_mag_color(self):
        color = self.comboBox_vector_mag_color.currentText()
        self.vtkWidget.draw_property.mag_vec.color = color
        self.vtkWidget.update_draw()
    
    def change_vector_mag_scale(self):
        scale = self.comboBox_vector_mag_scale.currentText()
        self.vtkWidget.draw_property.mag_vec.length_scale = scale
        self.vtkWidget.update_draw()
    
    def change_vector_mag_thick(self):
        thick = int(self.comboBox_vector_mag_thick.currentText())
        self.vtkWidget.draw_property.mag_vec.thick = thick
        self.vtkWidget.update_draw()


    def change_show_vector_vel(self):
        is_checked = self.checkBox_vector_vel.isChecked()
        self.vtkWidget.draw_property.vel_vec.show = is_checked
        self.vtkWidget.update_draw()
    
    def change_vector_vel_color(self):
        color = self.comboBox_vector_vel_color.currentText()
        self.vtkWidget.draw_property.vel_vec.color = color
        self.vtkWidget.update_draw()
    
    def change_vector_vel_scale(self):
        scale = self.comboBox_vector_vel_scale.currentText()
        self.vtkWidget.draw_property.vel_vec.length_scale = scale
        self.vtkWidget.update_draw()
    
    def change_vector_vel_thick(self):
        thick = int(self.comboBox_vector_vel_thick.currentText())
        self.vtkWidget.draw_property.vel_vec.thick = thick
        self.vtkWidget.update_draw()

    def change_show_vector_user(self):
        is_checked = self.checkBox_vector_user.isChecked()
        self.vtkWidget.draw_property.user_vec.show = is_checked
        self._update_vector()
    
    def change_vector_user_color(self):
        color = self.comboBox_vector_user_color.currentText()
        self.vtkWidget.draw_property.user_vec.color = color
        self._update_vector()
    
    def change_vector_user_scale(self):
        scale = self.comboBox_vector_user_scale.currentText()
        self.vtkWidget.draw_property.user_vec.length_scale = scale
        self._update_vector()
    
    def change_vector_user_thick(self):
        thick = int(self.comboBox_vector_user_thick.currentText())
        self.vtkWidget.draw_property.user_vec.thick = thick
        self._update_vector()
    
    def change_vector_user_elems(self):
        self._update_vector()
    
    def _update_vector(self):
        try:
            x = float(self.lineEdit_vector_user_x.text())
            y = float(self.lineEdit_vector_user_y.text())
            z = float(self.lineEdit_vector_user_z.text())
        except:
            return False
        self.vtkWidget.draw_property.user_vec.vector = np.array([x, y, z])
        self.vtkWidget.update_draw()

    # -------------------------------------------------------------------
    # TAB FOR VIEW
    # -------------------------------------------------------------------
    def _set_view_tab_widgets(self):
        self.checkBox_view_box.setChecked(self.vtkWidget.draw_property.outline.show_box)
        self.checkBox_view_center.setChecked(self.vtkWidget.draw_property.outline.show_center_lines)
        self.checkBox_view_axis.setChecked(self.vtkWidget.draw_property.outline.show_axis)

        self._initial_camera_params = self._get_orientation()
        self._camera_params_xy = {'position': (0.0, 0.0, 1.0),
                                  'focal point': (0.0, 0.0, 0.0),
                                  'view up': (0.0, 1.0, 0.0),
                                  'distance': 1.0,
                                  'clipping range': (0.01, 1000.01),
                                  'orientation': (0.0, 0.0, 0.0),
                                  'parallel_scale': 1.0}

        self._camera_params_yz = {'position': (1.0, 0.0, 0.0),
                                  'focal point': (0.0, 0.0, 0.0),
                                  'view up': (0.0, 0.0, 1.0),
                                  'distance': 1.0,
                                  'clipping range': (0.01, 1000.01),
                                  'orientation': (0.0, -90.0, -90.0),
                                  'parallel_scale': 1.0}

        self._camera_params_xz = {'position': (0.0, -1.0, 0.0),
                                  'focal point': (0.0, 0.0, 0.0),
                                  'view up': (0.0, 0.0, 1.0),
                                  'distance': 1.0,
                                  'clipping range': (0.01, 1000.01),
                                  'orientation': (-90.0, 0.0, 0.0),
                                  'parallel_scale': 1.0}

    def change_view_box(self):
        is_checked = self.checkBox_view_box.isChecked()
        self.vtkWidget.draw_property.outline.show_box = is_checked
        self.vtkWidget.update_draw()

    def change_view_center(self):
        is_checked = self.checkBox_view_center.isChecked()
        self.vtkWidget.draw_property.outline.show_center_lines = is_checked
        self.vtkWidget.update_draw()

    def change_view_axis(self):
        is_checked = self.checkBox_view_axis.isChecked()
        self.vtkWidget.draw_property.outline.show_axis = is_checked
        self.vtkWidget.update_draw()

    def view_xyPlane(self):
        self._set_orientation(self._camera_params_xy)
        self.vtkWidget.update_draw()

    def view_yzPlane(self):
        self._set_orientation(self._camera_params_yz)
        self.vtkWidget.update_draw()

    def view_xzPlane(self):
        self._set_orientation(self._camera_params_xz)
        self.vtkWidget.update_draw()

    def view_reset(self):
        self._set_orientation(self._initial_camera_params)
        self.vtkWidget.update_draw()

    def _get_orientation(self):
        camera = self.vtkWidget.camera
        p = dict()
        p['position'] = camera.GetPosition()
        p['focal point'] = camera.GetFocalPoint()
        p['view up'] = camera.GetViewUp()
        p['distance'] = camera.GetDistance()
        p['clipping range'] = camera.GetClippingRange()
        p['orientation'] = camera.GetOrientation()
        p['parallel_scale'] = camera.GetParallelScale()
        return p

    def _set_orientation(self, p):
        camera = self.vtkWidget.camera
        camera.SetPosition(p['position'])
        camera.SetFocalPoint(p['focal point'])
        camera.SetViewUp(p['view up'])
        camera.SetDistance(p['distance'])
        camera.SetClippingRange(p['clipping range'])
        camera.SetParallelScale(p['parallel_scale'])
