import numpy as np
from pyspedas import tnames
from pyspedas.particles.spd_part_products.spd_pgs_make_e_spec import spd_pgs_make_e_spec
from pyspedas.particles.spd_part_products.spd_pgs_make_theta_spec import spd_pgs_make_theta_spec
from pyspedas.particles.spd_part_products.spd_pgs_progress_update import spd_pgs_progress_update
from pytplot import get_data

from .erg_pgs_clean_data import erg_pgs_clean_data
from .erg_pgs_limit_range import erg_pgs_limit_range
from .erg_convert_flux_units import erg_convert_flux_units


def erg_mep_part_products(
    in_tvarname,
    spiecies=None,
    outputs=['energy'],
    no_ang_weighting=False,
    suffix='',
    units='flux',
    datagap=16.1,
    regrid=[32, 16],
    pitch=[0., 180.],
    theta=[-90., 90.],
    phi_in=[0., 360.],
    gyro=[0., 360.],
    fac_type='mphism',
    trange=None,
    mag_name=None,
    pos_name=None
    ):

    if len(tnames(in_tvarname)) < 1:
        print('No input data, please specify tplot variable!')
        return 0

    in_tvarname = tnames(in_tvarname)[0]
    instnm = in_tvarname.split('_')[1]  #  ;; mepe or mepi

    if isinstance(outputs, str):
        outputs_lc = outputs.lower()
        outputs_lc = outputs_lc.split(' ')
    elif isinstance(outputs, list):
        outputs_lc = []
        for output in outputs:
            outputs_lc.append(output.lower())
