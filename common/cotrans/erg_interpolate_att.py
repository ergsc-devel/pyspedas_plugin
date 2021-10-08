import numpy as np
import pyspedas
import pytplot
from pytplot.tplot_math.degap import degap
from att.att import att
from pyspedas.utilities.time_string import time_string


def erg_interpolate_att(erg_xxx_in = None):

    if erg_xxx_in == None or erg_xxx_in not in pyspedas.tnames():
        print(f'{erg_xxx_in} is None, or not defined')
        return
