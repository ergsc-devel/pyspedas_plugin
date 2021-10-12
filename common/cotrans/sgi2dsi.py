import numpy as np
from pytplot import get_data
from common.cotrans.erg_interpolate_att import erg_interpolate_att

def sgi2dsi(name_in=None,
            name_out=None,
            no_orb=False,
            DSI2SGI=False,
            noload=False):
            