import numpy as np
from pytplot import get_data, tplot_names, store_data
from common.cotrans.erg_interpolate_att import erg_interpolate_att
from common.cotrans.cart_trans_matrix_make import cart_trans_matrix_make

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

                #Transform SGI-X,Y,Z axis unit vectors in J2000 to those in SGA 
                mat = cart_trans_matrix_make(sgax, sgay, sgaz)
                sgix_in_sga = np.array([np.dot(mat[i,:,:],sgix[i,:]) for i in range(time_length)])
                sgiy_in_sga = np.array([np.dot(mat[i,:,:],sgiy[i,:]) for i in range(time_length)])
                sgiz_in_sga = np.array([np.dot(mat[i,:,:],sgiz[i,:]) for i in range(time_length)])

                #Now transform the given vector in SGA to those in SGI
                mat = cart_trans_matrix_make(sgix_in_sga, sgiy_in_sga, sgiz_in_sga)
                dat_new = np.array([np.dot(mat[i,:,:],dat[i,:]) for i in range(time_length)])


            else:
                print('SGI --> SGA')
                coord_out = 'sga'

                #Transform SGA-X,Y,Z axis unit vectors in J2000 to those in SGI
                mat = cart_trans_matrix_make(sgix, sgiy, sgiz)
                sgax_in_sgi = np.array([np.dot(mat[i,:,:],sgax[i,:]) for i in range(time_length)])
                sgay_in_sgi = np.array([np.dot(mat[i,:,:],sgay[i,:]) for i in range(time_length)])
                sgaz_in_sgi = np.array([np.dot(mat[i,:,:],sgaz[i,:]) for i in range(time_length)])

                #Now transform the given vector in SGI to those in SGA
                mat = cart_trans_matrix_make(sgax_in_sgi, sgay_in_sgi, sgaz_in_sgi)
                dat_new = np.array([np.dot(mat[i,:,:],dat[i,:]) for i in range(time_length)])

            #Store the converted data in a tplot variable 
            store_data(name_out, data={'x':time, 'y':dat_new}, attr_dict=dl_in)