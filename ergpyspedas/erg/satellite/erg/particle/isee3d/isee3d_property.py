from dataclasses import dataclass

import numpy as np


@dataclass
class VectorProperty:
    show: bool
    color: str
    max_squared_length: float
    length_scale: str
    thick: int
    vector: np.ndarray

@dataclass
class ColorbarProperty:
    name: str
    min: float
    max: float
    units: str

    def reset(self):
        self.min = None
        self.max = None

@dataclass
class IsosurfaceProperty:
    show: bool
    mesh: bool
    color: str
    value: float

@dataclass
class Slice2dProperty:
    show_image: bool
    show_contour: bool
    cut_axis: str
    cut_value: float

    @property
    def show(self):
        return self.show_image or self.show_contour

@dataclass
class OutlineProperty:
    show_box: bool
    show_center_lines: bool
    show_axis: bool
    axis_units: str
    axis_screen_size: float
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float

@dataclass
class DrawDataProperty:
    coordinates: str # 'MAG' or 'SC'
    axis_units: str # 'Velocity' or 'Energy'
    units: str # 'PSD' or 'FLUX'
    show_data_index: int


class Isee3dProperty:
    def __init__(self, max_mag_squared_length: float, max_vel_squared_length: float, colormap_name):
        self.mag_vec = VectorProperty(show=True, color='CYAN', max_squared_length=max_mag_squared_length, length_scale='full', thick=4, vector=None)
        self.vel_vec = VectorProperty(show=True, color='YELLOW', max_squared_length=max_vel_squared_length, length_scale='full', thick=4, vector=None)
        self.user_vec = VectorProperty(show=False, color='MAGENTA', max_squared_length=None, length_scale='full', thick=4, vector=np.array([0, 1, 0]))

        self.isosurface1 = IsosurfaceProperty(show=False, mesh=False, color='MAGENTA', value=None)
        self.isosurface2 = IsosurfaceProperty(show=False, mesh=False, color='LIME', value=None)

        self.yz_plane = Slice2dProperty(show_image=False, show_contour=False, cut_axis='x_axis', cut_value=None)
        self.xz_plane = Slice2dProperty(show_image=False, show_contour=False, cut_axis='y_axis', cut_value=None)
        self.xy_plane = Slice2dProperty(show_image=False, show_contour=False, cut_axis='z_axis', cut_value=None)

        self.outline = OutlineProperty(show_box=True, show_center_lines=True, show_axis=True, axis_units='Velocity', axis_screen_size=28,
                                       x_min=None, x_max=None, y_min=None, y_max=None, z_min=None, z_max=None)
        self.colorbar = ColorbarProperty(name=colormap_name, min=None, max=None, units='PSD')

        self.data = DrawDataProperty(coordinates='SC', axis_units='Velocity', units='PSD', show_data_index=0)

    def setup(self, draw_data):

        mag_vec = draw_data.mag_vec
        self.mag_vec.vector = mag_vec

        vel_vec = draw_data.vel_vec
        self.vel_vec.vector = vel_vec

        if self.isosurface1.value is None:
            self.isosurface1.value = draw_data.value.min()
        if self.isosurface2.value is None:
            self.isosurface2.value = draw_data.value.min()

        bounds = draw_data.point_cloud_data.GetBounds()
        min_value = min(bounds[0], bounds[2], bounds[4]) * draw_data.scale
        max_value = max(bounds[1], bounds[3], bounds[5]) * draw_data.scale

        self.outline.x_min = min_value
        self.outline.x_max = max_value
        self.outline.y_min = min_value
        self.outline.y_max = max_value
        self.outline.z_min = min_value
        self.outline.z_max = max_value
        
        eps = 1e-10
        # Minimum value is not displayed in slice, so make it slightly larger than the minimum value.
        if self.yz_plane.cut_value is None:
            self.yz_plane.cut_value = min_value + abs(min_value) * eps
        if self.xz_plane.cut_value is None:
            self.xz_plane.cut_value = min_value + abs(min_value) * eps
        if self.xy_plane.cut_value is None:
            self.xy_plane.cut_value = min_value + abs(min_value) * eps
