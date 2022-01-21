import cdflib
import numpy as np

from pytplot import get_data, store_data, options, clip, ylim

from ...satellite.erg.load import load


def camera_omti_asi(
    trange=['2020-08-01', '2020-08-02'],
    suffix='',
    site='all',
    wavelength=[5577],
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

    site_code_all = ['abu', 'ath', 'drw', 'eur', 'gak', 'hlk',
                     'hus', 'isg', 'ist', 'ith', 'kap', 'ktb',
                     'mgd', 'nai', 'nyr', 'ptk', 'rik', 'rsb',
                     'sgk', 'sta', 'syo', 'trs', 'yng']

    if isinstance(wavelength, str):
        wavelengthc = wavelength.split(' ')
    elif isinstance(wavelength, int):
        wavelengthc = [str(wavelength)]
    elif isinstance(wavelength, list):
        wavelengthc = []
        for i in range(len(wavelength)):
            wavelengthc.append(str(wavelength[i]))

    if isinstance(site, str):
        site_code = site.lower()
        site_code = site_code.split(' ')
    elif isinstance(site, list):
        site_code = []
        for i in range(len(site)):
            site_code.append(site[i].lower())
    if 'all' in site_code:
        site_code = site_code_all
    
    site_code = list(set(site_code).intersection(site_code_all))

    
    if notplot:
        loaded_data = {}
    else:
        loaded_data = []
    for site_input in site_code:
        for wavelength_in in wavelengthc:
            prefix = 'omti_asi_'+site_input+'_'+wavelength_in+'_'
            file_res = 3600.
            pathformat = 'ground/camera/omti/asi/'+site_input\
                            +'/%Y/%m/%d/omti_asi_c??_'+site_input+'_'+wavelength_in+'_%Y%m%d%H_v??.cdf'

            loaded_data_temp = load(pathformat=pathformat, file_res=file_res, trange=trange, prefix=prefix, suffix='_'+site_input+suffix, get_support_data=get_support_data,
                            varformat=varformat, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
            
            if notplot:
                loaded_data.update(loaded_data_temp)
            else:
                loaded_data += loaded_data_temp
            """if (len(loaded_data_temp) > 0) and ror:
                try:
                    if isinstance(loaded_data_temp, list):
                        if downloadonly:
                            cdf_file = cdflib.CDF(loaded_data_temp[-1])
                            gatt = cdf_file.globalattsget()
                        else:
                            gatt = get_data(loaded_data_temp[-1], metadata=True)['CDF']['GATT']
                    elif isinstance(loaded_data_temp, dict):
                        gatt = loaded_data_temp[list(loaded_data_temp.keys())[-1]]['CDF']['GATT']
                    print('**************************************************************************')
                    print(gatt["Logical_source_description"])
                    print('')
                    print(f'Information about {gatt["Station_code"]}')
                    print('PI and Host PI(s):')
                    print(gatt["PI_name"])
                    print('')
                    print('Affiliations: ')
                    print(gatt["PI_affiliation"])
                    print('')
                    print('Rules of the Road for ISEE Fluxgate Data Use:')
                    for gatt_text in gatt["TEXT"]:
                        print(gatt_text)
                    print(f'{gatt["LINK_TEXT"]} {gatt["HTTP_LINK"]}')
                    print('**************************************************************************')
                except:
                    print('printing PI info and rules of the road was failed')
                
            if (not downloadonly) and (not notplot):
                if fres == '1min':
                    fres_list = ['1min', '1h']
                else:
                    fres_list = [fres]
                for fres_in in fres_list:
                    current_tplot_name = prefix+'hdz_'+fres_in+'_' + site_input+suffix
                    if current_tplot_name in loaded_data:
                        get_data_vars = get_data(current_tplot_name)
                        if get_data_vars is None:
                            store_data(current_tplot_name, delete=True)
                        else:
                            new_tplot_name = prefix+'mag_'+site_input+'_'+fres_in+'_hdz'+suffix
                            store_data(current_tplot_name, newname=new_tplot_name)
                            loaded_data.remove(current_tplot_name)
                            loaded_data.append(new_tplot_name)
                            clip(new_tplot_name, -1e+4, 1e+4)
                            get_data_vars = get_data(new_tplot_name)
                            ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            options(new_tplot_name, 'legend_names', ['H','D','Z'])
                            options(new_tplot_name, 'Color', ['b', 'g', 'r'])
                            options(new_tplot_name, 'ytitle', '\n'.join(new_tplot_name.split('_')))
"""

    return loaded_data
