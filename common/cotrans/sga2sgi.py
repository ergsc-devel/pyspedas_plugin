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

            get_data_vars = get_data(name_in)
            dl_in = get_data(name_in, metadata=True)
            time = get_data_vars[0]
            time_length = time.shape[0]
            dat = get_data_vars[1]

            #Get the SGA and SGI axes by interpolating the attitude data
            interpolated_values = erg_interpolate_att(name_in, noload=noload)
            sgix = interpolated_values['sgix_j2000']['y']
            sgiy = interpolated_values['sgiy_j2000']['y']
            sgiz = interpolated_values['sgiz_j2000']['y']
            sgax = interpolated_values['sgax_j2000']['y']
            sgay = interpolated_values['sgay_j2000']['y']
            sgaz = interpolated_values['sgaz_j2000']['y']

            if not SGI2SGA:
                print('SGA --> SGI')
                coord_out = 'sgi'

            else:
                print('SGI --> SGA')
                coord_out = 'sga'

                
