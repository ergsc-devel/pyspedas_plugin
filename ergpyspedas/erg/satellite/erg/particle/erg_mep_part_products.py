import numpy as np
from pyspedas import tnames, tinterpol
from pyspedas.utilities.time_double import time_double
from pyspedas.utilities.time_string import time_string
from pyspedas.particles.spd_part_products.spd_pgs_make_e_spec import spd_pgs_make_e_spec
from pyspedas.particles.spd_part_products.spd_pgs_make_theta_spec import spd_pgs_make_theta_spec
from pyspedas.particles.spd_part_products.spd_pgs_make_phi_spec import spd_pgs_make_phi_spec
from pyspedas.particles.spd_part_products.spd_pgs_progress_update import spd_pgs_progress_update
from pyspedas.particles.spd_part_products.spd_pgs_make_tplot import spd_pgs_make_tplot
from pyspedas.particles.spd_part_products.spd_pgs_do_fac import spd_pgs_do_fac
from pyspedas.particles.moments.spd_pgs_moments import spd_pgs_moments
from pyspedas.particles.spd_part_products.spd_pgs_regrid import spd_pgs_regrid
from pytplot import get_timespan, get_data, store_data

from .erg_mepe_get_dist import erg_mepe_get_dist
from .erg_pgs_clean_data import erg_pgs_clean_data
from .erg_pgs_limit_range import erg_pgs_limit_range
from .erg_convert_flux_units import erg_convert_flux_units
from .erg_pgs_moments_tplot import erg_pgs_moments_tplot
from .erg_pgs_make_fac import erg_pgs_make_fac

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
    relativistic=False,
    no_regrid=False
    ):

    if len(tnames(in_tvarname)) < 1:
        print('No input data, please specify tplot variable!')
        return 0

    in_tvarname = tnames(in_tvarname)[0]
    instnm = in_tvarname.split('_')[1]  #  ;; mepe or mepi

    if no_ang_weighting:
        no_regrid = True

    if isinstance(outputs, str):
        outputs_lc = outputs.lower()
        outputs_lc = outputs_lc.split(' ')
    elif isinstance(outputs, list):
        outputs_lc = []
        for output in outputs:
            outputs_lc.append(output.lower())

    units_lc = units.lower()

    if phi_in != [0., 360.]:
        if abs(phi_in[1] - phi_in[0]) > 360.:
            print('ERROR: Phi restrictions must have range no larger than 360 deg')
            return 0
        
        phi = phi_in  # Survey or implement of spd_pgs_map_azimuth() have not conducted yet.
        if phi[0] == phi[1]:
            phi = [0., 360.]


    if abs(gyro[1] - gyro[0]) > 360.:
        print('ERROR: Gyro restrictions must have range no larger than 360 deg')
        return 0
    if gyro[0] == gyro[1]:
        gyro = [0., 360.]


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
    if 'phi' in outputs_lc:
        out_phi = np.zeros((times_array.shape[0], dist['n_phi']))
        out_phi_y = np.zeros((times_array.shape[0], dist['n_phi']))

    if 'gyro' in outputs_lc:
        out_gyro = np.zeros((times_array.shape[0], dist['n_phi']))
        out_gyro_y = np.zeros((times_array.shape[0], dist['n_phi']))

    if 'pa' in outputs_lc:
        out_pad = np.zeros((times_array.shape[0], dist['n_theta']))
        out_pad_y = np.zeros((times_array.shape[0], dist['n_theta']))

    if 'moments' in outputs_lc:
        out_density = np.zeros(times_array.shape[0])
        out_avgtemp = np.zeros(times_array.shape[0])
        out_vthermal = np.zeros(times_array.shape[0])
        out_flux = np.zeros([times_array.shape[0], 3])
        out_velocity = np.zeros([times_array.shape[0], 3])
        out_mftens = np.zeros([times_array.shape[0], 6])
        out_ptens = np.zeros([times_array.shape[0], 6])
        out_ttens = np.zeros([times_array.shape[0], 3, 3])

    out_vars = []
    last_update_time = None

    """
    ;;--------------------------------------------------------
    ;;Prepare support data
    ;;--------------------------------------------------------
    """
    # ;;create rotation matrix to B-field aligned coordinates if needed
    
    fac_outputs = ['pa','gyro','fac_energy', 'fac_moments']
    fac_requested = len(set(outputs_lc).intersection(fac_outputs)) > 0
    if fac_requested:
        """
        ;; Create magnetic field data with times shifted by half of spin
        ;; periods
        """
        if (mag_name is None) or (len(tnames(mag_name)) < 1):
            print('Cannot find the magnetic field data given by keyword mag_name! EXIT!')
            return
        mag_data = get_data(mag_name)
        dt_array = mag_data[0][1:] - mag_data[0][:-1]
        dt_array = np.insert(dt_array, dt_array.shape[0], dt_array[-1])  # ;; Note that the last value might not be correct.
        mag_name_sftd = mag_name + '_shifted'
        store_data(mag_name_sftd, data={'x':mag_data[0] + dt_array/2.,
                                        'y':mag_data[1]})
        """
        ;;The time shift applied above assumes that the time labels of MGF
        ;;data correspond to the spin start times. Otherwise this should
        ;;be modified properly.
        """

        fac_matrix = erg_pgs_make_fac(times_array, mag_name_sftd, pos_name, fac_type=fac_type)

        if fac_matrix is None:
            # problem creating the FAC matrices
            fac_requested = False

    #  ;;create the magnetic field vector array for moment calculation
    magf = np.array([0., 0., 0.])
    no_mag_for_moments = False

    if ('moments' in outputs_lc) or ('fac_moments' in outputs_lc):

        no_mag = mag_name is None
        magnm = tnames(mag_name)
        if (len(magnm) < 1) or no_mag:
            print('the magnetic field data is not given!')
            no_mag_for_moments = True
        else:
            magnm = magnm[0]

            """
            ;; Create magnetic field data with times shifted by half of spin
            ;; periods
            """

            mag_data = get_data(magnm)
            dt_array = mag_data[0][1:] - mag_data[0][:-1]
            dt_array = np.insert(dt_array, 
            dt_array.shape[0], dt_array[-1])#;; Note that the last value might not be correct.
            magnm_sftd = magnm + '_shifted'
            store_data(magnm_sftd, data={'x':mag_data[0] + dt_array / 2.,
                                         'y':mag_data[1]})
            tinterpol(magnm_sftd, times_array, newname=magnm_sftd)
            magf = get_data(magnm_sftd)[1]  #  ;; [ time, 3] nT

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

        if magf.ndim == 2:
            magvec = magf[index]
        elif magf.ndim == 1:
            magvec = magf

        clean_data = erg_pgs_clean_data(dist, units=units_lc,relativistic=relativistic, magf=magvec)

        if fac_requested:
            pre_limit_bins = np.copy(clean_data['bins'])

        clean_data = erg_pgs_limit_range(clean_data, phi=phi_in, theta=theta, energy=energy)

        if 'moments' in outputs_lc:
            clean_data_eflux = erg_convert_flux_units(clean_data, units='eflux')
            magfarr = np.copy(magf)
            moments = spd_pgs_moments(clean_data_eflux)

            out_density[index] = moments['density']
            out_avgtemp[index] = moments['avgtemp']
            out_vthermal[index] = moments['vthermal']
            out_flux[index, :] = moments['flux']
            out_velocity[index, :] = moments['velocity']
            out_mftens[index, :] = moments['mftens']
            out_ptens[index, :] = moments['ptens']
            out_ttens[index, :] = moments['ttens']

        #  ;;Build theta spectrogram
        if 'theta' in outputs_lc:
            out_theta_y[index, :], out_theta[index, :] = spd_pgs_make_theta_spec(clean_data)

        #  ;;Build energy spectrogram
        if 'energy' in outputs_lc:
            out_energy_y[index, :], out_energy[index, :] = spd_pgs_make_e_spec(clean_data)

        #  ;;Build phi spectrogram
        if 'phi' in outputs_lc:
            out_phi_y[index, :], out_phi[index, :] = spd_pgs_make_phi_spec(clean_data, resolution=dist['n_phi'])

        #  ;;Perform transformation to FAC, (regrid data), and apply limits in new coords
        
        if fac_requested:
            
            # ;limits will be applied to energy-aligned bins
            clean_data['bins'] = np.copy(pre_limit_bins)
            clean_data = erg_pgs_limit_range(clean_data, phi=phi_in, theta=theta, energy=energy, no_ang_weighting=no_ang_weighting)

            # ;perform FAC transformation and interpolate onto a new, regular grid 
            clean_data = spd_pgs_do_fac(clean_data, fac_matrix[index, :, :])

            #;nearest neighbor interpolation to regular grid in FAC
            if not no_regrid:
                clean_data = spd_pgs_regrid(clean_data, regrid)

            clean_data['theta'] = 90.0-clean_data['theta']  #  ;pitch angle is specified in co-latitude

            # ;apply gyro & pitch angle limits(identical to phi & theta, just in new coords)
            clean_data = erg_pgs_limit_range(clean_data, theta=pitch, phi=gyro)

            if 'pa' in outputs_lc:
                # ;Build pitch angle spectrogram
                out_pad_y[index, :], out_pad[index, :] = spd_pgs_make_theta_spec(clean_data, colatitude=True, resolution=regrid[1])

            if 'gyro' in outputs_lc:
                # ;Build gyrophase spectrogram
                out_gyro_y[index, :], out_gyro[index, :] = spd_pgs_make_phi_spec(clean_data, resolution=regrid[0])



    if 'energy' in outputs_lc:
        output_tplot_name = in_tvarname+'_energy' + suffix
        spd_pgs_make_tplot(output_tplot_name, x=times_array, y=out_energy_y, z=out_energy, units=units, ylog=True, ytitle=dist['data_name'] + ' \\ energy (eV)')
        out_vars.append(output_tplot_name)
    if 'theta' in outputs_lc:
        output_tplot_name = in_tvarname+'_theta' + suffix
        spd_pgs_make_tplot(output_tplot_name, x=times_array, y=out_theta_y, z=out_theta, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ theta (deg)')
        out_vars.append(output_tplot_name)
    if 'phi' in outputs_lc:
        output_tplot_name = in_tvarname+'_phi' + suffix
        spd_pgs_make_tplot(output_tplot_name, x=times_array, y=out_phi_y, z=out_phi, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ phi (deg)')
        out_vars.append(output_tplot_name)

    #  ;;Pitch Angle Spectrograms
    if 'pa' in outputs_lc:
        output_tplot_name = in_tvarname+'_pa' + suffix
        spd_pgs_make_tplot(output_tplot_name, x=times_array, y=out_pad_y, z=out_pad, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ PA (deg)')
        out_vars.append(output_tplot_name)

    if 'gyro' in outputs_lc:
        output_tplot_name = in_tvarname+'_gyro' + suffix
        spd_pgs_make_tplot(output_tplot_name, x=times_array, y=out_gyro_y, z=out_gyro, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ gyro (deg)')
        out_vars.append(output_tplot_name)


    #  ;Moments Variables
    if 'moments' in outputs_lc:
        moments = {'density': out_density, 
              'flux': out_flux, 
              'mftens': out_mftens, 
              'velocity': out_velocity, 
              'ptens': out_ptens,
              'ttens': out_ttens,
              'vthermal': out_vthermal,
              'avgtemp': out_avgtemp}
        moments_vars = erg_pgs_moments_tplot(moments, x=times_array, prefix=in_tvarname)
        out_vars.extend(moments_vars)


    return out_vars
