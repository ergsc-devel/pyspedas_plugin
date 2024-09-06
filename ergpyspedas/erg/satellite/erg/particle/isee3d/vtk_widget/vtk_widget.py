from PIL import Image

import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.numpy_interface import dataset_adapter as dsa

from PySide6 import QtWidgets
import pyspedas

from .draw import draw_all
from ..isee3d_property import Isee3dProperty
from ..data_manager import DataManager

# ignore vtk warning in vtk.vtkDelaunay3D(): degenerate triangles encountered, mesh quality suspect
vtk.vtkObject.GlobalWarningDisplayOff()


class VtkWidget(QVTKRenderWindowInteractor, QtWidgets.QWidget):
    def __init__(self,centralwidget, dists, mag_vn, vel_vn, colormap_name):
        super(VtkWidget,self).__init__(centralwidget)

        self._colormap_name = colormap_name

        self.renderer = vtk.vtkRenderer()
        background_color = vtk.vtkNamedColors().GetColor3d("white")
        self.renderer.SetBackground(background_color)

        self.camera = self.renderer.GetActiveCamera()
        self.camera.ParallelProjectionOn()
        # default
        self.camera.Roll(30)
        self.camera.Elevation(-60)

        self.render_window = self.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)

        self.render_window_interactor = self.render_window.GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        style.AddObserver("CharEvent", lambda x, y: None)
        style.AddObserver("RightButtonPressEvent", lambda x, y: None)
        style.AddObserver("RightButtonReleaseEvent", lambda x, y: None)
        self.render_window_interactor.SetInteractorStyle(style)

        self.data_manager = None
        self.draw_property = None
        self.draw_data = None
        self.first_data_time = None
        self.last_data_time = None
        self.setup(dists, mag_vn, vel_vn)

    def setup(self, dists, mag_vn, vel_vn):
        first_data_time = pyspedas.utilities.time_string.time_string(dists['time'][0])
        last_data_time = pyspedas.utilities.time_string.time_string(dists['time'][-1])

        data_manager = DataManager(dists, mag_vn, vel_vn)
        data_manager.setup()
        draw_property = Isee3dProperty(data_manager.max_mag_squared_length,
                                       data_manager.max_vel_squared_length,
                                       self._colormap_name)
        draw_data = data_manager.make_draw_data(draw_property.data)
        draw_property.setup(draw_data)

        draw_all(draw_property, draw_data, self.renderer)

        self.data_manager = data_manager
        self.draw_property = draw_property
        self.draw_data = draw_data
        self.first_data_time = first_data_time
        self.last_data_time = last_data_time
    
    def update_data(self):
        self.draw_data = self.data_manager.make_draw_data(self.draw_property.data)
        self.draw_property.setup(self.draw_data)

    def update_draw(self):
        self.renderer.RemoveAllViewProps()
        draw_all(self.draw_property, self.draw_data, self.renderer)
        self.render_window.Render()

    def save_png_image(self, save_path):
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.render_window)
        w2if.SetInputBufferTypeToRGB()
        w2if.ReadFrontBufferOff()
        w2if.Update()

        writer = vtk.vtkPNGWriter()
        writer.SetFileName(save_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

    def save_eps_image(self, save_path):
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.render_window)
        w2if.SetInputBufferTypeToRGB()
        w2if.ReadFrontBufferOff()
        w2if.Update()

        image_data = w2if.GetOutput()
        width, height, _ = image_data.GetDimensions()
        wrapped_data = dsa.WrapDataObject(w2if.GetOutput())
        serial_data = wrapped_data.PointData['ImageScalars']
        image_numpy = serial_data.reshape([height, width, -1])
        image_pil = Image.fromarray(image_numpy[::-1])
        image_pil = image_pil.convert('RGB')
        image_pil.save(save_path, lossless=True)
