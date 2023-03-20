import copy
from dataclasses import dataclass, fields
from typing import Any, Dict, Optional, Union

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6 import QtCore, QtGui, QtWidgets

from ..options.data_option import DataName, DataOptions
from ..options.orbital_info_option import OrbitalInfoName, OrbitalInfoOption
from ..options.support_line_option import SupportLineOption, SupportLineOptions
from ..options.wfc_view_option import WFCViewOption
from ..plot.common import plot_init
from ..utils.colormaps import colormaps
from ..utils.utils import choose_black_or_white_for_high_contrast
from ..utils.widgets import DoubleValidator, IntValidator, LineEditWithValidator


@dataclass
class YaxisWidgetProperty:
    title: str = "TITLE"
    ymin: str = "YMIN"
    ymax: str = "YMAX"
    ylog: str = "YLOG"


@dataclass
class ZaxisWidgetProperty:
    title: str = "TITLE"
    zmin: str = "ZMIN"
    zmax: str = "ZMAX"
    zlog: str = "ZLOG"
    mask: str = "MASK"
    plot: str = "PLOT"


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


class SupportLinesModel(QtCore.QAbstractTableModel):
    def __init__(
        self,
        data: SupportLineOptions,
        parent: Optional[QtCore.QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._props = SupportLineOption.props
        self._data = data
        self._data_backup = copy.deepcopy(self._data)

    def rowCount(
        self,
        parent: Union[
            QtCore.QModelIndex, QtCore.QPersistentModelIndex
        ] = QtCore.QModelIndex(),
    ) -> int:
        return len(self._data)

    def columnCount(
        self,
        parent: Union[
            QtCore.QModelIndex, QtCore.QPersistentModelIndex
        ] = QtCore.QModelIndex(),
    ) -> int:
        return len(self._props)

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int
    ) -> Optional[str]:
        data_names_vs_header_view_names = {
            "species": "Species",
            "m": "M",
            "q": "Q",
            "lsty": "Style",
            "lcol": "Color",
            "enable": "Enable",
        }
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation != QtCore.Qt.Orientation.Horizontal:
            return None
        return data_names_vs_header_view_names[self._props[section]]

    def data(
        self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex], role: int
    ) -> Any:
        # Determine various appearance properties of each data
        if index.isValid():
            row = index.row()
            column = index.column()
            name = self._props[column]
            # Text to show in read-only mode and edit mode
            if role in [
                QtCore.Qt.ItemDataRole.DisplayRole,
                QtCore.Qt.ItemDataRole.EditRole,
            ]:
                return getattr(self._data[row], name)
            # Foreground / background color to show
            else:
                if name == "species":
                    color_idl_code = int(getattr(self._data[row], "lcol"))
                    colormap = colormaps["Blue-Red"]
                    rgb = colormap(color_idl_code)
                    background_color = QtGui.QColor.fromRgbF(*rgb)
                elif name == "enable":
                    is_enable = getattr(self._data[row], name)
                    if is_enable == "ON":
                        # Cyan-like color
                        rgb_255 = (153, 244, 204)
                        rgb = tuple(c / 255 for c in rgb_255)
                        background_color = QtGui.QColor.fromRgbF(*rgb)
                    else:
                        background_color = QtGui.QColor("white")
                else:
                    background_color = QtGui.QColor("white")

                if role == QtCore.Qt.ItemDataRole.BackgroundRole:
                    return background_color

                # Choose foreground color to be black or white
                # based on contrast against background color
                elif role == QtCore.Qt.ItemDataRole.ForegroundRole:
                    r, g, b, _ = background_color.getRgbF()  # type: ignore
                    rgb = choose_black_or_white_for_high_contrast((r, g, b))
                    foreground_color = QtGui.QColor.fromRgbF(*rgb)
                    return foreground_color

        return None

    def flags(
        self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex]
    ) -> QtCore.Qt.ItemFlag:
        # Convention
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags

        default_flags = super().flags(index)
        column = index.column()
        name = self._props[column]
        # Make "enable" column to uneditable
        if name == "enable":
            return default_flags
        return default_flags | QtCore.Qt.ItemFlag.ItemIsEditable

    def setData(
        self,
        index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex],
        value: Any,
        role: int,
    ) -> bool:
        # How to set data in edit mode
        if index.isValid():
            if role == QtCore.Qt.ItemDataRole.EditRole:
                row = index.row()
                column = index.column()
                name = self._props[column]
                setattr(self._data[row], name, value)
                return True
        return False

    def insertRows(
        self,
        row: int,
        count: int,
        parent: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = ...,
    ) -> bool:
        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
        opt = SupportLineOption(
            species="new", m="1", q="1", lsty="0", lcol="0", enable="OFF"
        )
        for _ in range(count):
            self._data.insert(row, opt)
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
        # Use validator so that user cannot input invalid value like non-numbers
        column = index.column()
        names = SupportLineOption.props
        name = names[column]
        if name in ["m", "q"]:
            editor = QtWidgets.QLineEdit(parent)
            editor.setValidator(DoubleValidator())
        elif name == "lsty":
            editor = QtWidgets.QLineEdit(parent)
            # Possible line style options
            editor.setValidator(IntValidator(bottom=0, top=6))
        elif name == "lcol":
            editor = QtWidgets.QLineEdit(parent)
            # Possible line color options
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
        # Change "enable" column to ON/OFF switch
        column = index.column()
        name = model._props[column]
        if name == "enable":
            # Switch ON/OFF on click
            if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                before = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
                after = "OFF" if before == "ON" else "ON"
                model.setData(index, after, QtCore.Qt.ItemDataRole.EditRole)
            return True
        else:
            return super().editorEvent(event, model, option, index)


class OptionsTab(QtWidgets.QWidget):
    def __init__(
        self,
        data_options: DataOptions,
        orbital_info_options: OrbitalInfoOption,
        support_line_options: SupportLineOptions,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._layout = QtWidgets.QVBoxLayout(self)

        # Support lines
        self._support_lines_label = QtWidgets.QLabel("[Support lines]")
        self._layout.addWidget(self._support_lines_label)

        # Model-View pattern in Qt
        # View
        self._support_lines_table_view = QtWidgets.QTableView()
        # Model
        self.support_lines_model = SupportLinesModel(support_line_options)
        # Delegate for custom editing
        support_lines_delegate = SupportLinesDelegate()
        self._support_lines_table_view.setItemDelegate(support_lines_delegate)
        self._support_lines_table_view.setModel(self.support_lines_model)

        # Make table cells look nicer
        self._support_lines_table_view.resizeRowsToContents()
        self._support_lines_table_view.resizeColumnsToContents()
        self._support_lines_table_view.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self._support_lines_table_view.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.support_lines_model.modelReset.connect(self.resize_row_columns)  # type: ignore
        self.support_lines_model.rowsInserted.connect(self.resize_row_columns)  # type: ignore
        self.support_lines_model.rowsRemoved.connect(self.resize_row_columns)  # type: ignore
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
            OrbitalInfoName.lshell: "L-shell",
        }
        self._orbital_info_boxes: Dict[OrbitalInfoName, QtWidgets.QCheckBox] = {}
        for name, label in orbital_info_check_box_labels.items():
            box = QtWidgets.QCheckBox(label)
            self._orbital_info_layout.addWidget(box)
            self._orbital_info_boxes[name] = box

        self._orbital_info_layout.addStretch()
        self._layout.addLayout(self._orbital_info_layout)
        # Setup changeable value
        self.update_orbital_info_boxes_value(orbital_info_options)

        # xyz axis
        # Place almost everything in QGridLayout
        # Row index of QGridLayout
        row_i = 0
        self._axis_layout = QtWidgets.QGridLayout()
        self._layout.addLayout(self._axis_layout)
        self._yaxis_label = QtWidgets.QLabel("[Y axis]")
        self._axis_layout.addWidget(self._yaxis_label, row_i, 0)
        row_i += 1

        y_axis_widget_property = YaxisWidgetProperty()
        self._yaxis_headers = []
        for i, field in enumerate(fields(y_axis_widget_property)):
            label = QtWidgets.QLabel(getattr(y_axis_widget_property, field.name))
            label.setFrameStyle(
                QtWidgets.QFrame.Shape.Box | QtWidgets.QFrame.Shadow.Raised
            )
            self._yaxis_headers.append(label)
            self._axis_layout.addWidget(label, row_i, i)
        row_i += 1

        # y axis widgets
        title_line_edit = QtWidgets.QLineEdit()
        ymin_line_edit = LineEditWithValidator(DoubleValidator())
        ymax_line_edit = LineEditWithValidator(DoubleValidator())
        ylog_check_box = QtWidgets.QCheckBox()
        # Nested layout to center above QCheckBox in each grid
        ylog_check_box_hlayout = QtWidgets.QHBoxLayout()
        ylog_check_box_hlayout.addWidget(ylog_check_box)
        ylog_check_box_hlayout.setContentsMargins(0, 0, 0, 0)
        # Group
        self.yaxis_widgets = YaxisWidgets(
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

        z_axis_widget_property = ZaxisWidgetProperty()
        self._zaxis_headers = []
        for i, field in enumerate(fields(z_axis_widget_property)):
            label = QtWidgets.QLabel(getattr(z_axis_widget_property, field.name))
            label.setFrameStyle(
                QtWidgets.QFrame.Shape.Box | QtWidgets.QFrame.Shadow.Raised
            )
            self._zaxis_headers.append(label)
            self._axis_layout.addWidget(label, row_i, i)
        row_i += 1

        # z axis widgets
        self._zaxis_widgets: Dict[DataName, ZaxisWidgets] = {}
        for name in DataName:
            # Create widgets
            title_line_edit = QtWidgets.QLineEdit()
            zmin_line_edit = LineEditWithValidator(DoubleValidator())
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
        # Setup changeable value
        self.update_xyzaxis_value(data_options)

    def update_xyzaxis_value(self, data_options: DataOptions) -> None:
        # yaxis
        # Assume y properties are all same
        opts = list(data_options.values())
        assert len(opts) >= 1 and all(
            [(opt.ysubtitle, opt.ymin, opt.ymax, opt.ylog) for opt in opts]
        )
        opt = opts[0]
        self.yaxis_widgets.title.setText(opt.ysubtitle)
        self.yaxis_widgets.ylog.setChecked(opt.ylog)
        ymin = opt.ymin
        ymax = opt.ymax
        ymin_str = f"{ymin}"
        ymax_str = f"{ymax}"
        # Used to prevent updating infinitely between two synced components
        with QtCore.QSignalBlocker(self.yaxis_widgets.ymin):
            self.yaxis_widgets.ymin.setText(ymin_str)
        with QtCore.QSignalBlocker(self.yaxis_widgets.ymax):
            self.yaxis_widgets.ymax.setText(ymax_str)

        # zaxis
        for name, opt in data_options.items():
            self._zaxis_widgets[name].title.setText(opt.ytitle)
            zmin = opt.zmin
            zmax = opt.zmax
            zmin_str = f"{zmin}"
            zmax_str = f"{zmax}"
            with QtCore.QSignalBlocker(self._zaxis_widgets[name].zmin):
                self._zaxis_widgets[name].zmin.setText(zmin_str)
            with QtCore.QSignalBlocker(self._zaxis_widgets[name].zmax):
                self._zaxis_widgets[name].zmax.setText(zmax_str)
            self._zaxis_widgets[name].zlog.setChecked(opt.zlog)
            self._zaxis_widgets[name].mask.setChecked(opt.mask)
            self._zaxis_widgets[name].plot.setChecked(opt.plot)

    def update_orbital_info_boxes_value(
        self, orbital_info_options: OrbitalInfoOption
    ) -> None:
        for name in OrbitalInfoName:
            self._orbital_info_boxes[name].setChecked(
                getattr(orbital_info_options, name.value)
            )

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
        # Nested layout to add space on left side
        self._layout_row_1 = QtWidgets.QHBoxLayout()
        self._slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._slider.setTracking(True)
        self._slider.setValue(0)
        self._slider.setMinimum(0)
        self._slider.setMaximum(100)
        self._slider.setEnabled(False)
        self._layout_row_1.addWidget(self._slider)
        self._line_edit = LineEditWithValidator(DoubleValidator())
        self._line_edit.setEnabled(False)
        self._layout_row_1.addWidget(self._line_edit)
        self._layout_row_1.addStretch()
        self._layout.addLayout(self._layout_row_1)


class MaskTab(QtWidgets.QWidget):
    def __init__(
        self,
        data_options: DataOptions,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._layout = QtWidgets.QVBoxLayout(self)
        self._support_lines_label = QtWidgets.QLabel("[Threshold]")
        self._layout.addWidget(self._support_lines_label)

        self._slider_groups: Dict[DataName, SliderGroup] = {}
        for name in DataName:
            group = SliderGroup()
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
        self.setup(data_options)

    def setup(self, data_options: DataOptions) -> None:
        for name, opt in data_options.items():
            group = self._slider_groups[name]
            group._label.setText(opt.mask_label)


class OutputTab(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QtWidgets.QVBoxLayout(self)
        self._support_lines_label = QtWidgets.QLabel("[Output]")
        self._layout.addWidget(self._support_lines_label)
        self._grid_layout = QtWidgets.QGridLayout()
        self._layout.addLayout(self._grid_layout)
        # Width ratio of Button: Other components = 2: 3
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
        self._png_width_line_edit.setText("800")
        self._png_height_line_edit.setText("900")
        self._png_font_size_line_edit.setText("9.0")
        # Calculated cm size from above pixel size with dpi = 100
        self._eps_width_line_edit.setText("20.32")
        self._eps_height_line_edit.setText("22.86")
        self._eps_font_size_line_edit.setText("9.0")


class WFCView(QtWidgets.QWidget):
    def __init__(
        self,
        data_options: DataOptions,
        orbital_info_options: OrbitalInfoOption,
        support_line_options: SupportLineOptions,
        view_options: WFCViewOption = WFCViewOption(),
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
        self._start_line_edit.setFixedWidth(140)
        self._end_label = QtWidgets.QLabel("End:")
        self._end_line_edit = QtWidgets.QLineEdit()
        self._end_line_edit.setFixedWidth(140)
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
        fig = plot_init(view_options.xsize, view_options.ysize)
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
        self._start_line_edit.setText("2017-04-01/13:57:45.000")
        self._end_line_edit.setText("2017-04-01/13:57:53.000")

    def setup_fft_options(self) -> None:
        for text in ["Hanning", "Hamming"]:
            index = self._fft_window_box.findText(text)
            # Not exist
            if index == -1:
                self._fft_window_box.addItem(text)
            if text == "Hanning":
                self._fft_window_box.setCurrentIndex(index)
        self._window_size_line_edit.setText("4096")
        self._stride_line_edit.setText("2048")
        self._n_average_line_edit.setText("3")
