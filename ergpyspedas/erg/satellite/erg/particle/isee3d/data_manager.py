from __future__ import annotations

import math
import random
from dataclasses import dataclass

import numpy as np
import vtk
from vtkmodules.numpy_interface import dataset_adapter as dsa

import pyspedas
import pytplot
from pytplot import get_data
from pyspedas.utilities.time_double import time_double
from pyspedas.utilities.time_string import time_string

from ..erg_convert_flux_units import erg_convert_flux_units


@dataclass
class DrawData:
    start_data_time: str
    end_data_time: str
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    scale: float
    value: np.ndarray
    mag_vec: np.ndarray
    vel_vec: np.ndarray
    point_cloud_data: vtk.vtkPolyData
    image_data: vtk.vtkImageData

class DataManager:
    def __init__(self, dists, mag_vn, vel_vn):
        self._dists = dists
        self._mag_vn = mag_vn
        self._vel_vn = vel_vn
        self._data_dict = {}

    @property
    def max_mag_squared_length(self) -> float:
        mag_squared_length_array = np.square(self._data_dict['bfield'][1]).sum(axis=1)
        max_mag_index = np.argmax(mag_squared_length_array)
        max_mag_squared_length = mag_squared_length_array[max_mag_index]
        return max_mag_squared_length
    
    @property
    def max_vel_squared_length(self) -> float:
        vel_squared_length_array = np.square(self._data_dict['velocity'][1]).sum(axis=1)
        max_vel_index = np.argmax(vel_squared_length_array)
        max_vel_squared_length = vel_squared_length_array[max_vel_index]
        return max_vel_squared_length
    
    def setup(self):
        self._adjust_dists()
        self._store_tvar(self._mag_vn, key_name='bfield')
        self._store_tvar(self._vel_vn, key_name='velocity')
        # self._set_maximum_vectors()
    
    def make_draw_data(self, draw_data_property) -> DrawData:
        mag_vec = self._data_dict['bfield'][1][draw_data_property.show_data_index]
        vel_vec = self._data_dict['velocity'][1][draw_data_property.show_data_index]

        data_key = self._data_dict['time'][draw_data_property.show_data_index]
        onedata = self._data_dict['data'][data_key]
        azimth = onedata["azim"]
        elevation = onedata["elev"]
        if draw_data_property.axis_units=='Velocity':
            r = onedata["v"]
        elif  draw_data_property.axis_units=='Energy':
            r = onedata["energy"]
        
        x_coord = r * np.cos(np.radians(azimth)) * np.cos(np.radians(elevation))
        y_coord = r * np.sin(np.radians(azimth)) * np.cos(np.radians(elevation))
        z_coord = r * np.sin(np.radians(elevation))
        if draw_data_property.coordinates == 'MAG':
            # ROTATION TO MAG COORDINATE
            x_coord, y_coord, z_coord, mag_vec, vel_vec = self._transform_to_mag(x_coord, y_coord, z_coord, mag_vec, vel_vec)
        
        if draw_data_property.units == 'PSD':
            v_array = onedata['psd']
        elif draw_data_property.units == 'FLUX':
            v_array = onedata['flux']
        start_data_time = self._data_dict['time'][draw_data_property.show_data_index]
        if draw_data_property.show_data_index < len(self._data_dict['time']) - 1:
            end_data_time = self._data_dict['time'][draw_data_property.show_data_index + 1]
        else:
            end_data_time = None

        x_array, y_array, z_array, v_array = self._make_draw_array(x_coord, y_coord, z_coord, v_array)
        scale = self._calculate_scale(x_array, y_array, z_array)
        x_normalized_array = x_array/scale
        y_normalized_array = y_array/scale
        z_normalized_array = z_array/scale

        # vtk points data
        point_cloud_data = self._make_point_cloud_data(x_normalized_array, y_normalized_array, z_normalized_array, v_array)

        # vtk 3d image data
        image_data = self._make_image_data(point_cloud_data, spacing=0.02)

        draw_data = DrawData(start_data_time=start_data_time,
                            end_data_time=end_data_time,
                            x=x_normalized_array,
                            y=y_normalized_array,
                            z=z_normalized_array,
                            scale=scale,
                            value=v_array,
                            mag_vec=mag_vec,
                            vel_vec=vel_vec,
                            point_cloud_data=point_cloud_data,
                            image_data=image_data)

        return draw_data

    def _extract_dist(self, dist_id):
        '''
        PySPEDASの新しい仕様では、get_dist からの戻り値を dists としたとき、
        dists[0]のようにしてある時間のデータを取得できるらしいので、この関数は不要になる
        '''
        dist = {}
        for k, v in self._dists.items():
            output_value = v
            if isinstance(v, np.ndarray):
                if isinstance(v[0], np.ndarray):
                    output_value = v[:, :, :, dist_id]
                else:
                    output_value = v[dist_id]
            dist[k] = output_value
        return dist

    def _adjust_dists(self):
        dists_dict = {}
        for i in range(len(self._dists['time'])):
            dist = self._extract_dist(i)
            
            tmp_data = {}
            ene_id = np.where(~np.isnan(dist['energy'][:, 0, 0]))
            tmp_data['data_flax'] = dist['data'][ene_id].astype('float64') # 元は float32
            tmp_data['bins'] = dist['bins'][ene_id]
            tmp_data['energy'] = dist['energy'][ene_id].astype('float64') # 元は float32
            tmp_data['denergy'] = dist['denergy'][ene_id].astype('float64') # 元は float32
            tmp_data['nenergy'] = np.nan
            tmp_data['phi'] = dist['phi'][ene_id]
            tmp_data['dphi'] = dist['dphi'][ene_id]
            tmp_data['theta'] = dist['theta'][ene_id]
            tmp_data['dtheta'] = dist['dtheta'][ene_id]

            dist_df = erg_convert_flux_units(dist, units='df')
            tmp_data['data_psd'] = dist_df['data'][ene_id].astype('float64') # 元は float32

            c = 299792458.0 # m/s
            erest = dist['mass'] * c ** 2 / 1e6 # convert mass from eV/(km/s)^2 to eV/c^2
            time = time_string(dist['time'])
            end_time = time_string(dist['end_time'])

            data = {'energy': tmp_data['energy'].flatten(),
                    'v': (c * np.sqrt( 1 - 1/((tmp_data['energy']/erest + 1) ** 2) )  /  1000).flatten(),
                    'azim': tmp_data['phi'].flatten(),
                    # IDL版の処理。この後、直交座標に変換するときに、elev = 90 - elev として theta の値に戻していたので、この時点で elev = theta にする
                    # 'elev': 90 - tmp_data['theta'].flatten(),
                    'elev': tmp_data['theta'].flatten(),
                    'flux': tmp_data['data_flax'].flatten(),
                    'psd': tmp_data['data_psd'].flatten(),
                    'end_time': end_time}

            dists_dict[time] = data
        
        self._data_dict['data'] = dists_dict
        self._data_dict['time'] = list(dists_dict.keys())

    def _store_tvar(self, variable_name, key_name):
        name = variable_name
        times_double = time_double(self._dists['time'])
        suffix = '_stel3d_temp'
        newname = name + suffix
        pyspedas.tinterpol(name, times_double, newname=newname)
        data = get_data(newname)
        pytplot.store_data(newname, delete=True)
        self._data_dict[key_name] = data

    def _calculate_scale(self, x_array, y_array, z_array):
        x_range = x_array.max() - x_array.min()
        y_range = y_array.max() - y_array.min()
        z_range = z_array.max() - z_array.min()
        return max(x_range, y_range, z_range)

    def _make_draw_array(self, x_array, y_array, z_array, v_array):
        # Randomise for stabirity of delaunay3d. https://vtkusers.public.kitware.narkive.com/FLceJKi0/delaunay3d-unable-to-factor-linear-system
        index_array = np.arange(v_array.shape[0])
        random.seed(0)
        random.shuffle(index_array)
        v_array = v_array[index_array]
        x_array = x_array[index_array]
        y_array = y_array[index_array]
        z_array = z_array[index_array]

        new_x_array = []
        new_y_array = []
        new_z_array = []
        new_v_array = []
        for v, x, y, z in zip(v_array, x_array, y_array, z_array):
            # Remove nan and negative points.
            if (np.isnan(v)) or v <= 0:
                continue
            new_v_array.append(v)
            new_x_array.append(x)
            new_y_array.append(y)
            new_z_array.append(z)
        new_v_array = np.array(new_v_array)
        new_x_array = np.array(new_x_array)
        new_y_array = np.array(new_y_array)
        new_z_array = np.array(new_z_array)
        return new_x_array, new_y_array, new_z_array, new_v_array

    def _transform_to_mag(self, x_coord, y_coord, z_coord, mag_vec, vel_vec):
        # ROTATION TO MAG COORDINATE
        mag_vec_unit = mag_vec / np.linalg.norm(mag_vec)
        vel_vec_unit = vel_vec / np.linalg.norm(vel_vec)
        # Cross product of magnetc and velocity vectors, B x V (=new Y) 
        mv_p = np.cross(mag_vec_unit, vel_vec_unit)
        mv_p = mv_p / np.linalg.norm(mv_p)
        # Cross product of (BxV) x B (=new X)
        mvm_p = np.cross(mv_p, mag_vec_unit)
        mvm_p = mvm_p / np.linalg.norm(mvm_p)
        # ROTATION USING MATRIX 
        rotmat = np.stack([mvm_p, mv_p, mag_vec_unit])
        
        coords = np.stack([x_coord, y_coord, z_coord])
        new_x_coord, new_y_coord, new_z_coord = np.dot(rotmat, coords)
        
        new_mag_vec = np.dot(rotmat, mag_vec.reshape(3, 1))
        new_vel_vec = np.dot(rotmat, vel_vec.reshape(3, 1))

        return new_x_coord, new_y_coord, new_z_coord, new_mag_vec, new_vel_vec 

    def _make_point_cloud_data(self, x_array, y_array, z_array, v_array):
        points = vtk.vtkPoints()
        values = vtk.vtkDoubleArray()
        values.SetName('ValueArray')

        for p in zip(v_array, x_array, y_array, z_array):
            points.InsertNextPoint(p[1:])
            values.InsertNextValue(p[0])

        point_cloud_data = vtk.vtkPolyData()
        point_cloud_data.SetPoints(points)
        point_cloud_data.GetPointData().SetScalars(values)
        point_cloud_data.GetPointData().SetActiveScalars('ValueArray')

        return point_cloud_data


    def _make_image_data(self, point_cloud_data, spacing=0.02):
        # triangulation by Delaunay method
        delny = vtk.vtkDelaunay3D()
        delny.SetInputData(point_cloud_data)
        delny.Update()
        unstructured_grid = delny.GetOutput()

        # 3D image probe
        bounds = point_cloud_data.GetBounds()
        probe = vtk.vtkImageData()
        # probe.SetOrigin(bounds[0], bounds[2], bounds[4])
        origin_value = min(bounds[0], bounds[2], bounds[4])
        probe.SetOrigin(origin_value, origin_value, origin_value)
        probe.SetSpacing(spacing, spacing, spacing)
        dim_val = max(
            math.ceil((bounds[1] - bounds[0])/spacing + 1),
            math.ceil((bounds[3] - bounds[2])/spacing + 1),
            math.ceil((bounds[5] - bounds[4])/spacing + 1),
        )
        probe.SetDimensions(dim_val, dim_val, dim_val)

        # set and activate log10 values
        wrapped_data = dsa.WrapDataObject(unstructured_grid)
        value_array = wrapped_data.PointData['ValueArray']
        log_value_array = np.log10(value_array)
        wrapped_data.PointData.append(log_value_array, 'log_ValueArray')

        # interpolation by vtkProbeFilter (linear interpolation)
        probe_filter = vtk.vtkProbeFilter()
        probe_filter.SetInputData(probe)
        probe_filter.SetSourceData(unstructured_grid)
        probe_filter.Update()
        image_data = probe_filter.GetOutput()

        # 10 raised to the power of interpolated values
        interpolated_data = dsa.WrapDataObject(image_data)
        is_valid_array = interpolated_data.PointData['vtkValidPointMask']
        log_interpolated_array = interpolated_data.PointData['log_ValueArray']
        interpolated_array = np.power(10, log_interpolated_array)
        interpolated_array[is_valid_array==0] = 0
        interpolated_data.PointData.append(interpolated_array, 'ValueArray')

        image_data.GetPointData().SetActiveScalars('ValueArray')

        return image_data
