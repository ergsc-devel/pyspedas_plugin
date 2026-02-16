
from ergpyspedas.erg import mgf, orb
mgf()
orb()
from pyspedas import tplot_options, options, tplot_names, split_vec, get_data, tnames
from pyspedas.tplot_tools import tplot_opt_glob

split_vec('erg_orb_l2_pos_rmlatmlt')
split_vec('erg_orb_l2_pos_Lm')
options('erg_orb_l2_pos_rmlatmlt_x', 'ytitle', 'R')
options('erg_orb_l2_pos_rmlatmlt_y', 'ytitle', 'Mlat')
options('erg_orb_l2_pos_rmlatmlt_z', 'ytitle', 'MLT')

var_label=['erg_orb_l2_pos_Lm_x', 'erg_orb_l2_pos_rmlatmlt_x','erg_orb_l2_pos_rmlatmlt_y','erg_orb_l2_pos_rmlatmlt_z']
#tplot_options('var_label', var_label)

plot_vars=['erg_mgf_l2_mag_8sec_sm','erg_mgf_l2_igrf_8sec_sm','erg_orb_l2_pos_Lm_x']

from ergpyspedas.util import tplot_vl
fig = tplot_vl(plot_vars)

