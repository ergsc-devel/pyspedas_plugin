
#from pyspedas.erg.load import load
from load import load
import numpy as np
from pytplot import options, clip, ylim, zlim, store_data, get_data
import cdflib

def lepi(trange=['2017-07-01', '2017-07-02'],
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
    This function loads data from the LEP-i experiment from the Arase mission
    
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
            Set this value to specify the version of cdf files (such as "v03_00")

    Returns:
        List of tplot variables created.

    """

    if level == 'l3':
        datatype = 'pa'

    file_res=3600. * 24
    prefix = 'erg_lepi_'+level+'_' + datatype + '_'

    pathformat = 'satellite/erg/lepi/'+level+'/'+datatype+'/%Y/%m/erg_lepi_'+level+'_'+datatype+'_%Y%m%d_'
    if version == None:
        pathformat += 'v??_??.cdf'
    else:
        pathformat += version + '.cdf'

    loaded_data = load(pathformat=pathformat, trange=trange, file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)


    if len(loaded_data) > 0 and ror:

    
        out_files = load(pathformat=pathformat, trange=trange,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
        cdf_file = cdflib.CDF(out_files[0])
        gatt = cdf_file.globalattsget()

        # --- print PI info and rules of the road

        print(' ')
        print('**************************************************************************')
        print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
        print('')
        print('Information about ERG LEPi')
        print('')
        print('PI: ', gatt['PI_NAME'])
        #print("Affiliation: "+gatt["PI_AFFILIATION"])
        print('')
        print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
        print('RoR of LEPi L2: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepi')
        print('RoR of ERG/LEPi: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepi#Rules_of_the_Road')
        print('')
        print('Contact: erg_lepi_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')



    if datatype == 'omniflux' and level == 'l2':
        tplot_variables = []

        if prefix + 'FPDO' + suffix in loaded_data:
            store_data(prefix + 'FPDO' + suffix,newname=prefix + 'FPDO_raw' + suffix)
            loaded_data.append(prefix + 'FPDO_raw' + suffix)
            get_data_vars = get_data(prefix + 'FPDO_raw' + suffix)
            flag_FPDO = store_data(prefix + 'FPDO' + suffix, data={'x':get_data_vars[0],
                                                                    'y':get_data_vars[1][:,:-2],
                                                                    'v':get_data_vars[2][:-2]})
            tplot_variables.append(prefix + 'FPDO' + suffix)


        if prefix + 'FHEDO' + suffix in loaded_data:
            store_data(prefix + 'FHEDO' + suffix,newname=prefix + 'FHEDO_raw' + suffix)
            loaded_data.append(prefix + 'FHEDO_raw' + suffix)
            get_data_vars = get_data(prefix + 'FHEDO_raw' + suffix)
            store_data(prefix + 'FHEDO' + suffix, data={'x':get_data_vars[0],
                                                        'y':get_data_vars[1][:,:-2],
                                                        'v':get_data_vars[2][:-2]})
            tplot_variables.append(prefix + 'FHEDO' + suffix)

        if prefix + 'FODO' + suffix in loaded_data:
            store_data(prefix + 'FODO' + suffix,newname=prefix + 'FODO_raw' + suffix)
            loaded_data.append(prefix + 'FODO_raw' + suffix)
            get_data_vars = get_data(prefix + 'FODO_raw' + suffix)
            store_data(prefix + 'FODO' + suffix, data={'x':get_data_vars[0],
                                                        'y':get_data_vars[1][:,:-2],
                                                        'v':get_data_vars[2][:-2]})
            tplot_variables.append(prefix + 'FODO' + suffix)

        # remove minus valuse of y array
        if flag_FPDO:
            clip(prefix + 'FPDO' + suffix, 0., 2.e+16)
        
        # set ytitle
        options(tplot_variables, 'ytitle', 'LEPi\nomniflux\nLv2\nEnergy')

        # set ysubtitle
        options(tplot_variables, 'ysubtitle', '[keV/q]')
        
        # set spectrogram plot option
        options(tplot_variables, 'Spec', 1)

        # set y axis to logscale
        options(tplot_variables, 'ylog', 1)

        for i in range(len(tplot_variables)):
            # set ylim
            ylim(tplot_variables[i], 0.01, 25.0)
            # set zlim
            zlim(tplot_variables[i], 1e+1, 1e+9)

        # set yrange
        #options(prefix + 'FPDO' + suffix, 'yrange', [0.01, 20.])
        #options(prefix + 'FHEDO' + suffix, 'yrange', [0.01, 20.])
        #options(prefix + 'FODO' + suffix, 'yrange', [0.01, 20.])

        # set ztitle
        options(tplot_variables, 'ztitle', '[/cm^2-str-s-keV]')

        # set z axis to logscale
        options(tplot_variables, 'zlog', 1)

        # set zrange
        #options(prefix + 'FPDO' + suffix, 'zrange', [1.e+02, 1.e+09])
        #options(prefix + 'FHEDO' + suffix, 'zrange', [1.e+02, 1.e+09])
        #options(prefix + 'FODO' + suffix, 'zrange', [1.e+01, 1.e+08])

        # change colormap option
        options(tplot_variables, 'Colormap', 'jet')

    elif datatype == '3dflux' and level == 'l2':
        if prefix + 'FPDU' + suffix in loaded_data:
            clip(prefix + 'FPDU' + suffix, -1.0e+10, 1.0e+10)
        if prefix + 'FHEDU' + suffix in loaded_data:
            clip(prefix + 'FHEDU' + suffix, -1.0e+10, 1.0e+10)
        if prefix + 'FODU' + suffix in loaded_data:
            clip(prefix + 'FODU' + suffix, -1.0e+10, 1.0e+10)

    return loaded_data
