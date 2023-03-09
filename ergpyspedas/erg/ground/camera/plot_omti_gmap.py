from pytplot import get_data, tplot_names, spedas_colorbar
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_omti_gmap(
    v_name,
    time=None,
    x_min=None,
    x_max=None,
    y_min=None,
    y_max=None,
    z_min=None,
    z_max=None,
    cmap=None,
    factor=1
    ):
    """
    Create the two-dimensional map of image data in geographic coordinates.
    
    @vname: tplot variable of image data
    @time: plot time. The default is start time of tplot variable
    @x_min: minimum value of x range. The default is the minimum value of image size
    @x_max: maximum value of x range. The default is the maximum value of image size
    @y_min: minimum value of y range. The default is the minimum value of image size
    @y_max: maximum value of y range. The default is the maximum value of image size
    @z_min: minimum value of z range. The default is the minimum value of image data
    @z_max: maximum value of z range. The default is the maximum value of image data   
    """

    # ---Get data from tplot variable
    if v_name not in tplot_names():
        print('Cannot find the tplot var in argument!')
        return

    # ---Get the ABB code and mapping altitude from tplot name:
    str_tnames = v_name.split('_')
    if len(str_tnames) < 8:
        print('Wrong tplot variable.')
        return

    times, ag_data = get_data(v_name)
    img_attrs = get_data(v_name, metadata=True)

    # ---Observation site (ABB code):
    site = str_tnames[2]

    # ---Wavelength:
    wavelength = str(float(str_tnames[3]) / 10.0)

    # ---Data level (raw or abs)
    level = str_tnames[5]

    # ---Mapping altitude [km]:
    altitude = str_tnames[-1]

    # --------------- Preparation for Plotting ----------------
    # ---Find the array number of image data corresponding to the input time:
    if time is None:
        time = str(times[0])

    condition = abs(times - float(time)) == min(abs(times - float(time)))
    idx = np.asarray(condition).nonzero()[0]

    if len(idx) == 0:
        print('Out of time range')
        return

    # ---Set the plot range of x, y, and z axes:
    x_pos = img_attrs['pos'][0]
    y_pos = img_attrs['pos'][1]

    if x_min is None:
        x_min = np.amin(x_pos)
    if x_max is None:
        x_max = np.amax(x_pos)

    if y_min is None:
        y_min = np.amin(y_pos)
    if y_max is None:
        y_max = np.amax(y_pos)

    if z_min is None:
        z_min = np.amin(ag_data[idx[0]])
    if z_max is None:
        z_max = np.amax(ag_data[idx[0]])

    x_idx = np.where((x_pos >= x_min) & (x_pos <= x_max))
    y_idx = np.where((y_pos >= y_min) & (y_pos <= y_max))
    x_idx_range, y_idx_range = np.meshgrid(x_idx, y_idx)
    x_values = x_pos[x_idx]
    y_values = y_pos[y_idx]
    z_values = np.transpose(ag_data[idx[0]])
    z_range = z_values[y_idx_range, x_idx_range]
    current_time = datetime.utcfromtimestamp(times[idx[0]]).strftime('%Y-%m-%d / %H:%M:%S')

    # ---Set the plot range of x, y, and z axes:
    if img_attrs['z_title'] == 'deg':
        x_title = 'GLON [deg]'
        y_title = 'GLAT [deg]'
    elif img_attrs['z_title'] == 'km':
        x_title = 'Zonal [km]'
        y_title = 'Meridional [km]'
    else:
        x_title = ''
        y_title = ''

    if level == 'raw':
        z_title = 'Count'
    elif level == 'abs':
        z_title = 'Intensity [R]'
    else:
        z_title = ''

    if 'dev' in str_tnames:
        z_title = 'Normalized deviation'

    # --- Set 'spedas' colormap
    if cmap is None:
        _colors = spedas_colorbar
        spd_map = [(np.array([r, g, b])).astype(np.float64) / 256
                   for r, g, b in zip(_colors.r, _colors.g, _colors.b)]
        cmap = LinearSegmentedColormap.from_list('spedas', spd_map)

    # ---Plot the image data in geographic coordinates:
    fig, ax = plt.subplots()
    im = ax.pcolormesh(x_values, y_values, z_range,
                       clim=(z_min, z_max), cmap=cmap, shading='nearest')
    plt.xlabel(x_title)
    plt.ylabel(y_title)

    ax.set_aspect('equal', 'box')
    divider = make_axes_locatable(ax)
    cax1 = divider.append_axes("right", size=0.21, pad=0.3)
    fig.colorbar(im, cax=cax1, label=z_title)
    fig.subplots_adjust(top=0.85)

    # ---Add the plot legends:
    fig.text(x=0.5, y=0.86, s=str(current_time), ha='center')
    fig.text(x=0.5, y=0.895, s=f'Mapping altitude: {altitude} [km]', ha='center')
    fig.text(x=0.5, y=0.93, s=f'Wavelength: {wavelength} [nm]', ha='center')
    fig.text(x=0.5, y=0.965, s=f'Station: {site.upper()}', ha='center')

    # --- Rescale the figure (if any)
    if factor != 1:
        fig_size = fig.get_size_inches()
        fig.set_size_inches(factor * fig_size)

    # ---Show the image:
    plt.show()
