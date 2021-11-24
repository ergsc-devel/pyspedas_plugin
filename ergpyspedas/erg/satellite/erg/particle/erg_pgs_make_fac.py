import numpy as np

from pytplot import get_data, store_data, tplot_copy

from pyspedas.cotrans.cotrans import cotrans
from pyspedas.analysis.tnormalize import tnormalize
from pyspedas.analysis.tcrossp import tcrossp
from pyspedas.analysis.tinterpol import tinterpol

from ..common.cotrans.erg_cotrans import erg_cotrans

# ;so we don't have one long routine of doom, all transforms should be separate helper functions
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

# ;so we don't have one long routine of doom, all transforms should be separate helper functions
def erg_pgs_phigeo(
    mag_temp,
    pos_temp
):
    
    postmp = 'pos_pgs_temp'
    tplot_copy(pos_temp, postmp)
    cotrans(postmp, postmp, coord_in='gse', coord_out='geo')
    pos_data = get_data(postmp)
    
    # transformation to generate other_dim dim for phigeo from thm_fac_matrix_make
    # All the conversions to polar and trig simplifies to this.
    # But the reason the conversion is why this is the conversion that is done, is lost on me.
    # The conversion swaps the x & y components of position, reflects over x=0,z=0 then projects into the xy plane
    pos_conv = np.stack((-pos_data.y[:, 1], pos_data.y[:, 0], np.zeros(len(pos_data.times))))
    pos_conv = np.transpose(pos_conv, [1, 0])
    store_data(postmp, data={'x': pos_data.times, 'y': pos_conv})

    # ;transform into dsl because particles are in dmpa
    cotrans(postmp,postmp,coord_in='geo', coord_out='j2000')
    erg_cotrans(postmp,postmp,in_coord='j2000', out_coord='dsi')
    
    # ;create orthonormal basis set
    z_basis = tnormalize(mag_temp, return_data=True)
    tinterpol(postmp,mag_temp, newname=postmp)
    x_basis = tcrossp(postmp,z_basis, return_data=True)
    x_basis = tnormalize(x_basis, return_data=True)
    y_basis = tcrossp(z_basis, x_basis, return_data=True)

    return (x_basis, y_basis, z_basis)

# ;so we don't have one long routine of doom, all transforms should be separate helper functions
def erg_pgs_mphigeo(
    mag_temp,
    pos_temp
):
    
    postmp = 'pos_pgs_temp'
    tplot_copy(pos_temp, postmp)
    cotrans(postmp, postmp, coord_in='gse', coord_out='geo')
    pos_data = get_data(postmp)

    # the following is heisted from the IDL version
    # transformation to generate other_dim dim for mphigeo from thm_fac_matrix_make
    # All the conversions to polar and trig simplifies to this.  
    # But the reason the conversion is why this is the conversion that is done, is lost on me.
    # The conversion swaps the x & y components of position, reflects over x=0,z=0 then projects into the xy plane
    pos_conv = np.stack((pos_data.y[:, 1], -pos_data.y[:, 0], np.zeros(len(pos_data.times))))
    pos_conv = np.transpose(pos_conv, [1, 0])
    store_data(pos_temp, data={'x': pos_data.times, 'y': pos_conv})
    
    # ;transform into dsl because particles are in dmpa
    cotrans(postmp,postmp,coord_in='geo', coord_out='j2000')
    erg_cotrans(postmp,postmp,in_coord='j2000', out_coord='dsi')
    
    # ;create orthonormal basis set
    z_basis = tnormalize(mag_temp, return_data=True)
    tinterpol(postmp,mag_temp, newname=postmp)
    x_basis = tcrossp(z_basis, postmp, return_data=True)
    x_basis = tnormalize(x_basis, return_data=True)
    y_basis = tcrossp(z_basis, x_basis, return_data=True)
    
    return (x_basis, y_basis, z_basis)
