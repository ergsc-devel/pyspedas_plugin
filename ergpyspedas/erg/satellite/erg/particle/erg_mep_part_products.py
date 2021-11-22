import numpy as np
from pyspedas import tnames
from pyspedas.particles.spd_part_products.spd_pgs_make_e_spec import spd_pgs_make_e_spec
from pytplot import get_data

from .erg_pgs_clean_data import erg_pgs_clean_data
from .erg_pgs_limit_range import erg_pgs_limit_range
from .erg_convert_flux_units import erg_convert_flux_units


def erg_mep_part_products(
    in_tvarname,
    spiecies=None,
    outputs=['energy'],
    no_ang_weighting=False
    ):

