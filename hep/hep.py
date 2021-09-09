#from pyspedas.erg.load import load
from load import load
import numpy as np
from pytplot import options, clip, ylim, zlim, store_data
import cdflib

def hep(trange=['2017-03-27', '2017-03-28'],
        datatype='omniflux', 
        level='l2', 
        suffix='',  
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
        version=None):
    """
    This function loads data from the HEP experiment from the Arase mission
    
    Parameters:
        trange : list of str
            time range of interest [starttime, endtime] with the format 
            'YYYY-MM-DD','YYYY-MM-DD'] or to specify more or less than a day 
            ['YYYY-MM-DD/hh:mm:ss','YYYY-MM-DD/hh:mm:ss']

        datatype: str
            Data type; Valid options:

        level: str
            Data level; Valid options:

        suffix: str
            The tplot variable names will be given this suffix.  By default, 
            no suffix is added.

        get_support_data: bool
            Data with an attribute "VAR_TYPE" with a value of "support_data"
            will be loaded into tplot.  By default, only loads in data with a 
            "VAR_TYPE" attribute of "data".

        varformat: str
            The file variable formats to load into tplot.  Wildcard character
            "*" is accepted.  By default, all variables are loaded in.

        varnames: list of str
            List of variable names to load (if not specified,
            all data variables are loaded)

        downloadonly: bool
            Set this flag to download the CDF files, but not load them into 
            tplot variables

        notplot: bool
            Return the data in hash tables instead of creating tplot variables

        no_update: bool
            If set, only load data from your local cache

        time_clip: bool
            Time clip the variables to exactly the range specified in the trange keyword

        ror: bool
            If set, print PI info and rules of the road

        version: str
            Set this value to specify the version of cdf files (such as "v01_02", "v01_03", ...)

    Returns:
        List of tplot variables created.

    """
    
    file_res=3600. * 24
    prefix = 'erg_hep_'+level+'_'

    if level == 'l2':
        pathformat = 'satellite/erg/hep/'+level+'/'+datatype+'/%Y/%m/erg_hep_'+level+'_'+datatype +'_%Y%m%d_'
        if version == None:
            pathformat += 'v??_??.cdf'
        else:
            pathformat += version + '.cdf'
    if level == 'l3':
        pathformat = 'satellite/erg/hep/'+level+'/pa/%Y/%m/erg_hep_'+level+'_pa_%Y%m%d_'
        if version == None:
            pathformat += 'v??_??.cdf'
        else:
            pathformat += version + '.cdf'


    if level == 'l2' and datatype == 'omniflux' or datatype == '3dflux' or level == 'l3':
        notplot=True # to avoid failure of creation plot variables (at store_data.py) of hep 

    loaded_data = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd, version=version)


    
    if len(loaded_data) > 0 and ror:

    
        out_files = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd, version=version)
        cdf_file = cdflib.CDF(out_files[0])
        
        try:
            gatt = cdf_file.globalattsget()
        except:
            gatt = None

        
        if gatt is not None:
            # --- print PI info and rules of the road

            print(' ')
            print('**************************************************************************')
            print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
            print('')
            print('PI: ', gatt['PI_NAME'])
            print("Affiliation: "+gatt["PI_AFFILIATION"])
            print('')
            print('- The rules of the road (RoR) common to the ERG project:')
            print('       https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
            print('- RoR for HEP data: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Hep')
            if level == 'l3':
                print('- RoR for MGF data: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Mgf')
            print('')
            print('Contact: erg_hep_info at isee.nagoya-u.ac.jp')
            print('**************************************************************************')



    if type(loaded_data) is dict:

        if level == 'l2' and datatype == 'omniflux':
            tplot_variables = []
            if 'erg_hep_l2_FEDO_L' + suffix in loaded_data:
                v_vars_min = loaded_data['erg_hep_l2_FEDO_L' + suffix]['v'][0]
                v_vars_max = loaded_data['erg_hep_l2_FEDO_L' + suffix]['v'][1]
                v_vars = np.power(10., (np.log10(v_vars_min) + np.log10(v_vars_max)) / 2.) # log average of energy bins
                store_data('erg_hep_l2_FEDO_L' + suffix, data={'x':loaded_data['erg_hep_l2_FEDO_L' + suffix]['x'], 
                                                    'y':loaded_data['erg_hep_l2_FEDO_L' + suffix]['y'],
                                                    'v':v_vars})
                tplot_variables.append('erg_hep_l2_FEDO_L' + suffix)

            if 'erg_hep_l2_FEDO_H' + suffix in loaded_data:
                v_vars_min = loaded_data['erg_hep_l2_FEDO_H' + suffix]['v'][0]
                v_vars_max = loaded_data['erg_hep_l2_FEDO_H' + suffix]['v'][1]
                v_vars = np.power(10., (np.log10(v_vars_min) + np.log10(v_vars_max)) / 2.) # log average of energy bins
                store_data('erg_hep_l2_FEDO_H' + suffix, data={'x':loaded_data['erg_hep_l2_FEDO_H' + suffix]['x'], 
                                                    'y':loaded_data['erg_hep_l2_FEDO_H' + suffix]['y'],
                                                    'v':v_vars})
                tplot_variables.append('erg_hep_l2_FEDO_H' + suffix)
            

            # remove minus valuse of y array
            if 'erg_hep_l2_FEDO_L' + suffix in tplot_variables:
                clip('erg_hep_l2_FEDO_L' + suffix, 0., 1.0e+10)
            if 'erg_hep_l2_FEDO_H' + suffix in tplot_variables:
                clip('erg_hep_l2_FEDO_H' + suffix, 0., 1.0e+10)

            # set spectrogram plot option
            options('erg_hep_l2_FEDO_L' + suffix, 'Spec', 1)
            options('erg_hep_l2_FEDO_H' + suffix, 'Spec', 1)

            # set y axis to logscale
            options('erg_hep_l2_FEDO_L' + suffix, 'ylog', 1)
            options('erg_hep_l2_FEDO_H' + suffix, 'ylog', 1)

            # set yrange
            options('erg_hep_l2_FEDO_L' + suffix, 'yrange', [3.0e+01, 2.0e+03])
            options('erg_hep_l2_FEDO_H' + suffix, 'yrange', [7.0e+01, 2.0e+03])

            # set ytitle
            options('erg_hep_l2_FEDO_L' + suffix, 'ytitle', 'HEP-L\nomniflux\nLv2\nEnergy')
            options('erg_hep_l2_FEDO_H' + suffix, 'ytitle', 'HEP-L\nomniflux\nLv2\nEnergy')

            # set ysubtitle
            options('erg_hep_l2_FEDO_L' + suffix, 'ysubtitle', '[keV]')
            options('erg_hep_l2_FEDO_H' + suffix, 'ysubtitle', '[keV]')

            # set ylim
            if 'erg_hep_l2_FEDO_L' + suffix in tplot_variables:
                ylim('erg_hep_l2_FEDO_L' + suffix, 30, 1800)
            if 'erg_hep_l2_FEDO_H' + suffix in tplot_variables:
                ylim('erg_hep_l2_FEDO_H' + suffix, 500, 2048)

            # set z axis to logscale
            options('erg_hep_l2_FEDO_L' + suffix, 'zlog', 1)
            options('erg_hep_l2_FEDO_H' + suffix, 'zlog', 1)

            # set zrange
            options('erg_hep_l2_FEDO_L' + suffix, 'zrange', [1.0e-15, 1.0e+06])
            options('erg_hep_l2_FEDO_H' + suffix, 'zrange', [1.0e-10, 1.0e+5])

            # set ztitle
            options('erg_hep_l2_FEDO_L' + suffix, 'ztitle', '[/cm^{2}-str-s-keV]')
            options('erg_hep_l2_FEDO_H' + suffix, 'ztitle', '[/cm^{2}-str-s-keV]')

            # set zlim
            if 'erg_hep_l2_FEDO_L' + suffix in tplot_variables:
                zlim('erg_hep_l2_FEDO_L' + suffix, 1e+0, 1e+5)
            if 'erg_hep_l2_FEDO_H' + suffix in tplot_variables:
                zlim('erg_hep_l2_FEDO_H' + suffix, 1e+0, 1e+5)

            # change colormap option
            options('erg_hep_l2_FEDO_L' + suffix,  'Colormap', 'jet')
            options('erg_hep_l2_FEDO_H' + suffix,  'Colormap', 'jet')

            return  tplot_variables

        if level == 'l2' and datatype == '3dflux':
           tplot_variables = []
           v2_array = [i for i in range(15)]

           if 'erg_hep_l2_FEDU_L' + suffix in loaded_data:

               store_data('erg_hep_l2_FEDU_L' + suffix, data={'x':loaded_data['erg_hep_l2_FEDU_L' + suffix]['x'],
                                                        'y':loaded_data['erg_hep_l2_FEDU_L' + suffix]['y'],
                                                        'v1':np.sqrt(loaded_data['erg_hep_l2_FEDU_L' + suffix]['v'][0,:]*
                                                        loaded_data['erg_hep_l2_FEDU_L' + suffix]['v'][1,:]), # geometric mean for 'v1'
                                                        'v2':v2_array})
               tplot_variables.append('erg_hep_l2_FEDU_L' + suffix)
               clip('erg_hep_l2_FEDU_L' + suffix, -1.0e+10, 1.0e+10)

           if 'erg_hep_l2_FEDU_H' + suffix in loaded_data:

               store_data('erg_hep_l2_FEDU_H' + suffix, data={'x':loaded_data['erg_hep_l2_FEDU_H' + suffix]['x'],
                                                        'y':loaded_data['erg_hep_l2_FEDU_H' + suffix]['y'],
                                                        'v1':np.sqrt(loaded_data['erg_hep_l2_FEDU_H' + suffix]['v'][0,:]*
                                                        loaded_data['erg_hep_l2_FEDU_H' + suffix]['v'][1,:]), # geometric mean for 'v1'
                                                        'v2':v2_array})
               tplot_variables.append('erg_hep_l2_FEDU_H' + suffix)
               clip('erg_hep_l2_FEDU_H' + suffix, -1.0e+10, 1.0e+10)

           return tplot_variables



        if level == 'l3': # implementation for level = 'l3'

           tplot_variables = []

           if 'erg_hep_l3_FEDU_L' + suffix in loaded_data:

               L_energy_array_ave = np.sqrt(loaded_data['erg_hep_l3_FEDU_L' + suffix]['v1'][0,:]*
                                            loaded_data['erg_hep_l3_FEDU_L' + suffix]['v1'][1,:]) # geometric mean for 'v1'

               # get energy [keV] array for ytitle options
               L_energy_array = np.trunc(L_energy_array_ave).astype(int)

               store_data('erg_hep_l3_FEDU_L' + suffix, data={'x':loaded_data['erg_hep_l3_FEDU_L' + suffix]['x'],
                                                  'y':loaded_data['erg_hep_l3_FEDU_L' + suffix]['y'],
                                                  'v1':L_energy_array_ave,
                                                  'v2':loaded_data['erg_hep_l3_FEDU_L' + suffix]['v2']})
               # set ylim
               ylim('erg_hep_l3_FEDU_L' + suffix, 0, 180)
               # set zlim
               zlim('erg_hep_l3_FEDU_L' + suffix, 1e+2, 1e+6)
               
               tplot_variables.append('erg_hep_l3_FEDU_L' + suffix)

               


               for i in range(loaded_data['erg_hep_l3_FEDU_L' + suffix]['y'].shape[1]): # make Tplot Variables of erg_hep_l3_FEDU_L_paspec_ene?? (??: 00, 01, 02, ..., 15)
                    tplot_name = 'erg_hep_l3_FEDU_L_paspec_ene' + str(i).zfill(2) + suffix
                    store_data(tplot_name, data={'x':loaded_data['erg_hep_l3_FEDU_L' + suffix]['x'],
                                                'y':loaded_data['erg_hep_l3_FEDU_L' + suffix]['y'][:,i,:],
                                                'v':loaded_data['erg_hep_l3_FEDU_L' + suffix]['v2']})

                    # set ylim
                    ylim(tplot_name, 0, 180)
                    # set zlim
                    zlim(tplot_name, 1e+2, 1e+6)
                    # set ytitle
                    options(tplot_name, 'ytitle', f'HEP-L\nEne{str(i).zfill(2)}\n{L_energy_array[i]} keV')

                    tplot_variables.append(tplot_name)

           if 'erg_hep_l3_FEDU_H' + suffix in loaded_data:

               H_energy_array_ave = np.sqrt(loaded_data['erg_hep_l3_FEDU_H' + suffix]['v1'][0,:]*
                                            loaded_data['erg_hep_l3_FEDU_H' + suffix]['v1'][1,:]) # geometric mean for 'v1'

               # get energy [keV] array for ytitle options
               H_energy_array = np.trunc(H_energy_array_ave).astype(int)

               store_data('erg_hep_l3_FEDU_H' + suffix, data={'x':loaded_data['erg_hep_l3_FEDU_H' + suffix]['x'],
                                                  'y':loaded_data['erg_hep_l3_FEDU_H' + suffix]['y'],
                                                  'v1':H_energy_array_ave,
                                                  'v2':loaded_data['erg_hep_l3_FEDU_H' + suffix]['v2']})
               # set ylim
               ylim('erg_hep_l3_FEDU_H' + suffix, 0, 180)
               # set zlim
               zlim('erg_hep_l3_FEDU_H' + suffix, 1e+1, 1e+4)
               
               tplot_variables.append('erg_hep_l3_FEDU_H' + suffix)


               for i in range(loaded_data['erg_hep_l3_FEDU_H' + suffix]['y'].shape[1]): # make Tplot Variables of erg_hep_l3_FEDU_H_paspec_ene?? (??: 00, 01, 02, ..., 10)
                    tplot_name = 'erg_hep_l3_FEDU_H_paspec_ene' + str(i).zfill(2) + suffix
                    store_data(tplot_name, data={'x':loaded_data['erg_hep_l3_FEDU_H' + suffix]['x'],
                                                'y':loaded_data['erg_hep_l3_FEDU_H' + suffix]['y'][:,i,:],
                                                'v':loaded_data['erg_hep_l3_FEDU_H' + suffix]['v2']})
                    
                    # set ylim
                    ylim(tplot_name, 0, 180)
                    # set zlim
                    zlim(tplot_name, 1e+1, 1e+4)
                    # set ytitle
                    options(tplot_name, 'ytitle', f'HEP-H\nEne{str(i).zfill(2)}\n{H_energy_array[i]} keV')

                    tplot_variables.append(tplot_name)
           
           
           # set z axis to logscale
           options(tplot_variables, 'zlog', 1)
           # set spectrogram plot option
           options(tplot_variables, 'spec', 1)
           # change colormap option
           options(tplot_variables, 'colormap', 'jet')
           # set ysubtitle
           options(tplot_variables, 'ysubtitle', 'PA [deg]')
           # set ztitle
           options(tplot_variables, 'ztitle', '[/keV/cm^{2}/sr/s]')

           return tplot_variables

    return loaded_data
