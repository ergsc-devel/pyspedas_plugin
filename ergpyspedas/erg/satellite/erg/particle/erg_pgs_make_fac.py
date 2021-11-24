import numpy as np

from pytplot import get_data, store_data

from pyspedas.cotrans.cotrans import cotrans
from pyspedas.analysis.tnormalize import tnormalize
from pyspedas.analysis.tcrossp import tcrossp

from ..common.cotrans.erg_cotrans import erg_cotrans

def erg_pgs_xgse(
    mag_temp,
    pos_tmp=None
):
    
    mag_data = get_data(mag_temp)

    # xaxis of this system is X of the gse system. Z is mag field
    x_axis = np.zeros((len(mag_data.times), 3))
    x_axis[:, 0] = 1
    
    store_data('xgse_pgs_temp', data={'x':mag_data[0], 'y':x_axis})
    cotrans('xgse_pgs_temp', name_out='xgse_pgs_temp',
            coord_in='gse', coord_out='j2000')
    erg_cotrans(in_name='xgse_pgs_temp', out_name='xgse_pgs_temp',
                in_coord='j2000', out_coord='dsi')
    
    # ;create orthonormal basis set
    z_basis = tnormalize(mag_temp, return_data=True)
    y_basis = tcrossp(z_basis, 'xgse_pgs_temp', return_data=True)
    y_basis = tnormalize(y_basis, return_data=True)
    x_basis = tcrossp(y_basis, z_basis, return_data=True)
    
    return (x_basis, y_basis, z_basis)