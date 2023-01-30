import sys

from PySide6 import QtWidgets

from .window.main_window import MainWindow
from .isee3d_config import CONFIG

def isee3d(dists, mag_vn, vel_vn, colormap_name=None, save_image_dir=None):
    '''
    Visualize three-dimensional plasma velocity and energy distributions

    Parameters:
        dists: dict
            Information extracted from a tplot variable by get_dist function.

        mag_vn: str
            The tplot variable name for magnetic field data.

        vel_vn: str
            The tplot variable name for velocity data.

        colormap_name: str
            Colormap name used for visualization. 'spedas' or names in matplotlib are available.

        save_image_dir: str
            Directory where images will be saved.

    '''
    if colormap_name is not None:
        CONFIG['colormap_name'] = colormap_name
    if save_image_dir is not None:
        CONFIG['save_image_dir'] = save_image_dir

    app = QtWidgets.QApplication()
    window = MainWindow(dists, mag_vn, vel_vn, CONFIG)
    window.show()
    window.vtkWidget.render_window_interactor.Initialize()
    sys.exit(app.exec_())
