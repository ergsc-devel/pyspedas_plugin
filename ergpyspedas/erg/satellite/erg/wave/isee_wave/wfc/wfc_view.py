import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6 import QtCore, QtGui, QtWidgets

from ..options.options import (
    DataName,
    DataOption,
    OrbitalInfoName,
    SupportLineOptionName,
)
from ..utils.colormaps import colormaps
from ..utils.utils import (
    check_safe_string,
    choose_black_or_white_for_high_contrast,
    safe_eval_formula,
)
from .plot_wfc import plot_wfc_init


class LineEditWithValidator(QtWidgets.QLineEdit):
    def __init__(
        self,
        validator: QtGui.QValidator,
        arg__1: str = "",
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(arg__1, parent)
        self.setValidator(validator)

    def focusOutEvent(self, arg__1: QtGui.QFocusEvent) -> None:
        # args are input, cursor position
        ret = self.validator().validate(self.text(), 0)
        # ret is tuple of state, input, cursor position
        # States are Acceptable, Intermediate, Invalid
        # Since user cannot even input invalid text,
        # considering intermediate is enough
        if ret[0] == QtGui.QValidator.State.Intermediate:  # type: ignore
            self.setFocus()
        else:
            super().focusOutEvent(arg__1)


class DoubleValidator(QtGui.QValidator):
    def __init__(
        self,
        bottom: Optional[float] = None,
        top: Optional[float] = None,
        parent: Optional[QtCore.QObject] = None,
    ) -> None:
        super().__init__(parent)
        if bottom is None:
            bottom = -float("inf")
        self._bottom = bottom
        if top is None:
            top = float("inf")
        self._top = top

    def validate(self, arg__1: str, arg__2: int) -> object:
        is_safe = check_safe_string(arg__1)
        if not is_safe:
            return (QtGui.QValidator.State.Invalid, arg__1, arg__2)
        number = safe_eval_formula(arg__1)
        if number is None:
            return (QtGui.QValidator.State.Intermediate, arg__1, arg__2)
        if number < self._bottom:
            return (QtGui.QValidator.State.Intermediate, arg__1, arg__2)
        if number > self._top:
            return (QtGui.QValidator.State.Intermediate, arg__1, arg__2)
        return (QtGui.QValidator.State.Acceptable, arg__1, arg__2)

    def setBottom(self, arg__1: float) -> None:
        self._bottom = arg__1

    def setTop(self, arg__1: float) -> None:
        self._top = arg__1


class IntValidator(QtGui.QValidator):
    def __init__(
        self,
        bottom: Optional[int] = None,
        top: Optional[int] = None,
        parent: Optional[QtCore.QObject] = None,
    ) -> None:
        super().__init__(parent)
        if bottom is None:
            bottom = -float("inf")  # type: ignore
        self._bottom = bottom
        if top is None:
            top = float("inf")  # type: ignore
        self._top = top

    def validate(self, arg__1: str, arg__2: int) -> object:
        is_safe = check_safe_string(arg__1)
        if not is_safe:
            return (QtGui.QValidator.State.Invalid, arg__1, arg__2)
        number = safe_eval_formula(arg__1)
        if number is None:
            return (QtGui.QValidator.State.Intermediate, arg__1, arg__2)
        if not number.is_integer():
            return (QtGui.QValidator.State.Intermediate, arg__1, arg__2)
        if number < self._bottom:  # type: ignore
            return (QtGui.QValidator.State.Intermediate, arg__1, arg__2)
        if number > self._top:  # type: ignore
            return (QtGui.QValidator.State.Intermediate, arg__1, arg__2)
        return (QtGui.QValidator.State.Acceptable, arg__1, arg__2)

    def setBottom(self, arg__1: int) -> None:
        self._bottom = arg__1

    def setTop(self, arg__1: int) -> None:
        self._top = arg__1


@dataclass
class WFCViewOptions:
    xsize: int = 800  # px
    ysize: int = 1000  # px
    font_size: float = 10  # pt


class YaxisWidgetProperty(Enum):
    title = "TITLE"
    ymin = "YMIN"
    ymax = "YMAX"
    ylog = "YLOG"


class ZaxisWidgetProperty(Enum):
    title = "TITLE"
    zmin = "ZMIN"
    zmax = "ZMAX"
    zlog = "ZLOG"
    mask = "MASK"
    plot = "PLOT"


class SupportLinesModel(QtCore.QAbstractTableModel):
    def __init__(
        self,
        data: List[Dict[SupportLineOptionName, str]],
        parent: Optional[QtCore.QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._names = [name for name in SupportLineOptionName]
        self._data = data
        self._data_backup = copy.deepcopy(self._data)

    @property
    def _row_count(self):
        return len(self._data)

    @property
    def _column_count(self):
        return len(self._names)

    def rowCount(
        self,
        parent: Union[
            QtCore.QModelIndex, QtCore.QPersistentModelIndex
        ] = QtCore.QModelIndex(),
    ) -> int:
        return self._row_count

    def columnCount(
        self,
        parent: Union[
            QtCore.QModelIndex, QtCore.QPersistentModelIndex
        ] = QtCore.QModelIndex(),
    ) -> int:
        return self._column_count

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int
    ) -> Optional[str]:
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation != QtCore.Qt.Orientation.Horizontal:
            return None
        return self._names[section].value

    def data(
        self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex], role: int
    ) -> Any:
        if index.isValid():
            row = index.row()
            column = index.column()
            name = self._names[column]
            if role in [
                QtCore.Qt.ItemDataRole.DisplayRole,
                QtCore.Qt.ItemDataRole.EditRole,
            ]:
                return self._data[row][name]
            else:
                if name == SupportLineOptionName.species:
                    color = self._data[row][SupportLineOptionName.lcol]
                    colormap = colormaps["Blue-Red"]
                    color = colormap(int(color))
                    bg_color = QtGui.QColor.fromRgbF(*color)
                elif name == SupportLineOptionName.enable:
                    is_enable = self._data[row][name]
                    if is_enable == "ON":
                        # Cyan-like color
                        rgb_255 = (153, 244, 204)
                        rgb = tuple(c / 255 for c in rgb_255)
                        bg_color = QtGui.QColor.fromRgbF(*rgb)
                    else:
                        bg_color = QtGui.QColor("white")
                else:
                    bg_color = QtGui.QColor("white")

                if role == QtCore.Qt.ItemDataRole.BackgroundRole:
                    return bg_color

                elif role == QtCore.Qt.ItemDataRole.ForegroundRole:
                    r, g, b, _ = bg_color.getRgbF()  # type: ignore
                    color = choose_black_or_white_for_high_contrast((r, g, b))
                    fg_color = QtGui.QColor.fromRgbF(*color)
                    return fg_color

        return None

    def flags(
        self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex]
    ) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        default_flags = super().flags(index)
        column = index.column()
        name = self._names[column]
        if name == SupportLineOptionName.enable:
            return default_flags  #  | QtCore.Qt.ItemFlag.ItemIsSelectable
        return default_flags | QtCore.Qt.ItemFlag.ItemIsEditable

    def setData(
        self,
        index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex],
        value: Any,
        role: int,
    ) -> bool:
        if index.isValid():
            if role == QtCore.Qt.ItemDataRole.EditRole:
                row = index.row()
                column = index.column()
                name = self._names[column]
                self._data[row][self._names[column]] = value
                # TODO: Not necessary right now but may be important for another usage
                # self.dataChanged.emit(index, index, {role})
                return True
        return False

    def insertRows(
        self,
        row: int,
        count: int,
        parent: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = ...,
    ) -> bool:
        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
        default = {
            SupportLineOptionName.species: "new",
            SupportLineOptionName.m: "1",
            SupportLineOptionName.q: "1",
            SupportLineOptionName.lsty: "0",
            SupportLineOptionName.lcol: "0",
            SupportLineOptionName.enable: "OFF",
        }
        for _ in range(count):
            self._data.insert(row, default)
        self.endInsertRows()
        return True

    def removeRows(
        self,
        row: int,
        count: int,
        parent: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = ...,
    ) -> bool:
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
        for _ in range(count):
            del self._data[row]
        self.endRemoveRows()
        return True

    def reset(self) -> None:
        self.beginResetModel()
        self._data = copy.deepcopy(self._data_backup)
        self.endResetModel()


class SupportLinesDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex],
    ) -> QtWidgets.QWidget:
        column = index.column()
        names = [name for name in SupportLineOptionName]
        name = names[column]
        if name in [SupportLineOptionName.m, SupportLineOptionName.q]:
            editor = QtWidgets.QLineEdit(parent)
            editor.setValidator(DoubleValidator())
        elif name == SupportLineOptionName.lsty:
            editor = QtWidgets.QLineEdit(parent)
            editor.setValidator(IntValidator(bottom=0, top=6))
        elif name == SupportLineOptionName.lcol:
            editor = QtWidgets.QLineEdit(parent)
            editor.setValidator(IntValidator(bottom=0, top=255))
        else:
            editor = super().createEditor(parent, option, index)
        return editor

    def editorEvent(
        self,
        event: QtCore.QEvent,
        model: SupportLinesModel,
        option: QtWidgets.QStyleOptionViewItem,
        index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex],
    ) -> bool:
        # TODO: not selecting
        column = index.column()
        name = model._names[column]
        if name == SupportLineOptionName.enable:
            if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                before = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
                after = "OFF" if before == "ON" else "ON"
                model.setData(index, after, QtCore.Qt.ItemDataRole.EditRole)
            return True
        else:
            return super().editorEvent(event, model, option, index)


@dataclass
class YaxisWidgets:
    title: QtWidgets.QLineEdit
    ymin: QtWidgets.QLineEdit
    ymax: QtWidgets.QLineEdit
    ylog: QtWidgets.QCheckBox


@dataclass
class ZaxisWidgets:
    title: QtWidgets.QLineEdit
    zmin: QtWidgets.QLineEdit
    zmax: QtWidgets.QLineEdit
    zlog: QtWidgets.QCheckBox
    mask: QtWidgets.QCheckBox
    plot: QtWidgets.QCheckBox


class OptionsTab(QtWidgets.QWidget):
    def __init__(
        self,
        data_options: Dict[DataName, DataOption],
        orbital_info_options: Dict[OrbitalInfoName, bool],
        support_line_options: List[Dict[SupportLineOptionName, str]],
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._layout = QtWidgets.QVBoxLayout(self)

        # Support lines
        self._support_lines_label = QtWidgets.QLabel("[Support lines]")
        self._layout.addWidget(self._support_lines_label)
        self._support_lines_table_view = QtWidgets.QTableView()
        self._support_lines_model = SupportLinesModel(support_line_options)
        support_lines_delegate = SupportLinesDelegate()
        self._support_lines_table_view.setItemDelegate(support_lines_delegate)
        self._support_lines_table_view.setModel(self._support_lines_model)
        self._support_lines_table_view.resizeRowsToContents()
        self._support_lines_table_view.resizeColumnsToContents()
        self._support_lines_table_view.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self._support_lines_table_view.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self._support_lines_model.modelReset.connect(self.resize_row_columns)  # type: ignore
        self._support_lines_model.rowsInserted.connect(self.resize_row_columns)  # type: ignore
        self._support_lines_model.rowsRemoved.connect(self.resize_row_columns)  # type: ignore
        self.resize_row_columns()
        self._layout.addWidget(self._support_lines_table_view)
        self._support_lines_button_layout = QtWidgets.QHBoxLayout()
        self._support_lines_apply_button = QtWidgets.QPushButton("Apply")
        self._support_lines_button_layout.addWidget(self._support_lines_apply_button)
        self._support_lines_add_button = QtWidgets.QPushButton("Add New Line")
        self._support_lines_button_layout.addWidget(self._support_lines_add_button)
        self._support_lines_delete_button = QtWidgets.QPushButton(
            "Delete Selected Lines"
        )
        self._support_lines_button_layout.addWidget(self._support_lines_delete_button)
        self._support_lines_reset_button = QtWidgets.QPushButton("Reset")
        self._support_lines_button_layout.addWidget(self._support_lines_reset_button)
        self._layout.addLayout(self._support_lines_button_layout)

        # Orbital information
        self._orbital_label = QtWidgets.QLabel("[Orbital information]")
        self._layout.addWidget(self._orbital_label)
        self._orbital_info_layout = QtWidgets.QHBoxLayout()

        orbital_info_check_box_labels = {
            OrbitalInfoName.mlt: "MLT",
            OrbitalInfoName.mlat: "MLAT",
            OrbitalInfoName.alt: "Altitude",
            OrbitalInfoName.l: "L-shell",
        }
        self._orbital_info_boxes: Dict[OrbitalInfoName, QtWidgets.QCheckBox] = {}
        for name, label in orbital_info_check_box_labels.items():
            box = QtWidgets.QCheckBox(label)
            self._orbital_info_layout.addWidget(box)
            self._orbital_info_boxes[name] = box

        self.setup_orbital_info_boxes_value(orbital_info_options)
        self._orbital_info_layout.addStretch()
        self._layout.addLayout(self._orbital_info_layout)

        # xyz axis
        row_i = 0
        self._axis_layout = QtWidgets.QGridLayout()
        self._layout.addLayout(self._axis_layout)
        self._yaxis_label = QtWidgets.QLabel("[Y axis]")
        self._axis_layout.addWidget(self._yaxis_label, row_i, 0)
        row_i += 1

        self._yaxis_headers = []
        for i, prop in enumerate(YaxisWidgetProperty):
            label = QtWidgets.QLabel(prop.value)
            label.setFrameStyle(
                QtWidgets.QFrame.Shape.Box | QtWidgets.QFrame.Shadow.Raised
            )
            # label.setLineWidth(0)
            # label.setMidLineWidth(0)
            self._yaxis_headers.append(label)
            self._axis_layout.addWidget(label, row_i, i)
        row_i += 1

        opts = list(data_options.values())

        # Assume y properties are all same
        assert len(opts) >= 1 and all(
            [(opt.ysubtitle, opt.ymin, opt.ymax, opt.ylog) for opt in opts]
        )
        opt = opts[0]

        title_line_edit = QtWidgets.QLineEdit()
        ymin_line_edit = LineEditWithValidator(DoubleValidator())
        ymax_line_edit = LineEditWithValidator(DoubleValidator())
        ylog_check_box = QtWidgets.QCheckBox()
        ylog_check_box_hlayout = QtWidgets.QHBoxLayout()
        ylog_check_box_hlayout.addWidget(ylog_check_box)
        ylog_check_box_hlayout.setContentsMargins(0, 0, 0, 0)
        self._yaxis_widgets = YaxisWidgets(
            title=title_line_edit,
            ymin=ymin_line_edit,
            ymax=ymax_line_edit,
            ylog=ylog_check_box,
        )
        self._axis_layout.addWidget(title_line_edit, row_i, 0)
        self._axis_layout.addWidget(ymin_line_edit, row_i, 1)
        self._axis_layout.addWidget(ymax_line_edit, row_i, 2)
        self._axis_layout.addLayout(
            ylog_check_box_hlayout, row_i, 3, QtCore.Qt.AlignmentFlag.AlignCenter
        )
        row_i += 1

        self._zaxis_label = QtWidgets.QLabel("[Z axis]")
        self._axis_layout.addWidget(self._zaxis_label, row_i, 0)
        row_i += 1

        self._zaxis_headers = []
        for i, prop in enumerate(ZaxisWidgetProperty):
            label = QtWidgets.QLabel(prop.value)
            label.setFrameStyle(
                QtWidgets.QFrame.Shape.Box | QtWidgets.QFrame.Shadow.Raised
            )
            # label.setLineWidth(0)
            # label.setMidLineWidth(0)
            self._zaxis_headers.append(label)
            self._axis_layout.addWidget(label, row_i, i)
        row_i += 1

        self._zaxis_widgets: Dict[DataName, ZaxisWidgets] = {}
        for name, opt in data_options.items():
            # Create widgets
            title_line_edit = QtWidgets.QLineEdit()
            zmin_line_edit = LineEditWithValidator(DoubleValidator())
            zmin_line_edit.setValidator(DoubleValidator())
            zmax_line_edit = LineEditWithValidator(DoubleValidator())
            zlog_check_box = QtWidgets.QCheckBox()
            zlog_check_box_layout = QtWidgets.QHBoxLayout()
            zlog_check_box_layout.addWidget(zlog_check_box)

            zlog_check_box_layout.setContentsMargins(0, 0, 0, 0)
            zmask_check_box = QtWidgets.QCheckBox()
            zmask_check_box_layout = QtWidgets.QHBoxLayout()
            zmask_check_box_layout.addWidget(zmask_check_box)

            zmask_check_box_layout.setContentsMargins(0, 0, 0, 0)
            plot_check_box = QtWidgets.QCheckBox()
            plot_check_box_layout = QtWidgets.QHBoxLayout()
            plot_check_box_layout.addWidget(plot_check_box)

            plot_check_box_layout.setContentsMargins(0, 0, 0, 0)
            # Save widgets to dict
            self._zaxis_widgets[name] = ZaxisWidgets(
                title=title_line_edit,
                zmin=zmin_line_edit,
                zmax=zmax_line_edit,
                zlog=zlog_check_box,
                mask=zmask_check_box,
                plot=plot_check_box,
            )
            # Add widgets to layout
            self._axis_layout.addWidget(title_line_edit, row_i, 0)
            self._axis_layout.addWidget(zmin_line_edit, row_i, 1)
            self._axis_layout.addWidget(zmax_line_edit, row_i, 2)
            self._axis_layout.addLayout(
                zlog_check_box_layout, row_i, 3, QtCore.Qt.AlignmentFlag.AlignCenter
            )
            self._axis_layout.addLayout(
                zmask_check_box_layout, row_i, 4, QtCore.Qt.AlignmentFlag.AlignCenter
            )
            self._axis_layout.addLayout(
                plot_check_box_layout, row_i, 5, QtCore.Qt.AlignmentFlag.AlignCenter
            )

            row_i += 1

        self._xyzaxis_button_layout = QtWidgets.QHBoxLayout()
        self._xyzaxis_button_layout.addStretch()
        self._xyzaxis_apply_button = QtWidgets.QPushButton("Apply")
        self._xyzaxis_button_layout.addWidget(self._xyzaxis_apply_button)
        self._xyzaxis_reset_button = QtWidgets.QPushButton("Reset")
        self._xyzaxis_button_layout.addWidget(self._xyzaxis_reset_button)
        self._xyzaxis_button_layout.addStretch()
        self._layout.addLayout(self._xyzaxis_button_layout)
        self._layout.addStretch()
        self.setup_xyzaxis_value(data_options)

    def setup_xyzaxis_value(self, data_options: Dict[DataName, DataOption]) -> None:
        # Assume y properties are all same
        opts = list(data_options.values())
        assert len(opts) >= 1 and all(
            [(opt.ysubtitle, opt.ymin, opt.ymax, opt.ylog) for opt in opts]
        )
        opt = opts[0]
        self._yaxis_widgets.title.setText(opt.ysubtitle)
        self._yaxis_widgets.ylog.setChecked(opt.ylog)
        # TODO: Here limit values apperance is only changed but data structure should also be changed
        # But that case you need to remember log
        ymin = opt.ymin
        ymax = opt.ymax
        if opt.ylog:
            ymin = max(ymin, np.finfo(float).eps)  # type: ignore
            ymax = max(ymax, np.finfo(float).eps)  # type: ignore
        self._yaxis_widgets.ymin.setText(f"{ymin}")
        self._yaxis_widgets.ymax.setText(f"{ymax}")

        for name, opt in data_options.items():
            self._zaxis_widgets[name].title.setText(opt.ytitle)
            zmin = opt.zmin
            zmax = opt.zmax
            if opt.zlog:
                zmin = max(zmin, np.finfo(float).eps)  # type: ignore
                zmax = max(zmax, np.finfo(float).eps)  # type: ignore
            self._zaxis_widgets[name].zmin.setText(f"{zmin}")
            self._zaxis_widgets[name].zmax.setText(f"{zmax}")
            self._zaxis_widgets[name].zlog.setChecked(opt.zlog)
            self._zaxis_widgets[name].mask.setChecked(opt.mask)
            self._zaxis_widgets[name].plot.setChecked(opt.plot)

    def setup_orbital_info_boxes_value(
        self, orbital_info_options: Dict[OrbitalInfoName, bool]
    ) -> None:
        for name in OrbitalInfoName:
            self._orbital_info_boxes[name].setChecked(orbital_info_options[name])

    def resize_row_columns(self):
        self._support_lines_table_view.resizeRowsToContents()
        self._support_lines_table_view.resizeColumnsToContents()
        horizontal_header = self._support_lines_table_view.horizontalHeader()
        horizontal_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)


class SliderGroup(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QtWidgets.QVBoxLayout()
        self._label = QtWidgets.QLabel()
        self._layout.addWidget(self._label)
        self._layout_row_1 = QtWidgets.QHBoxLayout()
        self._slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._slider.setTracking(True)
        self._layout_row_1.addWidget(self._slider)
        self._line_edit = QtWidgets.QLineEdit()
        self._layout_row_1.addWidget(self._line_edit)
        self._layout_row_1.addStretch()
        self._layout.addLayout(self._layout_row_1)


class MaskTab(QtWidgets.QWidget):
    def __init__(
        self,
        data_options: Dict[DataName, DataOption],
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._layout = QtWidgets.QVBoxLayout(self)
        self._support_lines_label = QtWidgets.QLabel("[Threshold]")
        self._layout.addWidget(self._support_lines_label)

        self._slider_groups: Dict[DataName, SliderGroup] = {}
        for name, opt in data_options.items():
            group = SliderGroup()
            group._label.setText(opt.mask_label + ":")
            group._slider.setValue(0)
            group._slider.setMinimum(0)
            group._slider.setMaximum(100)
            self._slider_groups[name] = group
            self._layout.addLayout(group._layout)

        self._apply_button = QtWidgets.QPushButton("Apply")
        self._reset_button = QtWidgets.QPushButton("Revert to Default")
        self._apply_reset_layout = QtWidgets.QHBoxLayout()
        self._apply_reset_layout.addStretch()
        self._apply_reset_layout.addWidget(self._apply_button)
        self._apply_reset_layout.addWidget(self._reset_button)
        self._apply_reset_layout.addStretch()
        self._layout.addLayout(self._apply_reset_layout)
        self._layout.addStretch()


class OutputTab(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QtWidgets.QVBoxLayout(self)
        self._support_lines_label = QtWidgets.QLabel("[Output]")
        self._layout.addWidget(self._support_lines_label)
        self._grid_layout = QtWidgets.QGridLayout()
        self._layout.addLayout(self._grid_layout)
        self._grid_layout.setColumnStretch(0, 2)
        self._grid_layout.setColumnStretch(1, 3)
        self._layout.addStretch()

        self._eps_button = QtWidgets.QPushButton("EPS File (.eps)")
        self._grid_layout.addWidget(self._eps_button, 0, 0)

        self._eps_layout = QtWidgets.QHBoxLayout()
        self._grid_layout.addLayout(self._eps_layout, 0, 1)
        self._eps_width_line_edit = QtWidgets.QLineEdit()
        self._eps_times_label = QtWidgets.QLabel("x")
        self._eps_height_line_edit = QtWidgets.QLineEdit()
        self._eps_unit_label = QtWidgets.QLabel("cm")
        self._eps_font_size_label = QtWidgets.QLabel("Font size:")
        self._eps_font_size_line_edit = QtWidgets.QLineEdit()
        self._eps_layout.addWidget(self._eps_width_line_edit)
        self._eps_layout.addWidget(self._eps_times_label)
        self._eps_layout.addWidget(self._eps_height_line_edit)
        self._eps_layout.addWidget(self._eps_unit_label)
        self._eps_layout.addWidget(self._eps_font_size_label)
        self._eps_layout.addWidget(self._eps_font_size_line_edit)

        self._png_button = QtWidgets.QPushButton("PNG File (.png)")
        self._grid_layout.addWidget(self._png_button, 1, 0)

        self._png_layout = QtWidgets.QHBoxLayout()
        self._grid_layout.addLayout(self._png_layout, 1, 1)
        self._png_width_line_edit = QtWidgets.QLineEdit()
        self._png_times_label = QtWidgets.QLabel("x")
        self._png_height_line_edit = QtWidgets.QLineEdit()
        self._png_unit_label = QtWidgets.QLabel("px")
        self._png_font_size_label = QtWidgets.QLabel("Font size:")
        self._png_font_size_line_edit = QtWidgets.QLineEdit()
        self._png_layout.addWidget(self._png_width_line_edit)
        self._png_layout.addWidget(self._png_times_label)
        self._png_layout.addWidget(self._png_height_line_edit)
        self._png_layout.addWidget(self._png_unit_label)
        self._png_layout.addWidget(self._png_font_size_label)
        self._png_layout.addWidget(self._png_font_size_line_edit)

        self._tplot_button = QtWidgets.QPushButton("tplot Save File (.tplot)")
        self._grid_layout.addWidget(self._tplot_button, 2, 0)

        self.setup()

    def setup(self) -> None:
        self._eps_width_line_edit.setText("20.32")
        self._eps_height_line_edit.setText("25.4")
        self._eps_font_size_line_edit.setText("10")
        self._png_width_line_edit.setText("800")
        self._png_height_line_edit.setText("1000")
        self._png_font_size_line_edit.setText("10")


class WFCView(QtWidgets.QWidget):
    def __init__(
        self,
        data_options: Dict[DataName, DataOption],
        orbital_info_options: Dict[OrbitalInfoName, bool],
        support_line_options: List[Dict[SupportLineOptionName, str]],
        view_options: WFCViewOptions = WFCViewOptions(),
    ) -> None:
        super().__init__()
        self.setWindowTitle("ISEE_Wave (WFC)")
        self._layout = QtWidgets.QGridLayout(self)

        # tlimit layout
        self._tlimit_layout = QtWidgets.QHBoxLayout()
        self._layout.addLayout(self._tlimit_layout, 0, 0, 1, 1)

        self._tlimit_layout_wo_stretch = QtWidgets.QVBoxLayout()
        self._tlimit_layout.addLayout(self._tlimit_layout_wo_stretch)

        self._tlimit_button = QtWidgets.QPushButton("Get Time Interval from OFA")
        self._tlimit_layout_wo_stretch.addWidget(self._tlimit_button)

        self._time_layout = QtWidgets.QHBoxLayout()
        self._start_label = QtWidgets.QLabel("Start:")
        self._start_line_edit = QtWidgets.QLineEdit()
        self._end_label = QtWidgets.QLabel("End:")
        self._end_line_edit = QtWidgets.QLineEdit()
        self._time_layout.addWidget(self._start_label)
        self._time_layout.addWidget(self._start_line_edit)
        self._time_layout.addStretch()
        self._time_layout.addWidget(self._end_label)
        self._time_layout.addWidget(self._end_line_edit)
        self._tlimit_layout_wo_stretch.addLayout(self._time_layout)

        # Left side stretch, must be written here
        self._tlimit_layout.addStretch()

        # fft_layout
        self._fft_layout = QtWidgets.QGridLayout()
        # QGridLayout must be added to its parent here before anything is done with it
        self._layout.addLayout(self._fft_layout, 0, 1, 1, 1)

        self._fft_option_layout_row_0 = QtWidgets.QHBoxLayout()
        self._fft_option_layout_row_1 = QtWidgets.QHBoxLayout()
        self._fft_layout.addLayout(self._fft_option_layout_row_0, 0, 0, 1, 2)
        self._fft_layout.addLayout(self._fft_option_layout_row_1, 1, 0, 1, 2)

        self._fft_window_label = QtWidgets.QLabel("FFT window:")
        self._fft_option_layout_row_0.addWidget(self._fft_window_label)
        self._fft_window_box = QtWidgets.QComboBox()
        self._fft_window_box.addItem("Hanning")
        self._fft_window_box.addItem("Hamming")
        self._fft_option_layout_row_0.addWidget(self._fft_window_box)
        self._fft_option_layout_row_0.addStretch()
        self._fft_revert_button = QtWidgets.QPushButton("Revert to Default")
        self._fft_option_layout_row_0.addWidget(self._fft_revert_button)

        self._window_size_label = QtWidgets.QLabel("Window size:")
        self._fft_option_layout_row_1.addWidget(self._window_size_label)
        self._window_size_line_edit = QtWidgets.QLineEdit()
        self._window_size_line_edit.setFixedWidth(40)
        self._fft_option_layout_row_1.addWidget(self._window_size_line_edit)
        self._stride_label = QtWidgets.QLabel("Stride:")
        self._fft_option_layout_row_1.addWidget(self._stride_label)
        self._stride_line_edit = QtWidgets.QLineEdit()
        self._stride_line_edit.setFixedWidth(40)
        self._fft_option_layout_row_1.addWidget(self._stride_line_edit)
        self._n_average_label = QtWidgets.QLabel("N_average:")
        self._fft_option_layout_row_1.addWidget(self._n_average_label)
        self._n_average_line_edit = QtWidgets.QLineEdit()
        self._n_average_line_edit.setFixedWidth(40)
        self._fft_option_layout_row_1.addWidget(self._n_average_line_edit)

        self._fft_calc_button = QtWidgets.QPushButton("=> Start Calculation")
        policy = self._fft_calc_button.sizePolicy()
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        self._fft_calc_button.setSizePolicy(policy)
        self._fft_layout.addWidget(self._fft_calc_button, 0, 2, 2, 2)

        # plot_layout
        # HACK: Put single figure in nested layout with stretch
        # in order not the figure to stretch but spacings around the figure to stretch
        self._canvas_vlayout = QtWidgets.QVBoxLayout()
        self._layout.addLayout(self._canvas_vlayout, 1, 0, 1, 1)
        self._canvas_hlayout = QtWidgets.QHBoxLayout()
        self._canvas_vlayout.addLayout(self._canvas_hlayout)
        fig = plot_wfc_init(view_options.xsize, view_options.ysize)
        self._canvas = FigureCanvasQTAgg(fig)
        self._canvas_hlayout.addWidget(self._canvas)
        self._canvas_hlayout.addStretch()
        self._canvas_vlayout.addStretch()

        # tab_layout
        self._tabs = QtWidgets.QTabWidget()
        self._options_tab = OptionsTab(
            data_options=data_options,
            orbital_info_options=orbital_info_options,
            support_line_options=support_line_options,
            parent=self,
        )
        self._mask_tab = MaskTab(data_options, self)
        self._output_tab = OutputTab(self)
        self._tabs.addTab(self._options_tab, "Options")
        self._tabs.addTab(self._mask_tab, "Mask")
        self._tabs.addTab(self._output_tab, "Output")
        self._layout.addWidget(self._tabs, 1, 1, 1, 1)

        self._layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

        self.setup_trange()
        self.setup_fft_options()

    def setup_trange(self) -> None:
        self._start_line_edit.setText("2017-04-01/13:57:45")
        self._end_line_edit.setText("2017-04-01/13:57:53")

    def setup_fft_options(self) -> None:
        for text in ["Hanning", "Hamming"]:
            ret = self._fft_window_box.findText(text)
            if ret == -1:
                self._fft_window_box.addItem(text)
        self._window_size_line_edit.setText("4096")
        self._stride_line_edit.setText("2048")
        self._n_average_line_edit.setText("3")
