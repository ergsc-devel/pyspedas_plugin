
import logging
import numpy as np
from pytplot import get_data
from pyspedas import tnames

logging.captureWarnings(True)
logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


def erg_mepe_get_dist(tname,
                      index,
                      units='flux',
                      level = 'l2'):
    
    if len(tnames(tname)) > 0:
        input_name = tnames(tname)[0]
    else:
        print(f'Variable: {tname} not found!')
        return

    