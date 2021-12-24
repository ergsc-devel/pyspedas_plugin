import numpy as np

from copy import deepcopy

from pyspedas import tnames, tinterpol
from pyspedas.utilities.time_double import time_double
from pyspedas.utilities.time_string import time_string

from pyspedas.particles.moments.spd_pgs_moments import spd_pgs_moments
from pyspedas.particles.spd_part_products.spd_pgs_regrid import spd_pgs_regrid
from pytplot import get_timespan, get_data, store_data, tplot_copy, ylim

from .erg_lepe_get_dist import erg_lepe_get_dist
from .erg_lepi_get_dist import erg_lepi_get_dist
from .erg_pgs_clean_data import erg_pgs_clean_data
from .erg_pgs_limit_range import erg_pgs_limit_range
from .erg_convert_flux_units import erg_convert_flux_units
from .erg_pgs_moments_tplot import erg_pgs_moments_tplot
from .erg_pgs_make_fac import erg_pgs_make_fac
from .erg_pgs_make_e_spec import erg_pgs_make_e_spec
from .erg_pgs_make_theta_spec import erg_pgs_make_theta_spec
from .erg_pgs_make_phi_spec import erg_pgs_make_phi_spec
from .erg_pgs_do_fac import erg_pgs_do_fac
from .erg_pgs_progress_update import erg_pgs_progress_update
from .erg_pgs_make_tplot import erg_pgs_make_tplot

def erg_lep_part_products(
    in_tvarname,
    species=None,
    outputs=['energy'],
    no_ang_weighting=True,
    suffix='',
    units='flux',
    datagap=32.1,
    regrid=[16, 16],
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
    vn_info = in_tvarname.split('_')
    instnm = vn_info[1]  #  ;; should be 'lepe' or 'lepi'
    lvl = vn_info[2]  #  ;; 'l2'
    datnm = vn_info[3]  #  ;; '3dflux'

    #  ;; Check if a tplot variable given is acceptable
    if (instnm != 'lepe') and (instnm != 'lepi') or (datnm != '3dflux'):
        print('The tplot variable given as an argument is not valid!')
        print(f'varname: {in_tvarname}')
        return

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


    """
    ;;Create energy spectrogram after FAC transformation if limits are not 
    ;;identical to the default.
    """
    if (gyro != [0., 360.]) or (pitch != [0.,180.]):
        idx = np.where(np.array(outputs_lc) == 'energy')[0]
        if (idx.shape[0] > 0) and ('fac_energy' not in outputs_lc):
            idx = idx[0]
            outputs_lc[idx] = 'fac_energy'

        idx = np.where(np.array(outputs_lc) == 'moments')[0]
        if (idx.shape[0] > 0) and ('fac_moments' not in outputs_lc):
            idx = idx[0]
            outputs_lc[idx] = 'fac_moments'

    #  ;;Preserve the original time range
    tr_org = get_timespan(in_tvarname)

    if instnm == 'lepe':
        times_array = erg_lepe_get_dist(in_tvarname, species=species, units=units_lc, time_only=True)
    if instnm == 'lepi':
        times_array = erg_lepi_get_dist(in_tvarname, species=species, units=units_lc, time_only=True)

    if trange is not None:
        
        trange_double = time_double(trange)
        time_indices = np.where((times_array >= trange_double[0]) \
                                & (times_array <= trange_double[1]))[0]
        
        if time_indices.shape[0] < 1:
            print(f'No ,{in_tvarname}, data for time range ,{time_string(trange_double)}')

    elif trange is None:
        time_indices = np.arange(times_array.shape[0])

    times_array = times_array[time_indices]



    if instnm == 'lepe':
        dist, angarr_loaded_raw = erg_lepe_get_dist(in_tvarname, 0, species=species, units=units_lc)
    if instnm == 'lepi':
        dist = erg_lepi_get_dist(in_tvarname, 0, species=species, units=units_lc)

    if 'energy' in outputs_lc:
        out_energy = np.zeros((times_array.shape[0], dist['n_energy']))
        out_energy_y = np.zeros((times_array.shape[0], dist['n_energy']))
    if 'theta' in outputs_lc:
        if instnm == 'lepe':
            n_theta_unique = len(np.unique(dist['theta']))
            out_theta = np.zeros((times_array.shape[0], n_theta_unique))
            out_theta_y = np.zeros((times_array.shape[0], n_theta_unique))
        elif  instnm == 'lepi':
            out_theta = np.zeros((times_array.shape[0], dist['n_theta']))
            out_theta_y = np.zeros((times_array.shape[0], dist['n_theta']))
    if 'phi' in outputs_lc:
        out_phi = np.zeros((times_array.shape[0], dist['n_phi']))
        out_phi_y = np.zeros((times_array.shape[0], dist['n_phi']))

    if 'gyro' in outputs_lc:
        out_gyro = np.zeros((times_array.shape[0], regrid[0]))
        out_gyro_y = np.zeros((times_array.shape[0], regrid[0]))

    if 'pa' in outputs_lc:
        out_pad = np.zeros((times_array.shape[0], regrid[1]))
        out_pad_y = np.zeros((times_array.shape[0], regrid[1]))

    if 'moments' in outputs_lc:
        out_density = np.zeros(times_array.shape[0])
        out_avgtemp = np.zeros(times_array.shape[0])
        out_vthermal = np.zeros(times_array.shape[0])
        out_flux = np.zeros([times_array.shape[0], 3])
        out_velocity = np.zeros([times_array.shape[0], 3])
        out_mftens = np.zeros([times_array.shape[0], 6])
        out_ptens = np.zeros([times_array.shape[0], 6])
        out_ttens = np.zeros([times_array.shape[0], 3, 3])

    if 'fac_energy' in outputs_lc:
        out_fac_energy = np.zeros((times_array.shape[0], dist['n_energy']))
        out_fac_energy_y = np.zeros((times_array.shape[0], dist['n_energy']))

    if 'fac_moments' in outputs_lc:
        out_fac_density = np.zeros(times_array.shape[0])
        out_fac_avgtemp = np.zeros(times_array.shape[0])
        out_fac_vthermal = np.zeros(times_array.shape[0])
        out_fac_flux = np.zeros([times_array.shape[0], 3])
        out_fac_velocity = np.zeros([times_array.shape[0], 3])
        out_fac_mftens = np.zeros([times_array.shape[0], 6])
        out_fac_ptens = np.zeros([times_array.shape[0], 6])
        out_fac_ttens = np.zeros([times_array.shape[0], 3, 3])
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
        ;; Currently triangulation fails, so forcidly no_regrid is set for
        ;; spectum generation in FAC coordinates.
        """
        no_regrid = True

        fac_matrix = erg_pgs_make_fac(times_array, mag_name, pos_name, fac_type=fac_type)

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

            magtmp = magnm+'_pgs_temp'
            tplot_copy(magnm, magtmp)
            tinterpol(magtmp, times_array, newname=magtmp)
            magf = get_data(magtmp)[1]  #  ;; [ time, 3] nT

    """
    ;;-------------------------------------------------
    ;; Loop over time to build spectrograms and/or moments
    ;;-------------------------------------------------
    """
    for index in range(time_indices.shape[0]):
        last_update_time = erg_pgs_progress_update(last_update_time=last_update_time,
             current_sample=index, total_samples=time_indices.shape[0], type_string=in_tvarname)

        #  ;; Get the data structure for this sample

        if instnm == 'lepe':

            dist, angarr_loaded_raw = erg_lepe_get_dist(in_tvarname, time_indices[index], species=species, units=units_lc, angrarr_input=angarr_loaded_raw)

        if instnm == 'lepi':
            dist = erg_lepi_get_dist(in_tvarname, time_indices[index], species=species, units=units_lc)

        if magf.ndim == 2:
            magvec = magf[index]
        elif magf.ndim == 1:
            magvec = magf

        if ('moments' in outputs_lc) or ('fac_moments' in outputs_lc):
            clean_data = erg_pgs_clean_data(dist, units=units_lc, magf=magvec,
                                            for_moments=True)  #;; invalid values are zero-padded. 
        else:
            clean_data = erg_pgs_clean_data(dist, units=units_lc, magf=magvec)

        if fac_requested:
            pre_limit_bins = deepcopy(clean_data['bins'])

        clean_data = erg_pgs_limit_range(clean_data, phi=phi_in, theta=theta, energy=energy, no_ang_weighting=no_ang_weighting)

        if ('moments' in outputs_lc) or ('fac_moments' in outputs_lc):
            clean_data_eflux = erg_convert_flux_units(clean_data, units='eflux')
            magfarr = deepcopy(magf)
            clean_data_eflux_for_moments = deepcopy(clean_data_eflux)
            clean_data_eflux_for_moments['data'] = np.where(clean_data_eflux_for_moments['bins'] == 0,
                                                            0,clean_data_eflux_for_moments['data'])
            moments = spd_pgs_moments(clean_data_eflux_for_moments)

            if 'moments' in outputs_lc:
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
            if  instnm == 'lepe':
                out_theta_y[index, :], out_theta[index, :] = erg_pgs_make_theta_spec(clean_data, no_ang_weighting=no_ang_weighting)
            elif instnm == 'lepi':
                out_theta_y[index, :], out_theta[index, :] = erg_pgs_make_theta_spec(clean_data, resolution=dist['n_theta'],no_ang_weighting=no_ang_weighting)

        #  ;;Build energy spectrogram
        if 'energy' in outputs_lc:
            out_energy_y[index, :], out_energy[index, :] = erg_pgs_make_e_spec(clean_data)

        #  ;;Build phi spectrogram
        if 'phi' in outputs_lc:
            out_phi_y[index, :], out_phi[index, :] = erg_pgs_make_phi_spec(clean_data, resolution=dist['n_phi'],no_ang_weighting=no_ang_weighting)

        #  ;;Perform transformation to FAC, (regrid data), and apply limits in new coords
        
        if fac_requested:
            
            # ;limits will be applied to energy-aligned bins
            clean_data['bins'] = deepcopy(pre_limit_bins)
            clean_data = erg_pgs_limit_range(clean_data, phi=phi_in, theta=theta, energy=energy, no_ang_weighting=no_ang_weighting)

            # ;perform FAC transformation and interpolate onto a new, regular grid 
            clean_data = erg_pgs_do_fac(clean_data, fac_matrix[index, :, :])

            #;nearest neighbor interpolation to regular grid in FAC
            if not no_regrid:
                if (not np.all(np.isnan(clean_data['theta']))) and (not np.all(np.isnan(clean_data['phi']))):
                    clean_data = spd_pgs_regrid(clean_data, regrid)

            clean_data['theta'] = 90.0-clean_data['theta']  #  ;pitch angle is specified in co-latitude

            # ;apply gyro & pitch angle limits(identical to phi & theta, just in new coords)
            clean_data = erg_pgs_limit_range(clean_data, theta=pitch, phi=gyro, no_ang_weighting=no_ang_weighting)

            if 'pa' in outputs_lc:
                # ;Build pitch angle spectrogram
                out_pad_y[index, :], out_pad[index, :] = erg_pgs_make_theta_spec(clean_data, colatitude=True, resolution=regrid[1], no_ang_weighting=no_ang_weighting)

            if 'gyro' in outputs_lc:
                # ;Build gyrophase spectrogram
                out_gyro_y[index, :], out_gyro[index, :] = erg_pgs_make_phi_spec(clean_data, resolution=regrid[0], no_ang_weighting=no_ang_weighting)

            if 'fac_energy' in outputs_lc:
                out_fac_energy_y[index, :], out_fac_energy[index, :] = erg_pgs_make_e_spec(clean_data)

            if 'fac_moments' in outputs_lc:
                clean_data['theta'] = 90. - clean_data['theta'] # ;convert back to latitude for moments calc
                temp_dict = {'charge': dist['charge'],
                             'magf': magvec,
                             'species': dist['species'],
                             'sc_pot': 0.,
                             'units_name': units_lc}
                temp_dict.update(clean_data)
                clean_data = deepcopy(temp_dict)
                del temp_dict
                clean_data_eflux = erg_convert_flux_units(clean_data, units='eflux')
                clean_data_eflux_for_moments = deepcopy(clean_data_eflux)
                clean_data_eflux_for_moments['data'] = np.where(clean_data_eflux_for_moments['bins'] == 0,
                                                                0,clean_data_eflux_for_moments['data'])
                fac_moments = spd_pgs_moments(clean_data_eflux_for_moments)

                out_fac_density[index] = fac_moments['density']
                out_fac_avgtemp[index] = fac_moments['avgtemp']
                out_fac_vthermal[index] = fac_moments['vthermal']
                out_fac_flux[index, :] = fac_moments['flux']
                out_fac_velocity[index, :] = fac_moments['velocity']
                out_fac_mftens[index, :] = fac_moments['mftens']
                out_fac_ptens[index, :] = fac_moments['ptens']
                out_fac_ttens[index, :] = fac_moments['ttens']

    made_et_spec = ('energy' in outputs_lc) or ('fac_energy' in outputs_lc)

    if 'energy' in outputs_lc:
        output_tplot_name = in_tvarname+'_energy' + suffix
        erg_pgs_make_tplot(output_tplot_name, x=times_array, y=out_energy_y, z=out_energy, units=units, ylog=True, ytitle=dist['data_name'] + ' \\ energy (eV)')
        ylim(output_tplot_name,  1e+1, 3e+4) #  ;; default yrange: [10 eV, 30 keV]
        out_vars.append(output_tplot_name)
    if 'theta' in outputs_lc:
        output_tplot_name = in_tvarname+'_theta' + suffix
        erg_pgs_make_tplot(output_tplot_name, x=times_array, y=out_theta_y, z=out_theta, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ theta (deg)')
        out_vars.append(output_tplot_name)
    if 'phi' in outputs_lc:
        output_tplot_name = in_tvarname+'_phi' + suffix
        erg_pgs_make_tplot(output_tplot_name, x=times_array, y=out_phi_y, z=out_phi, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ phi (deg)')
        out_vars.append(output_tplot_name)

    #  ;;Pitch Angle Spectrograms
    if 'pa' in outputs_lc:
        output_tplot_name = in_tvarname+'_pa' + suffix
        erg_pgs_make_tplot(output_tplot_name, x=times_array, y=out_pad_y, z=out_pad, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ PA (deg)')
        out_vars.append(output_tplot_name)

    if 'gyro' in outputs_lc:
        output_tplot_name = in_tvarname+'_gyro' + suffix
        erg_pgs_make_tplot(output_tplot_name, x=times_array, y=out_gyro_y, z=out_gyro, units=units, ylog=False, ytitle=dist['data_name'] + ' \\ gyro (deg)')
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
        moments_vars = erg_pgs_moments_tplot(moments, x=times_array, prefix=in_tvarname, suffix=suffix)
        out_vars.extend(moments_vars)

    if 'fac_energy' in outputs_lc:

        output_tplot_name = in_tvarname+'_energy_mag' + suffix
        erg_pgs_make_tplot(output_tplot_name, x=times_array, y=out_fac_energy_y, z=out_fac_energy, units=units, ylog=True, ytitle=dist['data_name'] + ' \\ energy (eV)')
        ylim(output_tplot_name, 1e+1, 3e+4)  # ;; default yrange: [10 eV, 30 keV]
        out_vars.append(output_tplot_name)

    #  ;FAC Moments Variables
    if 'fac_moments' in outputs_lc:
        fac_moments = {'density': out_fac_density, 
              'flux': out_fac_flux, 
              'mftens': out_fac_mftens, 
              'velocity': out_fac_velocity, 
              'ptens': out_fac_ptens,
              'ttens': out_fac_ttens,
              'vthermal': out_fac_vthermal,
              'avgtemp': out_fac_avgtemp}
        fac_mom_suffix = '_mag' + suffix
        fac_moments_vars = erg_pgs_moments_tplot(fac_moments, x=times_array, prefix=in_tvarname, suffix=fac_mom_suffix)
        out_vars.extend(fac_moments_vars)

    return out_vars
