from pytplot import tplot_names , get_data, get_timespan, store_data
from common.cotrans.erg_interpolate_att import erg_interpolate_att
from pyspedas.analysis.tnormalize import tnormalize
from orb.orb import orb
from common.cotrans.cart_trans_matrix_make import cart_trans_matrix_make
from pyspedas.utilities.time_string import time_string
from pyspedas.cotrans.cotrans import cotrans
from pyspedas.analysis.tcrossp import tcrossp

def dsi2j2000(name_in=None,
              name_out=None):

              if name_in == None or name_in not in tplot_names(quiet=True):
                  print('Input of Tplot name is undifiend')
                  return

              if name_out == None:
                  print('Tplot name for output is undifiend')
                  name_out = 'result_of_dsi2j2000'


