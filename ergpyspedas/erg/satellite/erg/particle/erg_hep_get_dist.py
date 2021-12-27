import cdflib
import logging
import numpy as np


from copy import deepcopy
from scipy.spatial import KDTree
from pyspedas import tnames
from pyspedas.utilities.time_double import time_double
from pyspedas.utilities.time_string import time_string
from pytplot import get_data
from scipy import interpolate

from astropy.coordinates import spherical_to_cartesian, cartesian_to_spherical

logging.captureWarnings(True)
logging.basicConfig(format='%(asctime)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
def erg_hep_get_dist(tname,
                      index=None,
                      units='flux',
                      level='l2',
                      species='e',
                      time_only=False,
                      single_time=None,
                      trange=None,
                      new_effic=False,
                      w_sct015=False,
                      exclude_azms=False,
                      flip_the_of_ssd3=False):
    if len(tnames(tname)) > 0:
        input_name = tnames(tname)[0]
    else:
        print(f'Variable: {tname} not found!')
        return 0
    level = level.lower()
    
    #  ;; only erg_hep_l2_3dflux_FEDU is acceptable for this routine
    if ('erg_hep_l2_FEDU_L' not in input_name) \
    and ('erg_hep_l2_FEDU_H' not in input_name) \
    and ('erg_hep_l2_rawcnt_H' not in input_name) \
    and ('erg_hep_l2_rawcnt_L' not in input_name):
        print(f'Variable {input_name}  is not acceptable. This routine can take only erg_hep_l2_(FEDU/rawcnt)_? as the argument.')
        return 0
    """
    ;; Extract some information from a tplot variable name
    ;; e.g., erg_lepi_l2_3dflux_FPDU
    """
    vn_info = input_name.split('_')
    instrument = vn_info[1]  #  ;;hep
    level = vn_info[2]       #  ;;l2
    dtype = vn_info[3]       #  ;;FEDU or rawcnt
    suf = vn_info[4]        #  ;; L or H 
    arrnm = vn_info[4]
    if species is None:
        if instrument == 'hep':
            species = 'e'
        else:
            print(f'RROR: given an invalid tplot variable: {input_name}')
    # ;; Reform a data array so that it is grouped for each spin
    data_in = get_data(input_name)
    
    if data_in is None:
        print('Problem extracting the mepe 3dflux data.')
        return 0
    data_in_metadata = get_data(input_name, metadata=True)
    t_fedu = deepcopy(data_in[0])
    fedu = deepcopy(data_in[1])
    vn_angsga = '_'.join(vn_info[0:3] +['FEDU', suf, 'Angle_sga'])
    if get_data(vn_angsga) is not None:
        angsga = deepcopy(get_data(vn_angsga)[1])
    else:
        print(f'Cannot find variable {vn_angsga}, which is essential for this routine to work.')
        return 0

    vn_sctno = '_'.join(vn_info[0:3] +['sctno', suf])
    if len(tnames(vn_sctno)) < 1:
        print(f'Cannot find variable {vn_sctno}, which is essential for this routine to work.')
        return 0
    else:
        time_scno, scno = get_data(tnames(vn_sctno)[0])

    id_scno_0=np.argwhere(scno == 0)
    sc0num = len(id_scno_0)
    if sc0num < 5:
        print(f'Only data for less than 5 spins are loaded for HEP_{suf}!!')
        return 0
    
    # ;; integration time for each spin sector
    sctdt = time_scno[1:] - time_scno[:-1]
    sctintgt=np.insert(sctdt, sctdt.shape[0],sctdt[-1])

    id_scno_0_list = id_scno_0[:,0].tolist()
    sc0_t = time_scno[id_scno_0_list]  # ;; times of spin sector #0, namely the start of each spin
    dt_array = sc0_t[1:] - sc0_t[:-1]
    sc0_dt = np.insert(dt_array, dt_array.shape[0], dt_array[-1])

    #  processing for 'id_t_fedu = value_locate()' in IDL.
    sc0_t_repeat = np.repeat(np.array([sc0_t]).T, 2, 1)
    t_fedu_repeat = np.repeat(np.array([t_fedu]).T, 2, 1)
    tree = KDTree(sc0_t_repeat)
    _, id_t_fedu_nn = tree.query(t_fedu_repeat)
    id_t_fedu = np.where((t_fedu - sc0_t[id_t_fedu_nn.tolist()]) < 0., id_t_fedu_nn-1, id_t_fedu_nn)
    #  processing for 'id_t_fedu = value_locate()' in IDL.

    #  ;; Genrate angarr by picking up angle values at each spin start
    angarr = angsga[id_scno_0_list, :, :]

    #  ;; fedu_arr:[ time, spin sct, energy, azm ]
    #   ;; by default
    nene = 16
    nazm = 15
    nsct = 16
    #   ;; by default

    if suf == 'H':  # ;; Lv2 HEP-H flux array has 11 elements for energy bin currently.
        nene = 11
    fedu_arr = np.full(shape=(sc0num, nsct, nene, nazm ), fill_value=np.nan)  # ;; padded with NaN
    intgt = np.full(shape=(sc0num, nsct), fill_value=np.nan)  # ;; padded with NaN
    
    for i in range(sc0num):
        id_array = np.argwhere( (id_t_fedu == i) & (scno >= 0) & (scno <= 15))
        if len(id_array) < 2:
            continue
        id_list = id_array[:, 0].tolist()
        datarr = fedu[id_list, :, :]  # ;; usually [16(time), 16(energy), 15(azm)]
        tarr = t_fedu[id_list]
        sctarr = scno[id_list]
        sctarr_list = sctarr.tolist()
        nsct = len(sctarr_list)
        inttarr = sctintgt[id_list]

        fedu_arr[i, sctarr_list, :, :] = datarr.reshape(1, nsct, nene, nazm)
        intgt[i, sctarr_list] = inttarr.reshape(1, nsct)

    p_structure = {
    'x':sc0_t,  # ;; Put the start time of each spin
    'y':fedu_arr  # ;; [ time, 16(sct), 16(energu), 15(azm) ]
    }

    if p_structure['y'].ndim != 4:
        print(f'Variable: {input_name} contains wrong number of elements!')
        return 0

    # ;; Return time labels corresponding the middle time of each spin
    if time_only:
        return p_structure['x']
    
    if single_time is not None:
        single_time_double = time_double(single_time)
        if (p_structure['x'][0] <= single_time_double)\
                and (single_time_double <= p_structure['x'][-1]):
            nearest_time = interpolate.interp1d(p_structure['x'], p_structure['x'],
                                                kind="nearest")(single_time_double)
        elif (single_time_double < p_structure['x'][0])\
                or (p_structure['x'][-1] < single_time_double):
            nearest_time = interpolate.interp1d(p_structure['x'], p_structure['x'],
                                                kind="nearest", fill_value='extrapolate')(single_time_double)
        index = np.where(p_structure['x'] == nearest_time)[0]
        n_times = index.size
    else:
        # index supersedes time range
        if index is None:
            if trange is not None:
                trange_double_array = np.array(time_double(trange))
                trange_minmax = np.array([trange_double_array.min(),
                                          trange_double_array.max()])
                index = np.where((p_structure['x'] >= trange_minmax[0])
                                 & (p_structure['x'] <= trange_minmax[1]))[0]
                n_times = index.size
                if n_times == 0:
                    print('No data in time range: '
                          + ' '.join(time_string(trange_minmax)))
                    return 0
            else:
                n_times = p_structure['x'].size
                index = np.arange(n_times)
        else:
            n_times = np.array([index]).size
    """
    ;; --------------------------------------------------------------
    ;; HEP data arr: [9550(time), 16(spin phase), 16(energy), 15(azimuth ch )]
    ;; Dimensions
    """
    # ;; Dimensions
    # ;; to [ energy, spin phase, azimuth ch(elevation) ]
    dim_array = np.array(p_structure['y'].shape[1:])[[1, 0, 2]]
    if species.lower() == 'e':
        mass = 5.68566e-06
        charge = -1.
        data_name = f'HEP-{suf} Electron 3dflux'
        if dtype == 'rawcnt':
            data_name = f'HEP-{suf} Electron raw count/sample'
        integ_time = 7.99 / 16  # ;; currently hard-coded, but practically not used.
    else:
        print('given species is not supported by this routine.')
        return 0
    #  ;; basic template structure compatible with other routines
    dist = {
        'project_name': 'ERG',
        'spacecraft': 1,  # always 1 as a dummy value
        'data_name': data_name,
        'units_name': 'flux',  # ; HEP data in [/keV-s-sr-cm2] should be converted to [/eV-s-sr-cm2]
        'units_procedure': 'erg_convert_flux_units',
        'species': species,
        'valid': 1,
        'charge': charge,
        'mass': mass,
    }
    # other keys (members) will added in below processing, sequentially.
    """
    ;; Then, fill in arrays in the data structure
    ;;   dim[ nenergy, nspinph(azimuth), nanode(elevation), ntime]
    """
    dist['time'] = p_structure['x'][[index]]  # ;; the start time of spin
    dist['end_time'] = dist['time'] + sc0_dt[[index]]  # ;; the end time of spin
    """
    ;; Shuffle the original data array [time,spin phase,energy,apd] to
    ;; be energy-azimuth-elevation-time.
    ;; The factor 1d-3 is to convert [/keV-s-sr-cm2] (default unit of
    ;; HEP Lv2 flux data) to [/eV-s-sr-cm2] 
    """
    if 'cnt' not in dtype:
        dist['data'] = p_structure['y'][[index]].transpose([2, 1, 3, 0]) * 1.e-03
    else:
        dist['data'] = p_structure['y'][[index]].transpose([2, 1, 3, 0])  # ;; for count/sample, count/sec
    
    dist['bins'] = np.ones(shape=np.insert(dim_array, dim_array.shape[0],
                                           n_times), dtype='int8')

    """
    ;; Exclude spin phases #0 and #15 currently from spectrum
    ;; calculations
    """
    if not w_sct015:
        dist['bins'][:, 0, :, :] = 0
        dist['bins'][:, 15, :, :] = 0
    
    #  ;; Exclude invalid azimuth channels
    if exclude_azms:
        invalid_azms = [0, 4, 5, 9, 10, 11, 14]
        dist['bins'][:, :, invalid_azms, :] = 0

    #  ;; Apply the empiricallly-derived efficiency (only for cnt/cntrate/dtcntrate)
    if (new_effic) and ('cnt' in dtype):
        """
        ;; efficiency for each azim. ch. based on the inter-ch. calibration
        ;; Only valid for 2017-06-21 through 2019-02-07 
        """
        effic = [
          0.171, 0.460, 1.013, 0.411, 0.158, 
          0.162, 0.450, 1.000, 0.399, 0.158, 
          0.120, 0.170, 0.629, 0.346, 0.132
        ]
        for i in range(15):
            dist['data'][:, :, i, :] /= effic[i]
        print(' new_effic has been applied!')

    file_name_raw= get_data(input_name, metadata=True)['CDF']['FILENAME']
    if isinstance(file_name_raw, str):
        cdf_path = file_name_raw
    elif isinstance(file_name_raw, list):
        cdf_path = file_name_raw[-1]

    cdf_file = cdflib.CDF(cdf_path)

    #  ;; Energy ch
    """
    ;; Default unit of v in F?DU tplot variables [keV/q] should be
    ;; converted to [eV] by multiplying (1000 * charge number).
    """
    e0_array_raw = data_in[2][[index]]# ;; [time, 32]
    e0_array = e0_array_raw.T
    energy_reform = np.reshape(e0_array, [dim_array[0], 1, 1, n_times])
    energy_rebin1 = np.repeat(energy_reform, dim_array[2],
                             axis=2)  # repeated across apd(elevation)
    dist['energy'] = np.repeat(energy_rebin1, dim_array[1],
                              axis=1)  # repeated across spin phase(azimuth)

    # denergy member
    
    de_array = e0_array + np.nan  #  ;; initialized as [ time, 32 ]  
    for i in range(n_times):
        enec0_array = deepcopy(e0_array[:, i])
        id_array = np.argwhere(np.isfinite(enec0_array))
        if len(id_array) < 2:
            continue
        enec_array = np.sort(np.unique(enec0_array[id_array[:,0].tolist()]))
        n_enec = enec_array.size
        if (n_enec < 3) or (np.nansum(enec_array) < 0.):
            continue  # ;; invalid energy value found
        logenec_array = np.log10(enec_array)
        logmn_array = (logenec_array[1:] + logenec_array[:-1]) / 2.
        logdep_array = enec_array * 0.
        logdem_array = enec_array * 0.
        logdep_array[:-1] = deepcopy(logmn_array)
        logdem_array[1:] = deepcopy(logmn_array)
        logdem_array[0] = logenec_array[0] - (logmn_array[0] - logenec_array[0])
        logdep_array[-1] = logenec_array[-1] + (logenec_array[-1] - logmn_array[-1])
        de_array_i= 10.**logdep_array - 10.**logdem_array

        # getting nearest neighbor indices, 'id = nn( enec, enec0 ) ' in IDL
        enec0_array_temp = np.nan_to_num(enec0_array, copy=True,nan=np.nanmin(enec0_array))
        enec0_array_temp_repeat= np.repeat(np.array([enec0_array_temp]).T, 2, 1)
        enec_array_repeat= np.repeat(np.array([enec_array]).T, 2, 1)
        tree = KDTree(enec_array_repeat, leafsize=1)
        _, id_array = tree.query(enec0_array_temp_repeat)
        # getting nearest neighbor indices, 'id = nn( enec, enec0 ) ' in IDL
        de_array[:, i] = de_array_i[id_array].T

    de_reform = np.reshape(de_array, [dim_array[0], 1, 1, n_times])
    de_rebin1 = np.repeat(de_reform, dim_array[2],
                         axis=2)  # repeated across apd(elevation)
    dist['denergy'] = np.repeat(de_rebin1, dim_array[1],
                         axis=1)  # repeated across spin phase(azimuth)

    dist['n_energy'] = dim_array[0]
    dist['n_bins'] = dim_array[1] * dim_array[2]  #   # thetas * # phis
    """
    ;; Array elements containing NaN are excluded from the further
    ;; calculations, by setting bins to be zero.
    """
    dist['bins'] = np.where((np.isfinite(dist['data']))
                               &(np.isfinite(dist['energy'])),
                               1,0)
    
    #  ;; azimuthal angle in spin direction
    angarr = cdf_file.varget('FEDU_Angle_SGA') # ;;[elev/phi, (anode)] in SGA  (looking dir)

    # ;; Flip the looking dirs to the flux dirs
    n_anode = angarr[0].size
    r_array = np.ones(n_anode)
    elev_array = deepcopy(angarr[0])
    phi_array = deepcopy(angarr[1])
    deg_to_rad = np.pi / 180.
    x_array, y_array, z_array = spherical_to_cartesian(
                                     r_array,
                                     elev_array * deg_to_rad,
                                     phi_array* deg_to_rad
                                     )
    r_array, elev_array, phi_array = cartesian_to_spherical(
                                        -x_array,
                                        -y_array,
                                        -z_array)
    elev_array = elev_array.value / deg_to_rad
    phi_array = phi_array.value / deg_to_rad
    angarr = np.array([elev_array, phi_array])

    phissi = angarr[1] - (90. + 21.6)  # ;; [(anode)] (21.6 = degree between sun senser and satellite coordinate)
    spinph_ofst = data_in[4] * 22.5
    phi0_1_reform = np.reshape(phissi, [1, 1, dim_array[2], 1])
    phi0_1_rebin1 = np.repeat(phi0_1_reform, dim_array[1],
                             axis=1)  # repeated across spin phase(azimuth)
    phi0_1_rebin2 = np.repeat(phi0_1_rebin1, dim_array[0],
                             axis=0)  # repeated across energy
    phi0_1 = np.repeat(phi0_1_rebin2,     n_times,
                              axis=3)  # repeated across n_times
    phi0_2_reform = np.reshape(spinph_ofst, [1, dim_array[1], 1, 1])
    phi0_2_rebin1 = np.repeat(phi0_2_reform, dim_array[2],
                             axis=2)  # repeated across apd(elevation)
    phi0_2_rebin2 = np.repeat(phi0_2_rebin1, dim_array[0],
                             axis=0)  # repeated across energy
    phi0_2 = np.repeat(phi0_2_rebin2, n_times,
                              axis=3)  # repeated across n_times
    phi0 = phi0_1 + phi0_2
    ofst_sv = (np.arange(dim_array[0]) + 0.5) * \
        22.5/dim_array[0]  # ;; [(energy)]
    phi_ofst_for_sv_reform = np.reshape(ofst_sv, [dim_array[0], 1, 1, 1])
    phi_ofst_for_sv_rebin1 = np.repeat(
        phi_ofst_for_sv_reform, dim_array[2],
                                 axis=2)  # repeated across apd(elevation)
    phi_ofst_for_sv_rebin2 = np.repeat(
        phi_ofst_for_sv_rebin1,dim_array[1],
                                 axis=1)  # repeated across spin phase(azimuth)
    phi_ofst_for_sv = np.repeat(phi_ofst_for_sv_rebin2,         n_times,
                                 axis=3)  # repeated across n_times
    """
    ;;  phi angle for the start of each spin phase
    ;;    + offset angle foreach sv step
    """
    dist['phi'] = np.fmod((phi0 + phi_ofst_for_sv + 360.), 360.)
    dist['dphi'] = np.full(shape=np.insert(dim_array, dim_array.shape[0],
                                           n_times), fill_value=22.5)  # ;; 22.5 deg as a constant
    del phi0, phi_ofst_for_sv  # ;; Clean huge arrays
    dist['n_phi'] = dim_array[1]
    #  ;; elevation angle
    elev = angarr[0]  # ;; [(anode)]
    elev_reform = np.reshape(elev, [1, 1, dim_array[2], 1])
    elev_rebin1 = np.repeat(elev_reform, dim_array[1],
                             axis=1)  # repeated across spin phase(azimuth)
    elev_rebin2 = np.repeat(elev_rebin1, dim_array[0],
                             axis=0)  # repeated across energy
    dist['theta'] = np.repeat(elev_rebin2, n_times,
                             axis=3)  # repeated across n_times

    #  ;; elevation angle for fine channel  
    
    if 'fine_ch' in vn_info:
        dist['dtheta'] = np.full(shape=np.insert(dim_array, dim_array.shape[0],
                                             n_times), fill_value=22.5/6.)  #  ;; Fill all with 22.5/6.
    else:
        dist['dtheta'] = np.full(shape=np.insert(dim_array, dim_array.shape[0],
                                             n_times), fill_value=22.5)  #  ;; Fill all with 22.5. first
        #  ;; give half weight for ch1,2,3,4, 19,20,21,22
        dist['dtheta'][:, :, 0:4, :] = 11.25
        dist['dtheta'][:, :, dim_array[2]-4:dim_array[2], :] = 11.25
        if dim_array[2] == 22:  #  ;; with full fine channels
            dist['dtheta'][:, :, 5:17, :] = 22.5/6

    dist['n_theta'] = dim_array[2]
    
    return dist
