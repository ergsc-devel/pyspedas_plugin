
import logging
import numpy as np

from pytplot import get_data
from pyspedas import tnames
from scipy import interpolate

from pyspedas.utilities.time_double import time_double
from pyspedas.utilities.time_string import time_string

logging.captureWarnings(True)
logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


def erg_mepe_get_dist(tname,
                      index=None,
                      units='flux',
                      level = 'l2',
                      species = 'e',
                      time_only=False,
                      single_time=None,
                      trange=None):
    
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
        n_times = index.size
    else:
        # index supersedes time range
        if index is None:
            if trange is not None:
                trange_double_array = np.array(time_double(trange))
                trange_minmax = np.array([trange_double_array.min(),
                                          trange_double_array.max()])
                index = np.where((data_in[0] >= trange_minmax[0])
                                 & (data_in[0] <= trange_minmax[1]))[0]
                n_times = index.size
                if n_times == 0:
                    print('No data in time range: ' \
                        + ' '.join(time_string(trange_minmax)))
                    return 0
            else:
                n_times = data_in[0].size
                index = np.arange(n_times)
        else:
            n_times = np.array([index]).size

    """
    ;; --------------------------------------------------------------

    ;; MEPe data arr: [9550(time), 32(spin phase), 16(energy), 16(apd)]
    ;; Dimensions
    """

    dim_array = np.array(data_in[1].shape[1:])[[1, 0, 2]]
    n_sp = dim_array[1]  # ;; # of spin phases in 1 spin

    if species.lower() == 'e':
        mass = 5.68566e-06
        charge = -1.
        data_name = 'MEP-e Electron 3dflux'
        integ_time = 7.99 / 32 / 16 #  ;; currently hard-coded
    else:
        print('given species is not supported by this routine.')
        return 0

    #  ;; basic template structure compatible with other routines

    dist_template = {
        'project_name': 'ERG',
        'spacecraft': 1,  # always 1 as a dummy value
        'data_name': data_name,
        'units_name': 'flux',  #   MEP-e data in [/keV-s-sr-cm2] should be converted to [/eV-s-sr-cm2] 
        'units_procedure': 'erg_convert_flux_units',
        'species': species,
        'valid': 1,
        
        'charge': charge,
        'mass': mass,
        'time': 0,
        'end_time': 0,
        
        'data': np.zeros(shape=dim_array),
        'bins': np.ones(shape=dim_array, dtype='int8'),  # must be set or data will be consider invalid
        
        'energy': np.zeros(shape=dim_array),  #  should be in eV
        'denergy':  np.zeros(shape=dim_array),
        'nenergy': dim_array[0],  #   # of energy chs
        'nbins': dim_array[1] * dim_array[2],   #  # thetas * # phis
        'phi': np.zeros(shape=dim_array),
        'dphi': np.zeros(shape=dim_array),
        'theta': np.zeros(shape=dim_array),
        'dtheta': np.zeros(shape=dim_array),
    }
