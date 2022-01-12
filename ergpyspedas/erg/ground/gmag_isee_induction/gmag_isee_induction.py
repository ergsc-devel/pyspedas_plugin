import cdflib
import numpy as np

from pytplot import get_data, store_data, options, clip

from ...satellite.erg.load import load


def gmag_isee_induction(
    trange=['2008-02-28/00:00:00','2008-02-28/02:00:00'],
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

    site_code_all = ['ath', 'gak', 'hus', 'kap', 'lcl', 'mgd', 'msr', 'nai', 'ptk', 'rik', 'sta', 'zgn']


    if isinstance(site, str):
        if site == 'all':
            site_code = site_code_all
        else:
            site_code = site.lower()
            site_code = site.split(' ')
    elif isinstance(site, list):
        site_code = []
        for i in range(len(site)):
            site_code.append(site[i].lower())
    site_code = list(set(site_code).intersection(site_code_all))

    prefix = 'isee_induction_'
    if notplot:
        loaded_data = {}
    else:
        loaded_data = []
    
    for site_input in site_code:

        file_res = 3600.
        pathformat = 'ground/geomag/isee/induction/'+site_input\
                        +'/%Y/%m/isee_induction_'+site_input+'_%Y%m%d%H_v??.cdf'

        if notplot:
            loaded_data.update(load(pathformat=pathformat, file_res=file_res, trange=trange, prefix=prefix, suffix='_'+site_input+suffix, get_support_data=get_support_data,
                        varformat=varformat, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd))
        else:
            loaded_data += load(pathformat=pathformat, file_res=file_res, trange=trange, prefix=prefix, suffix='_'+site_input+suffix, get_support_data=get_support_data,
                        varformat=varformat, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
        if (len(loaded_data) > 0) and ror:
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
            
        """if (not downloadonly) and (not notplot):
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
                        store_data(prefix+'hdz_'+fres_in+'_' + site_input+suffix, newname=new_tplot_name)
                        clip(new_tplot_name, -1e+4, 1e+4)
                        options(new_tplot_name, 'legend_names', ['H','D','Z'])
                        options(new_tplot_name, 'Color', ['b', 'g', 'r'])
                        options(new_tplot_name, 'ytitle', '\n'.join(new_tplot_name.split('_')))"""


    return loaded_data
