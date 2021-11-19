
import logging
import numpy as np

from pytplot import get_data
from pyspedas import tnames
from scipy import interpolate

from pyspedas.utilities.time_double import time_double

logging.captureWarnings(True)
logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


def erg_mepe_get_dist(tname,
                      index,
                      units='flux',
                      level = 'l2',
                      species = 'e',
                      time_only=False,
                      single_time=None):
    
    if len(tnames(tname)) > 0:
        input_name = tnames(tname)[0]
    else:
        print(f'Variable: {tname} not found!')
        return 0

    level = level.lower()
    """
    ;; Extract some information from a tplot variable name
    ;; e.g., erg_mepe_l2_3dflux_FEDU
    """

    vn_info = input_name.split('_')
    instrument = vn_info[1]
    level = vn_info[2]
    vn_spph = '_'.join(vn_info[0:4]) + '_spin_phase'

    if instrument == 'mepe':
        species = 'e'
    else:
        print(f'ERROR: given an invalid tplot variable: {input_name}')
        return 0

    # ;; Get a reference to data and metadata

    data_in = get_data(input_name)
    data_in_metadata = get_data(input_name, metadata=True)

    if data_in is None:
        print('Problem extracting the mepe 3dflux data.')
        return 0

    # ;; Return time labels
    if time_only:
        return data_in[0]

    if single_time is not None:
        single_time_double = time_double(single_time)
        if (data_in[0][0] <= single_time_double)\
        and (single_time_double <= data_in[0][-1]):
            nearest_time = interpolate.interp1d(data_in[0], data_in[0],
                        kind="nearest")(single_time_double)
        elif (single_time_double < data_in[0][0])\
        or (data_in[0][-1] < single_time_double):
            nearest_time = interpolate.interp1d(data_in[0], data_in[0],
                        kind="nearest", fill_value='extrapolate')\
                            (single_time_double)
        index = np.where(data_in[0] == nearest_time)[0]
        n_times = index.shape[0]
