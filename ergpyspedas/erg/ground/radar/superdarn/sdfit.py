import cdflib
import numpy as np

from copy import deepcopy
from pytplot import get_data, store_data, options, clip, ylim
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

                        loaded_data.append(vlos_tplot_name)
                options(prefix + 'vlos_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'vlos_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'vlos_' + number_string + suffix, 'ztitle', 'Doppler velocity [m/s]')

                options(prefix + 'vlos_err_' + number_string + suffix, 'ytitle', site_input_upper+'\nall beams')
                options(prefix + 'vlos_err_' + number_string + suffix, 'ysubtitle', '[range gate]')
                options(prefix + 'vlos_err_' + number_string + suffix, 'ztitle', 'Vlos err [m/s]')
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


    return loaded_data
