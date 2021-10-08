import numpy as np
#import pyspedas
from pyspedas import tnames
#import pytplot
from pytplot import get_data
from pytplot.tplot_math.degap import degap
from att.att import att
from pyspedas.utilities.time_string import time_string


def erg_interpolate_att(erg_xxx_in = None):

    if erg_xxx_in == None or erg_xxx_in not in tnames():
        print(f'{erg_xxx_in} is None, or not defined')
        return

    time = get_data(erg_xxx_in)

    # Prepare some constants
    dtor = np.pi

