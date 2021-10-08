import numpy as np
#import pyspedas
from pyspedas import tnames
#import pytplot
from pytplot import get_data, get_timespan
from pytplot.tplot_math.degap import degap
from att.att import att
from pyspedas.utilities.time_string import time_string


def erg_interpolate_att(erg_xxx_in = None):

    if erg_xxx_in == None or erg_xxx_in not in tnames():
        print('inputted Tplot variable name is None, or not defined')
        return

    time = get_data(erg_xxx_in)[0]

    # Prepare some constants
    dtor = np.pi

    output_dictionary = {}

    #Load the attitude data 
    if tnames('erg_att_sprate') == ['erg_att_sprate']:
        degap('erg_att_sprate',dt=8., margin=.5)
        sprate=get_data('erg_att_sprate')
        if sprate[0].min() > time.min() + 8. or sprate[0].max() < time.max() - 8.:
            tr = get_timespan(erg_xxx_in)
            att(trange=[time_string([tr[0] -60., tr[1] + 60.])])
    else:
        tr = get_timespan(erg_xxx_in)
        att(trange=time_string([tr[0] -60., tr[1] + 60.]))

    #Interpolate spin period 
    degap('erg_att_sprate',dt=8., margin=.5)
    sprate=get_data('erg_att_sprate')
    sper = 1./ (sprate[1] / 60.)
    sperInterp = np.interp(time, sprate[0], sper)
    spinperiod = {'x': time, 'y': sperInterp}
    output_dictionary['spinperiod'] = spinperiod

    return output_dictionary