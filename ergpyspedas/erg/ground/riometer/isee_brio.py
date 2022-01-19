import cdflib
import numpy as np

from pytplot import get_data, store_data, options, clip, ylim

from ...satellite.erg.load import load


def isee_brio(
    trange=['2020-08-01', '2020-08-02'],
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

    #;----- datatype -----;
    datatype='64hz'
    instr='brio'
    freq='30'
    
    site_code_all = ['ath', 'kap', 'gak', 'hus', 'zgn', 'ist']
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

    prefix = 'iseetmp_'
    if notplot:
        loaded_data = {}
    else:
        loaded_data = []
    for site_input in site_code:
        fres = datatype
        file_res = 3600. * 24
        pathformat = 'ground/riometer/'+site_input\
                        +'/%Y/isee_'+fres+'_'+instr+freq+'_'+site_input+'_%Y%m%d_v??.cdf'
        
        loaded_data_temp = load(pathformat=pathformat, file_res=file_res, trange=trange, datatype=datatype, prefix=prefix, suffix=suffix, get_support_data=get_support_data,
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
                print('printing PI info and rules of the road was failed')"""
            
        if (not downloadonly) and (not notplot):
            for t_plot_name in loaded_data_temp:
                get_data_vars = get_data(t_plot_name)
                if get_data_vars is None:
                    store_data(t_plot_name, delete=True)
                else:
                    t_plot_name_split =t_plot_name.split('_')
                    if len(t_plot_name_split) > 2:
                        #;----- Find param -----;
                        param = t_plot_name_split[1]
                        if param in ['cna', 'qdc', 'raw']:
                            #;----- Rename tplot variables -----;
                            new_tplot_name = 'isee_brio'+freq+'_'+site_input+'_'+fres+'_'+param + suffix
                            store_data(t_plot_name, newname=new_tplot_name)
                            loaded_data.remove(t_plot_name)
                            loaded_data.append(new_tplot_name)
                            #;----- Missing data -1.e+31 --> NaN -----;
                            clip(new_tplot_name, -1e+5, 1e+5)
                            get_data_vars = get_data(new_tplot_name)
                            ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            #;----- Set options -----;
                            options(new_tplot_name, 'ytitle', site_input.upper())
                            if param == 'cna':
                                options(new_tplot_name, 'ysubtitle', '[dB]')
                                options(new_tplot_name, 'legend_names', ['CNA'])
                            elif param == 'qdc':
                                options(new_tplot_name, 'ysubtitle', '[V]')
                                options(new_tplot_name, 'legend_names', ['QDC'])
                            elif param == 'raw':
                                options(new_tplot_name, 'ysubtitle', '[V]')
                                options(new_tplot_name, 'legend_names', ['Raw data'])

    return loaded_data
