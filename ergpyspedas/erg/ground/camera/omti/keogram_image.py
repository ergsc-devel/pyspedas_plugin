from pytplot import get_data, store_data, tplot_names, options
import numpy as np


def keogram_image(v_name,
                  lat=60.0,
                  lon=240.0):
    """
    Create the keogram of image data at a specific location.

    @v_name: tplot variable of image data
    @lat: latitude to create a longitude-time plot of image data
    @lon: longitude to create a latitude-time plot of image data
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
    var_attrs = get_data(v_name, metadata=True)

    # ---Observation site (ABB code):
    site = str_tnames[2]

    # ---Wavelength:
    wavelength = str(float(str_tnames[3]) / 10.0)

    # ---Data level (raw or abs)
    level = str_tnames[5]

    # ---Mapping altitude [km]:
    altitude = str_tnames[-1]

    sg_lat = str(float(lat))
    sg_lon = str(float(lon))

    x_pos = var_attrs['pos'][0]
    y_pos = var_attrs['pos'][1]
    condition_lon = abs(x_pos - lon) == min(abs(x_pos - lon))
    condition_lat = abs(y_pos - lat) == min(abs(y_pos - lat))
    idx_lon = np.asarray(condition_lon).nonzero()[0]
    idx_lat = np.asarray(condition_lat).nonzero()[0]

    keogram_lon_time = ag_data[:, :, idx_lat[0]]
    keogram_lat_time = ag_data[:, idx_lon[0], :]

    # --------------- Preparation for setting tplot variables ----------------
    if var_attrs['z_title'] == 'deg':
        y_title_lat = \
            f'Station: {site.upper()}\nWavelength: {wavelength}\nSlice GLON: {sg_lon} [deg]\nGLAT [deg]'
        y_title_lon = \
            f'Station: {site.upper()}\nWavelength: {wavelength}\nSlice GLAT: {sg_lat} [deg]\nGLON [deg]'
    elif var_attrs['z_title'] == 'km':
        y_title_lat = \
            f'Station: {site.upper()}\nWavelength: {wavelength}\nZonal [km]'
        y_title_lon = \
            f'Station: {site.upper()}\nWavelength: {wavelength}\nMeridional [km]'
    else:
        y_title_lat = y_title_lon = ''

    if level == 'raw':
        z_title = 'Count'
    elif level == 'abs':
        z_title = 'Intensity [R]'
    else:
        z_title = ''

    if 'dev' in str_tnames:
        z_title = 'Normalized deviation'

    # ---Store tplot variable:
    keogram_lon_name = f'{v_name}_keogram_lon_{int(lon)}'
    keogram_lat_name = f'{v_name}_keogram_lat_{int(lat)}'
    store_data(keogram_lon_name,
               data={'x': times, 'y': keogram_lat_time, 'v': y_pos})
    options(keogram_lon_name, opt_dict={'spec': 1, 'ytitle': y_title_lat, 'ztitle': z_title})

    store_data(keogram_lat_name,
               data={'x': times, 'y': keogram_lon_time, 'v': x_pos})
    options(keogram_lat_name, opt_dict={'spec': 1, 'ytitle': y_title_lon, 'ztitle': z_title})
