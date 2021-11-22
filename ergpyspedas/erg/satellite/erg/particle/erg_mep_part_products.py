import numpy as np
from pyspedas import tnames
from pyspedas.utilities.time_double import time_double
from pyspedas.utilities.time_string import time_string
from pyspedas.particles.spd_part_products.spd_pgs_make_e_spec import spd_pgs_make_e_spec
from pyspedas.particles.spd_part_products.spd_pgs_make_theta_spec import spd_pgs_make_theta_spec
from pyspedas.particles.spd_part_products.spd_pgs_progress_update import spd_pgs_progress_update
from pyspedas.particles.spd_part_products.spd_pgs_make_tplot import spd_pgs_make_tplot
from pytplot import get_timespan, get_data

from .erg_mepe_get_dist import erg_mepe_get_dist
from .erg_pgs_clean_data import erg_pgs_clean_data
from .erg_pgs_limit_range import erg_pgs_limit_range
from .erg_convert_flux_units import erg_convert_flux_units


def erg_mep_part_products(
    in_tvarname,
    species=None,
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
    energy=None,
    fac_type='mphism',
    trange=None,
    mag_name=None,
    pos_name=None,
    relativistic=False
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

    units_lc = units.lower()

    #  ;;Preserve the original time range
    tr_org = get_timespan(in_tvarname)

    if instnm == 'mepe':
        times_array = erg_mepe_get_dist(in_tvarname, species=species, units=units_lc, time_only=True)

    if trange is not None:
        
        trange_double = time_double(trange)
        time_indices = np.where((times_array >= trange_double[0]) \
                                & (times_array <= trange_double[1]))[0]
        
        if time_indices.shape[0] < 1:
            print(f'No ,{in_tvarname}, data for time range ,{time_string(trange_double)}')

    elif trange is None:
        time_indices = np.arange(times_array.shape[0])

    times_array = times_array[time_indices]



    dist = erg_mepe_get_dist(in_tvarname, 0, species=species, units=units_lc)
    if 'energy' in outputs_lc:
        out_energy = np.zeros((times_array.shape[0], dist['n_energy']))
        out_energy_y = np.zeros((times_array.shape[0], dist['n_energy']))
    if 'theta' in outputs_lc:
        out_theta = np.zeros((times_array.shape[0], dist['n_theta']))
        out_theta_y = np.zeros((times_array.shape[0], dist['n_theta']))

    last_update_time = None
    """
    ;;-------------------------------------------------
    ;; Loop over time to build spectrograms and/or moments
    ;;-------------------------------------------------
    """
    for index in range(time_indices.shape[0]):

        last_update_time = spd_pgs_progress_update(last_update_time=last_update_time,
             current_sample=index, total_samples=time_indices.shape[0], type_string=in_tvarname)

        #  ;; Get the data structure for this sample

        if instnm == 'mepe':

            dist = erg_mepe_get_dist(in_tvarname, time_indices[index], species=species, units=units_lc)

        clean_data = erg_pgs_clean_data(dist, units=units_lc,relativistic=relativistic)
        limited_data = erg_pgs_limit_range(clean_data, phi=phi_in, theta=theta, energy=energy)


        #  ;;Build theta spectrogram
        if 'theta' in outputs_lc:
            out_theta_y[index, :], out_theta[index, :] = spd_pgs_make_theta_spec(limited_data)

        #  ;;Build energy spectrogram
        if 'energy' in outputs_lc:
            out_energy_y[index, :], out_energy[index, :] = spd_pgs_make_e_spec(limited_data)

    if 'energy' in outputs_lc:
        spd_pgs_make_tplot(in_tvarname+'_energy' + suffix, x=times_array, y=out_energy_y, z=out_energy, units=units, ylog=True, ytitle=dist['data_name'] + ' \\ energy (eV)')

    if 'theta' in outputs_lc:
        spd_pgs_make_tplot(in_tvarname+'_theta' + suffix, x=times_array, y=out_theta_y, z=out_theta, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ theta (deg)')

