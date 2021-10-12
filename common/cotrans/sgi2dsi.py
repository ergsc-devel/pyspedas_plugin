import numpy as np
from pytplot import get_data, tplot_names
from common.cotrans.erg_interpolate_att import erg_interpolate_att

def sgi2dsi(name_in=None,
            name_out=None,
            DSI2SGI=False,
            noload=False):

            if name_in == None or name_in not in tplot_names(quiet=True):
                print('Input of Tplot name is undifiend')
                return

            if name_out == None:
                print('Tplot name for output is undifiend')
                name_out = 'result_of_dsi2j2000'

            # prepare for transformed Tplot Variable
            reload = not noload
            dl_in = get_data(name_in, metadata=True)
            get_data_array = get_data(name_in)
            time = get_data_array[0]
            time_length = time.shape[0]
            dat = get_data_array[1]