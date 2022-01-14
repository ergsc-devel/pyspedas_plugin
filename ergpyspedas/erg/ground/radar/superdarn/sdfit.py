import cdflib
import numpy as np

from copy import deepcopy
from pytplot import get_data, store_data, options, clip, ylim, zlim
from pyspedas import tnames

from ....satellite.erg.load import load


def sdfit(
    trange=['2018-10-18/00:00:00','2018-10-18/02:00:00'],
    suffix='',
    site='all',
    get_support_data=False,
    varformat=None,
    varnames=[],
    downloadonly=False,
    notplot=False,
    no_update=False,
    uname=None,
    passwd=None,
    time_clip=False,
    ror=True
):

    valid_sites = [ 'ade', 'adw', 'bks', 'bpk', 'cly', 'cve', 'cvw', 'dce', 'fhe',
    'fhw', 'fir', 'gbr', 'hal', 'han', 'hok', 'hkw', 'inv', 'kap', 'ker', 'kod',
    'ksr', 'mcm', 'pgr', 'pyk', 'rkn', 'san', 'sas', 'sps', 'sto', 'sye',
    'sys', 'tig', 'unw', 'wal', 'zho', 'lyr' ]



    if isinstance(site, str):
        if site == 'all':
            site_code = valid_sites
        else:
            site_code = site.lower()
            site_code = site_code.split(' ')
    elif isinstance(site, list):
        site_code = []
        for i in range(len(site)):
            site_code.append(site[i].lower())
    site_code = list(set(site_code).intersection(valid_sites))

    if notplot:
        loaded_data = {}
    else:
        loaded_data = []
    
    for site_input in site_code:

        prefix = 'sd_' + site_input + '_'
        file_res = 3600. * 24.
        pathformat = 'ground/radar/sd/fitacf/'+site_input\
                        +'/%Y/sd_fitacf_l2_'+site_input+'_%Y%m%d*.cdf'

        if notplot:
            loaded_data.update(load(pathformat=pathformat, file_res=file_res, trange=trange, prefix=prefix, suffix=suffix, get_support_data=get_support_data,
                        varformat=varformat, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd))
        else:
            loaded_data += load(pathformat=pathformat, file_res=file_res, trange=trange, prefix=prefix, suffix=suffix, get_support_data=get_support_data,
                        varformat=varformat, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
        """if (len(loaded_data) > 0) and ror:
            try:
                if isinstance(loaded_data, list):
                    if downloadonly:
                        cdf_file = cdflib.CDF(loaded_data[-1])
                        gatt = cdf_file.globalattsget()
                    else:
                        gatt = get_data(loaded_data[-1], metadata=True)['CDF']['GATT']
                elif isinstance(loaded_data, dict):
                    gatt = loaded_data[list(loaded_data.keys())[-1]]['CDF']['GATT']
                print('**************************************************************************')
                print(gatt["Logical_source_description"])
                print('')
                print(f'Information about {gatt["Station_code"]}')
                print('PI and Host PI(s):')
                print(gatt["PI_name"])
                print('')
                print('Affiliation: ')
                print(gatt["PI_affiliation"])
                print('')
                print('Rules of the Road for ISEE Induction Magnetometer Data Use:')
                for gatt_text in gatt["TEXT"]:
                    print(gatt_text)
                print(gatt["LINK_TEXT"])
                print('**************************************************************************')
            except:
                print('printing PI info and rules of the road was failed')
            
        """

        if (not downloadonly) and (not notplot):

            t_plot_name_list = tnames([prefix + 'pwr*', prefix + 'spec*', prefix + 'vlos*'])
            t_plot_name_list = list(set(t_plot_name_list).intersection(loaded_data))
            for t_plot_name in t_plot_name_list:
                clip(t_plot_name, -9000, 9000)
            
            t_plot_name_list = tnames([prefix + 'elev*'])
            t_plot_name_list = list(set(t_plot_name_list).intersection(loaded_data))
            if len(t_plot_name_list) > 5:
                for t_plot_name in t_plot_name_list:
                    clip(t_plot_name, -9000, 9000)

            azim_no_name_list = list(set(tnames('*azim_no_?' + suffix)).intersection(loaded_data))
            number_string_list = []
            for azim_no_name in azim_no_name_list:
                number_string_list.append(azim_no_name.split('_')[4][0])

            for number_string in number_string_list:

                site_input_upper = site_input.upper()
                #  ;Set labels for some tplot variables
                options(prefix + 'pwr_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'pwr_' + number_string + suffix, 'ztitle', 'Backscatter power [dB]')
                options(prefix + 'pwr_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'pwr_err_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'pwr_err_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'pwr_err_' + number_string + suffix, 'ztitle', 'power err [dB]')
                options(prefix + 'spec_width_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'spec_width_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'spec_width_' + number_string + suffix, 'ztitle', 'Spec. width [m/s]')
                options(prefix + 'spec_width_err_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'spec_width_err_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'spec_width_err_' + number_string + suffix, 'ztitle', 'Spec. width err [m/s]')

                if not prefix+'vlos_' + number_string + suffix in loaded_data:
                    vlos_notplot_dictionary = load(pathformat=pathformat, file_res=file_res, trange=trange, prefix=prefix,suffix=suffix, get_support_data=get_support_data,
                            varformat='vlos_' + number_string, downloadonly=downloadonly, notplot=True, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
                    vlos_tplot_name = prefix+'vlos_' + number_string + suffix
                    if len(vlos_notplot_dictionary) > 0:
                        store_data(vlos_tplot_name,
                                data={'x':vlos_notplot_dictionary[vlos_tplot_name]['x'],
                                    'y':vlos_notplot_dictionary[vlos_tplot_name]['y'],
                                    'v1':vlos_notplot_dictionary[vlos_tplot_name]['v'],
                                    'v2':np.arange(vlos_notplot_dictionary[vlos_tplot_name]['y'].shape[2])},
                                attr_dict={'CDF':vlos_notplot_dictionary[vlos_tplot_name]['CDF']})

                        clip(vlos_tplot_name, -9000, 9000)
                        options(vlos_tplot_name, 'spec', 1)
                        loaded_data.append(vlos_tplot_name)
                options(prefix + 'vlos_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'vlos_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'vlos_' + number_string + suffix, 'ztitle', 'Doppler velocity [m/s]')

                options(prefix + 'vlos_err_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'vlos_err_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'vlos_err_' + number_string + suffix, 'ztitle', 'Vlos err [m/s]')
                if prefix + 'elev_angle_' + number_string + suffix in loaded_data:  # need to get_support_data=True
                    options(prefix + 'elev_angle_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                    options(prefix + 'elev_angle_' + number_string + suffix, 'ysubtitle', '[range gate]')
                    options(prefix + 'elev_angle_' + number_string + suffix, 'ztitle', 'Elev. angle [deg]')
                options(prefix + 'echo_flag_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'echo_flag_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'echo_flag_' + number_string + suffix, 'ztitle', '1: iono. echo')
                options(prefix + 'quality_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'quality_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'quality_' + number_string + suffix, 'ztitle', 'quality')
                options(prefix + 'quality_flag_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'quality_flag_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'quality_flag_' + number_string + suffix, 'ztitle', 'quality flg')

                #;Split vlos_? tplot variable into 3 components
                get_data_vlos = get_data(prefix + 'vlos_' + number_string + suffix)
                get_metadata_vlos = get_data(prefix + 'vlos_' + number_string + suffix, metadata=True)
                store_data(prefix + 'vlos_' + number_string + suffix,
                            data={'x':get_data_vlos[0],
                                  'y':get_data_vlos[1][:, :, 2],
                                  'v':get_data_vlos[2]},
                            attr_dict=get_metadata_vlos)
                options(prefix + 'vlos_' + number_string + suffix, 'ztitle', 'LOS Doppler vel. [m/s]')
                store_data(prefix + 'vnorth_' + number_string + suffix,
                            data={'x':get_data_vlos[0],
                                  'y':get_data_vlos[1][:, :, 0],
                                  'v':get_data_vlos[2]},
                            attr_dict=get_metadata_vlos)
                options(prefix + 'vnorth_' + number_string + suffix, 'ztitle', 'LOS V Northward [m/s]')
                loaded_data.append(prefix + 'vnorth_' + number_string + suffix)
                store_data(prefix + 'veast_' + number_string + suffix,
                            data={'x':get_data_vlos[0],
                                  'y':get_data_vlos[1][:, :, 1],
                                  'v':get_data_vlos[2]},
                            attr_dict=get_metadata_vlos)
                options(prefix + 'veast_' + number_string + suffix, 'ztitle', 'LOS V Eastward [m/s]')
                loaded_data.append(prefix + 'veast_' + number_string + suffix)

                #;Combine iono. echo and ground echo for vlos
                v_var_names = ['vlos_','vnorth_','veast_']
                flag_data = get_data(prefix + 'echo_flag_' + number_string + suffix)
                for v_var in v_var_names:
                    v_var_data = get_data(prefix + v_var + number_string + suffix)
                    v_var_metadata = get_data(prefix + v_var + number_string + suffix, metadata=True)
                    g_data_y = np.where(flag_data[1] == 1., np.nan, v_var_data[1])
                    v_var_data_y = np.where(flag_data[1] != 1., np.nan, v_var_data[1])
                    max_rg = np.nanmax(v_var_data[2]) + 1
                    store_data(prefix + v_var + 'iscat_' + number_string + suffix,
                            data={'x':v_var_data[0],
                                  'y':v_var_data_y,
                                  'v':v_var_data[2]},
                            attr_dict=v_var_metadata)
                    options(prefix + v_var + 'iscat_' + number_string + suffix, 'ytitle', ' ')
                    options(prefix + v_var + 'iscat_' + number_string + suffix, 'ysubtitle', ' ')
                    options(prefix + v_var + 'iscat_' + number_string + suffix, 'ztitle', ' ')
                    options(prefix + v_var + 'iscat_' + number_string + suffix, 'spec', 1)
                    loaded_data.append(prefix + v_var + 'iscat_' + number_string + suffix)
                    metadata_for_gscat = deepcopy(v_var_metadata)
                    metadata_for_gscat['plot_options']['extras']['fill_color'] = 5  #options like, 'fill_color:5' in IDL, have not implemented.
                    store_data(prefix + v_var + 'gscat_' + number_string + suffix,
                            data={'x':v_var_data[0],
                                  'y':g_data_y,
                                  'v':v_var_data[2]},
                            attr_dict=metadata_for_gscat)
                    options(prefix + v_var + 'gscat_' + number_string + suffix, 'ytitle', ' ')
                    options(prefix + v_var + 'gscat_' + number_string + suffix, 'ysubtitle', ' ')
                    options(prefix + v_var + 'gscat_' + number_string + suffix, 'ztitle', ' ')
                    options(prefix + v_var + 'gscat_' + number_string + suffix, 'spec', 1)
                    loaded_data.append(prefix + v_var + 'gscat_' + number_string + suffix)
                    store_data(prefix + v_var + 'bothscat_' + number_string + suffix,
                            data=[prefix + v_var + 'iscat_' + number_string + suffix,
                                  prefix + v_var + 'gscat_' + number_string + suffix])
                    options(prefix + v_var + 'bothscat_' + number_string + suffix, 'yrange', [0,max_rg])
                    loaded_data.append(prefix + v_var + 'bothscat_' + number_string + suffix)
                    """
                    Currently, '*iscat_*' and '*bothscat_*' are almost same plot outputs.
                    Because, options like, 'fill_color:5' of IDL for '*gscat_*' have not implemented.
                    """

                #;Set the z range explicitly for some tplot variables
                zlim(prefix + 'pwr_' + number_string + suffix, 0., 30.)
                zlim(prefix + 'pwr_err_' + number_string + suffix, 0., 30.)
                zlim(prefix + 'spec_width_' + number_string + suffix, 0., 200.)
                zlim(prefix + 'spec_width_err_' + number_string + suffix, 0., 300.)
                
                # zlim for '*vlos_*scat_*'
                t_names_raw = tnames(prefix + 'vlos_*scat_' + number_string + suffix)
                t_names_remove_space = [t_name.split(' ')[0] for t_name in t_names_raw]
                t_plot_name_list = list(set(t_names_remove_space).intersection(loaded_data))
                for t_plot_name in t_plot_name_list:
                    zlim(t_plot_name, -400., 400.)
                
                # zlim for '*vnorth_*scat_*'
                t_names_raw = tnames(prefix + 'vnorth_*scat_' + number_string + suffix)
                t_names_remove_space = [t_name.split(' ')[0] for t_name in t_names_raw]
                t_plot_name_list = list(set(t_names_remove_space).intersection(loaded_data))
                for t_plot_name in t_plot_name_list:
                    zlim(t_plot_name, -400., 400.)
                
                # zlim for '*veast_*scat_*'
                t_names_raw = tnames(prefix + 'veast_*scat_' + number_string + suffix)
                t_names_remove_space = [t_name.split(' ')[0] for t_name in t_names_raw]
                t_plot_name_list = list(set(t_names_remove_space).intersection(loaded_data))
                for t_plot_name in t_plot_name_list:
                    zlim(t_plot_name, -400., 400.)
                
                zlim(prefix + 'vlos_err_' + number_string + suffix, 0., 300.)

                # ;Fill values --> NaN
                get_data_vars_pwr = get_data(prefix + 'pwr_' + number_string + suffix)
                if get_data_vars_pwr is not None:
                    pwr_y = deepcopy(get_data_vars_pwr[1])
                    indices_array_tuple = np.where(np.isfinite(pwr_y) == False)
                    var_name_list = ['echo_flag_', 'quality_', 'quality_flag_']
                    for var_name in var_name_list:
                        t_plot_name = prefix + var_name + number_string + suffix
                        get_data_vars = get_data(t_plot_name)
                        get_metadata_vars = get_data(t_plot_name, metadata=True)
                        if get_data_vars is not None:
                            val_array = deepcopy(get_data_vars[1].astype(np.float64))
                            val_array[indices_array_tuple] = np.nan
                            store_data(t_plot_name, data={'x':get_data_vars[0],
                                                        'y':val_array,
                                                        'v':get_data_vars[2]},
                                    attr_dict=get_metadata_vars)

                #;Reassign scan numbers for the combined data
                if (prefix + 'scanstartflag_' + number_string + suffix in loaded_data)\
                   and (prefix + 'scanno_' + number_string + suffix in loaded_data):  # need to get_support_data=True
                    t_plot_name = prefix + 'scanstartflag_' + number_string + suffix
                    scanstartflag_data = get_data(t_plot_name)
                    if scanstartflag_data is not None:
                        scflg = abs(scanstartflag_data[1])
                        try:
                            scno = np.full(shape=scflg.shape, fill_value=-1, dtype=np.int64)
                        except:
                            scno = np.full(shape=scflg.shape, fill_value=-1, dtype=np.int32)
                        scno_t = 0
                        scno[0] = scno_t
                        gt_1_indices_array = np.where(scflg > 0)[0]
                        for i in range(gt_1_indices_array.size - 1):
                            scno[gt_1_indices_array[i]:gt_1_indices_array[i+1]] = i
                        scno[gt_1_indices_array[i+1]:] = i + 1
                        t_plot_name = prefix + 'scanno_' + number_string + suffix
                        get_data_var_scanno = get_data(t_plot_name)
                        if get_data_var_scanno is not None:
                            get_metadata_var_scanno = get_data(t_plot_name, metadata=True)
                            store_data(t_plot_name, data={'x':get_data_var_scanno[0],
                                                          'y':scno},
                                                    attr_dict=get_metadata_var_scanno)

    return loaded_data
