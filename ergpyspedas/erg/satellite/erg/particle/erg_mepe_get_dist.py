
import logging
import numpy as np
from pytplot import get_data
from pyspedas import tnames

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
