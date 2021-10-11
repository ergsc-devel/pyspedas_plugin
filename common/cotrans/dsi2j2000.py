from pytplot import tplot_names , get_data, get_timespan, store_data
from common.cotrans.erg_interpolate_att import erg_interpolate_att
from pyspedas.analysis.tnormalize import tnormalize
from orb.orb import orb
from common.cotrans.cart_trans_matrix_make import cart_trans_matrix_make
from pyspedas.utilities.time_string import time_string
from pyspedas.cotrans.cotrans import cotrans
from pyspedas.analysis.tcrossp import tcrossp
import numpy as np

def dsi2j2000(name_in=None,
              name_out=None,
              no_orb=False):

            if name_in == None or name_in not in tplot_names(quiet=True):
                print('Input of Tplot name is undifiend')
                return

            if name_out == None:
                print('Tplot name for output is undifiend')
                name_out = 'result_of_dsi2j2000'

            # prepare for transformed Tplot Variable
            dl_in = get_data(name_in, metadata=True)
            get_data_array = get_data(name_in)
            time = get_data_array[0]
            time_length = time.shape[0]
            dat = get_data_array[1]


            #Get the SGI axis by interpolating the attitude data
            dsiz_j2000 = erg_interpolate_att(name_in)['sgiz_j2000']


            #Sun direction in J2000
            sundir=np.array([[1., 0., 0.]]*time_length)

            if no_orb:
                store_data('sundir_gse',data={'x':time, 'y':sundir})

            else: #Calculate the sun directions from the instantaneous satellite locations 
                tr = get_timespan(name_in)
                orb(trange=time_string([tr[0] -60., tr[1] + 60.]))
                get_data_erg_orb_l2 = get_data('erg_orb_l2_pos_gse')
                scpos_x = np.interp(time, get_data_erg_orb_l2[0], get_data_erg_orb_l2[1][:,0])
                scpos_y = np.interp(time, get_data_erg_orb_l2[0], get_data_erg_orb_l2[1][:,1])
                scpos_z = np.interp(time, get_data_erg_orb_l2[0], get_data_erg_orb_l2[1][:,2])
                scpos = np.array([scpos_x,scpos_y,scpos_z]).T
                sunpos=np.array([[1.496e+08, 0., 0.]]*time.shape[0])
                sundir = sunpos - scpos
                store_data('sundir_gse', data={ 'x':time, 'y':sundir } )
                tnormalize('sundir_gse', newname='sundir_gse')



