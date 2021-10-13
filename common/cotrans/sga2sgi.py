import numpy as np
from pytplot import get_data, tplot_names, store_data
from common.cotrans.erg_interpolate_att import erg_interpolate_att

def sga2sgi(name_in=None,
            name_out=None,
            SGI2SGA=False,
            noload=False):

