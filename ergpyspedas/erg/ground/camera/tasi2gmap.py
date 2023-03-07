from pytplot import tplot_names, get_data, store_data
import numpy as np

from datetime import datetime


def tasi2gmap(
    v_name1,
    v_name2
    ):
    """
    Create the image data in geographic coordinates, and store tplot variable.

    @vname1: tplot variable of airgrow data
    @vname2: tplot variable of map table data
    """

    # ---Get data from two tplot variables:
    if (v_name1 not in tplot_names()) or (v_name2 not in tplot_names()):
        print('Cannot find the tplot var in argument!')
        return

    times, ag_data = get_data(v_name1)  # --- for airglow image data:
    var_attrs = get_data(v_name1, metadata=True)
    map_table_data = get_data(v_name2)[()]  # --- for map table data:
    map_unit = map_table_data['z_title']

    # ---Get the information of tplot name:
    str_tnames = v_name2.split('_')

    # ---Mapping altitude [km]:
    altitude = str_tnames[6]

    # ---Definition of parameters for convert loop:
    # ---Map saize from pos array size:
    map_size = len(map_table_data['pos'][0])

    # ---Array of image data in geographic coordinates:
    image_gmap = np.zeros((len(times), map_size, map_size), dtype=float)

    # ---Convert loop in geographic coordinates:
    for i in range(len(times)):
        current_time = datetime.utcfromtimestamp(times[i]).strftime('%Y-%m-%d / %H:%M:%S')
        print(f'now converting... : {current_time}')
        z_values = np.flip(ag_data[i], 0)
        img_t = np.transpose(z_values)
        image_gmap[i] = img_t[(map_table_data['map'][0], map_table_data['map'][1])]

    # ---Store tplot variable:
    var_attrs['pos'] = map_table_data['pos']
    var_attrs['z_title'] = map_unit
    store_data(f'{v_name1}_gmap_{str(int(altitude))}',
               data={'x': times, 'y': image_gmap},
               attr_dict=var_attrs)
