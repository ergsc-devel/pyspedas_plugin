from pytplot import tplot_names, get_data, store_data
import numpy as np


def tmake_image_dev(
    v_name, 
    width=3600.
    ):
    """
    Calculates the deviation of image data from 1-hour average data and store tplot variable.
    
    @v_name: tplot variable of image data
    @width: Period of data window to calculate the average value. The default is 3600 sec.
    """
    # ---Get data from tplot variable with image data:
    if v_name not in tplot_names():
        print('Cannot find the tplot var in argument!')
        return

    times, ag_data = get_data(v_name)
    var_attrs = get_data(v_name, metadata=True)

    # ---Definition of arrays for deviation and average data:
    # ---Map size:
    map_size = len(ag_data[0][:][0])

    # ---Set average period (1-hr period is default):
    h = width

    # ---Init deviation from average image data array:
    dev = np.zeros((len(times), map_size, map_size), dtype=float)

    for i in range(len(times)):

        # ---Init an array used in average calculations:
        avg = np.zeros((map_size, map_size), dtype=float)

        # ---Search time indexes where time is from t-width/2 to t+width/2 [sec]:
        idx = np.where((times >= times[i] - h / 2) & (times <= times[i] + h / 2))[0]
        if len(idx) != 0:

            # ---Sum up the image data within a time rage from t-width/2 to t+width/2 [sec]:
            for j in range(len(idx)):
                avg += ag_data[idx[j]]

            # ---Average data:
            avg /= len(idx)

            # ---Replace zero value of average data by 1.0 to use normalization:
            den_avg = np.copy(avg)
            idx_avg = np.where(den_avg == 0.)
            den_avg[idx_avg] = 1.

            # ---Calculate normalized deviation of image data:
            dev[i] = (ag_data[i] - avg) / den_avg
            dev[i] -= np.nanmean(dev[i])

    # ---Store new tplot variable with '_dev' in its name:
    store_data(f'{v_name}_dev', data={'x': times, 'y': dev}, attr_dict=var_attrs)
