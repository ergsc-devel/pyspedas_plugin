import numpy as np
from pytplot import get_data, tplot_names, store_data
from common.cotrans.erg_interpolate_att import erg_interpolate_att

def sga2sgi(name_in=None,
            name_out=None,
            SGI2SGA=False,
            noload=False):

            if name_in == None or name_in not in tplot_names(quiet=True):
                print('Input of Tplot name is undifiend')
                return

            if name_out == None:
                print('Tplot name for output is undifiend')
                name_out = 'result_of_sga2sgi'

