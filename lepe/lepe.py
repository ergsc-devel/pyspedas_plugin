
#from pyspedas.erg.load import load
from load import load
import numpy as np
from pytplot import options, clip, ylim, zlim, store_data, get_data
import cdflib

def lepe(trange=['2017-04-04', '2017-04-05'],
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
        version = None,
        only_fedu=False,
        et_diagram=False):
    """
    This function loads data from the LEP-e experiment from the Arase mission
    
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
            Set this value to specify the version of cdf files (such as "v02_02")

        only_fedu: bool
            If set, not make erg_lepe_l3_pa_enech_??(??:01,01,..32)_FEDU Tplot Variables

        only_fedu: bool
            If set, make erg_lepe_l3_pa_pabin_??(??:01,01,..16)_FEDU Tplot Variables

    Returns:
        List of tplot variables created.

    """

    if level == 'l3':
        datatype = 'pa'
    
    if (level == 'l2' and datatype == 'omniflux') or (level == 'l2' and datatype == '3dflux') or level == 'l3':
        notplot=True # to avoid failure of creation plot variables (at store_data.py) of lepe
    
    file_res=3600. * 24
    prefix = 'erg_lepe_'+level+'_'+ datatype + '_'
    pathformat = 'satellite/erg/lepe/'+level+'/'+datatype+'/%Y/%m/erg_lepe_'+level+'_'+datatype+'_%Y%m%d_'

    if version == None:
        pathformat += 'v??_??.cdf'
    else:
        pathformat += version + '.cdf'

    loaded_data = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)

    
    if len(loaded_data) > 0 and ror:

    
        out_files = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
        cdf_file = cdflib.CDF(out_files[0])
        gatt = cdf_file.globalattsget()

        # --- print PI info and rules of the road

        print(' ')
        print('**************************************************************************')
        print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
        print('')
        print('Information about ERG LEPe')
        print('')
        print('PI: ', gatt['PI_NAME'])
        print("Affiliation: "+gatt["PI_AFFILIATION"])
        print('')
        print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
        if level == 'l2':
            print('RoR of LEPe L2: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepe')
        if level == 'l3':
            print('RoR of LEPe L3: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepe')
            print('RoR of MGF L2: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Mgf')
        print('')
        print('Contact: erg_lepe_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')


    if type(loaded_data) is dict and len(loaded_data) > 0:
        if (level == 'l2' and datatype == 'omniflux'):
            tplot_variables = []
            v_array = (loaded_data[prefix + 'FEDO' + suffix]['v'][:,0,:] + loaded_data[prefix + 'FEDO' + suffix]['v'][:,1,:])/ 2.
            v_array = np.where(v_array < 0. , np.nan, v_array) # change minus values to NaN
            store_data(prefix + 'FEDO' + suffix, data={'x':loaded_data[prefix + 'FEDO' + suffix]['x'],
                                                'y':loaded_data[prefix + 'FEDO' + suffix]['y'],
                                                'v':v_array})
            tplot_variables.append(prefix + 'FEDO' + suffix)

            # set spectrogram plot option
            options(prefix + 'FEDO' + suffix, 'Spec', 1)
            # change minus values to NaN in y array
            clip(prefix + 'FEDO' + suffix, 0., 2.e+16)

            # set y axis to logscale
            options(prefix + 'FEDO' + suffix, 'ylog', 1)

            # set ylim
            ylim(prefix + 'FEDO' + suffix, 19, 21*1e3)

            # set ytitle
            options(prefix + 'FEDO' + suffix, 'ytitle', 'ERG\nLEP-e\nFEDO\nEnergy')

            # set ysubtitle
            options(prefix + 'FEDO' + suffix, 'ysubtitle', '[eV]')

            # set z axis to logscale
            options(prefix + 'FEDO' + suffix, 'zlog', 1)

            # set zlim
            zlim(prefix + 'FEDO' + suffix,  1, 1e6)

            # set ztitle
            options(prefix + 'FEDO' + suffix, 'ztitle',  '[/cm^{2}-str-s-eV]')

            # change colormap option
            options(prefix + 'FEDO' + suffix, 'Colormap', 'jet')

            return tplot_variables

        if (level == 'l2' and datatype == '3dflux'):
            tplot_variables = []
            
            if prefix + 'FEDU' +suffix in loaded_data:
                store_data(prefix + 'FEDU' +suffix, 
                          data={'x':loaded_data[prefix + 'FEDU' +suffix]['x'],
                                'y':loaded_data[prefix + 'FEDU' +suffix]['y'],
                                'v1':np.sqrt(loaded_data[prefix + 'FEDU' +suffix]['v'][:,0,:]
                                             *loaded_data[prefix + 'FEDU' +suffix]['v'][:,1,:]),# geometric mean
                                'v2':['01', '02', '03', '04', '05', 'A', 'B', '18', '19', '20', '21', '22'],
                                'v3':[i for i in range(16)]})
                    
                tplot_variables.append(prefix + 'FEDU' +suffix)

                options(prefix + 'FEDU' +suffix, 'spec', 1)
                if prefix + 'FEDU' +suffix in tplot_variables:
                    clip(prefix + 'FEDU' +suffix, 0, 21*1e3)
                ylim(prefix + 'FEDU' +suffix, 19, 21*1e3)
                zlim(prefix + 'FEDU' +suffix, 1, 1e6)
                options(prefix + 'FEDU' +suffix, 'zlog', 1)
                options(prefix + 'FEDU' +suffix, 'ylog', 1)
                options(prefix + 'FEDU' +suffix, 'ysubtitle', '[eV]')

                return tplot_variables

        if level == 'l3':
            tplot_variables = []

            if prefix + 'FEDU' +suffix in loaded_data:
                store_data(prefix + 'FEDU' +suffix, 
                            data={'x':loaded_data[prefix + 'FEDU' +suffix]['x'],
                                'y':loaded_data[prefix + 'FEDU' +suffix]['y'],
                                'v1':(loaded_data[prefix + 'FEDU' +suffix]['v1'][:,0,:]
                                        + loaded_data[prefix + 'FEDU' +suffix]['v1'][:,1,:]) / 2.,# arithmetic mean
                                'v2':loaded_data[prefix + 'FEDU' +suffix]['v2']})
                tplot_variables.append(prefix + 'FEDU' +suffix)

                options(prefix + 'FEDU' +suffix, 'spec', 1)
                if prefix + 'FEDU' +suffix in tplot_variables:
                    clip(prefix + 'FEDU' +suffix, 0, 21*1e3)
                ylim(prefix + 'FEDU' +suffix, 19, 21*1e3)
                zlim(prefix + 'FEDU' +suffix, 1, 1e6)
                options(prefix + 'FEDU' +suffix, 'zlog', 1)
                options(prefix + 'FEDU' +suffix, 'ylog', 1)
                options(prefix + 'FEDU' +suffix, 'ysubtitle', '[eV]')

                FEDU_get_data  = get_data(prefix + 'FEDU' +suffix)

                

                if not only_fedu:

                    ytitle_eV_array = np.round(np.nan_to_num(FEDU_get_data[2][0, :]), 2)
                    for i in range(FEDU_get_data[1].shape[1]): # processing for erg_lepe_l3_pa_enech_??(??:01,01,..32)_FEDU
                        tplot_name = prefix + 'enech_' + str(i + 1).zfill(2) +'_FEDU' + suffix
                        store_data(tplot_name,data={'x':FEDU_get_data[0],
                                                'y':FEDU_get_data[1][:,i,:],
                                                    'v':FEDU_get_data[3]})
                        options(tplot_name, 'spec', 1)
                        ylim(tplot_name, 0, 180)
                        zlim(tplot_name, 1, 1e6)
                        options(tplot_name, 'ytitle', 'ERG LEP-e\n' + str(ytitle_eV_array[i]) + ' eV\nPitch angle')
                        tplot_variables.append(tplot_name)
                    
                    options(tplot_variables[1:], 'zlog', 1)
                    options(tplot_variables[1:], 'ysubtitle', '[deg]')
                    options(tplot_variables[1:], 'yrange', [0 , 180])
                    options(tplot_variables[1:], 'colormap', 'jet')

                if et_diagram:
                    ytitle_deg_array = np.round(np.nan_to_num(FEDU_get_data[3]), 3)
                    
                    for i in range(FEDU_get_data[1].shape[2]): # processing for erg_lepe_l3_pa_pabin_??(??:01,01,..16)_FEDU
                            tplot_name = prefix + 'pabin_' + str(i + 1).zfill(2) +'_FEDU' + suffix
                            store_data(tplot_name,data={'x':FEDU_get_data[0],
                                                        'y':FEDU_get_data[1][:,:,i],
                                                        'v':FEDU_get_data[2]})
                            options(tplot_name, 'spec', 1)
                            ylim(tplot_name,  19, 21*1e3)
                            zlim(tplot_name, 1, 1e6)
                            options(tplot_name, 'ytitle', 'ERG LEP-e\n' + str(ytitle_deg_array[i]) + ' deg\nEnergy')
                            tplot_variables.append(tplot_name)
                    
                    options(tplot_variables[-FEDU_get_data[1].shape[2]:], 'ysubtitle', '[eV]')
                    options(tplot_variables[-FEDU_get_data[1].shape[2]:], 'zlog', 1)
                    options(tplot_variables[-FEDU_get_data[1].shape[2]:], 'ylog', 1)
                    options(tplot_variables[-FEDU_get_data[1].shape[2]:], 'colormap', 'jet')

                return tplot_variables

    return loaded_data