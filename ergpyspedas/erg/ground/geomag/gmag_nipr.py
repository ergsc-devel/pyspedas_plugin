import cdflib
import numpy as np

from pyspedas.utilities.time_double import time_double
from pyspedas.analysis.time_clip import time_clip as tclip
from pyspedas.utilities.dailynames import dailynames
from pyspedas.utilities.download import download

from pytplot import get_data, store_data, options, clip, ylim, cdf_to_tplot

from ...satellite.erg.load import load


def gmag_nipr(
    trange=['2020-08-01', '2020-08-02'],
    suffix='',
    site='all',
    datatype='all',
    get_support_data=False,
    varformat=None,
    varnames=[],
    downloadonly=False,
    notplot=False,
    no_update=False,
    uname=None,
    passwd=None,
    time_clip=False,
    ror=True,
    fproton=False
):

    site_code_all = ['syo', 'hus', 'tjo', 'aed', 'isa', 'h57', 'amb', 'srm', 'ihd', 'skl', 'h68']
    tres_all=['1sec']
    if isinstance(datatype, str):
        datatype = datatype.lower()
        datatype = datatype.split(' ')
    elif isinstance(datatype, list):
        for i in range(len(datatype)):
            datatype[i] = datatype[i].lower()

    if 'all' in datatype:
        datatype=tres_all
    datatype = list(set(datatype).intersection(tres_all))
    if len(datatype) < 1:
        return

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
    instr='fmag'
    trange_0 = time_double(trange[0])
    prefix = 'nipr_'
    if notplot:
        loaded_data = {}
    else:
        loaded_data = []
    
    for site_input in site_code:
        for data_type_in in datatype:
            if data_type_in == '1sec':
                if site_input == 'syo':
                    crttime = time_double('1998-01-01')
                    if trange_0 < crttime:
                        fres = '2sec'
                    else:
                        fres = '1sec'
                elif site_input == 'hus':
                    crttime = time_double('2001-09-08')
                    if trange_0 < crttime:
                        fres = '2sec'
                    else:
                        fres = '02hz'
                elif site_input == 'tjo':
                    crttime = time_double('2001-09-12')
                    if trange_0 < crttime:
                        fres = '2sec'
                    else:
                        fres = '02hz'
                elif site_input == 'aed':
                    crttime = time_double('2001-09-27')
                    if trange_0 < crttime:
                        fres = '2sec'
                    else:
                        fres = '02hz'
                elif site_input == 'isa':
                    fres = '2sec'
                else:
                    fres = '1sec'
            else:
                fres = data_type_in

            local_data_dir = 'iugonet/'
            remote_data_dir = 'http://iugonet0.nipr.ac.jp/data/'
            

            pathformat = instr+'/'+site_input+'/'+fres\
                            +'/%Y/nipr_'+fres+'_'+instr+'_'+site_input+'_%Y%m%d_v??.cdf'
            remote_names = dailynames(file_format=pathformat,
                                    trange=trange, res=3600. * 24)

            out_files = []

            files = download(remote_file=remote_names, remote_path=remote_data_dir, local_path=local_data_dir,
                            no_download=no_update, last_version=True, username=uname, password=passwd)
            if files is not None:
                for file in files:
                    out_files.append(file)

            out_files = sorted(out_files)

            if not downloadonly:
                loaded_data_temp = cdf_to_tplot(out_files, prefix=prefix, suffix='_'+site_input+suffix, get_support_data=get_support_data,
                                    varformat=varformat, varnames=varnames, notplot=notplot)

                if notplot:
                    if len(out_files) > 0:
                        cdf_file = cdflib.CDF(out_files[-1])
                        cdf_info = cdf_file.cdf_info()
                        all_cdf_variables = cdf_info['rVariables'] + cdf_info['zVariables']
                        gatt = cdf_file.globalattsget()
                        for var in all_cdf_variables:
                            t_plot_name = prefix + var + suffix
                            if t_plot_name in loaded_data_temp:
                                vatt = cdf_file.varattsget(var)
                                loaded_data_temp[t_plot_name]['CDF'] = {'VATT':vatt,
                                                                        'GATT':gatt,
                                                                        'FILENAME':out_files}
                else:
                    if time_clip:
                        for new_var in loaded_data_temp:
                            tclip(new_var, trange[0], trange[1], suffix='')


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
                """
            if (not downloadonly) and (not notplot):

                current_tplot_name = prefix+'hdz_'+fres+'_' + site_input+suffix
                if current_tplot_name in loaded_data:
                    get_data_vars = get_data(current_tplot_name)
                    if get_data_vars is None:
                        store_data(current_tplot_name, delete=True)
                    else:
                        #;--- Rename
                        new_tplot_name = prefix+'mag_'+site_input+'_'+fres+suffix
                        store_data(current_tplot_name, newname=new_tplot_name)
                        loaded_data.remove(current_tplot_name)
                        loaded_data.append(new_tplot_name)
                        #;--- Missing data -1.e+31 --> NaN
                        clip(new_tplot_name, -1e+5, 1e+5)
                        get_data_vars = get_data(new_tplot_name)
                        ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                        #;--- Labels
                        options(new_tplot_name, 'legend_names', ['H','D','Z'])
                        options(new_tplot_name, 'Color', ['b', 'g', 'r'])
                        options(new_tplot_name, 'ytitle', site_input.upper())
                        options(new_tplot_name, 'ysubtitle', '[nT]')

                #;----- If fproton=True is set, rename tplot variables of f_tres -----;
                if fproton:
                    current_tplot_name = prefix+'f_'+fres+'_' + site_input+suffix
                    if current_tplot_name in loaded_data:
                        get_data_vars = get_data(current_tplot_name)
                        if get_data_vars is None:
                            store_data(current_tplot_name, delete=True)
                        else:
                            #;--- Rename
                            new_tplot_name = prefix+'mag_'+site_input+'_'+fres+'_f' +suffix
                            store_data(current_tplot_name, newname=new_tplot_name)
                            loaded_data.remove(current_tplot_name)
                            loaded_data.append(new_tplot_name)
                            #;--- Missing data -1.e+31 --> NaN
                            clip(new_tplot_name, -1e+5, 1e+5)
                            get_data_vars = get_data(new_tplot_name)
                            if np.all(np.isnan(get_data_vars[1])):
                                ylim(new_tplot_name, 40000, 49000)
                            else:
                                ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            #;--- Labels
                            options(new_tplot_name, 'legend_names', ['F'])
                            options(new_tplot_name, 'ytitle', site_input.upper())
                            options(new_tplot_name, 'ysubtitle', '[nT]')



    return loaded_data
