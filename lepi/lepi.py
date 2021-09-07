
#from pyspedas.erg.load import load
from load import load
import numpy as np
from pytplot import options, clip, ylim, store_data
import cdflib

def lepi(trange=['2017-07-01', '2017-07-02'],
        datatype='omniflux', 
        level='l2', 
        suffix='',  
        get_support_data=False, 
        varformat=None,
        varnames=[],
        downloadonly=False,
        notplot=True, # to avoid failure of creation plot variables (at store_data.py) of lepi
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

    loaded_data = load(instrument='lepi', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd, version=version)

    
    if len(loaded_data) > 0 and ror:

    
        out_files = load(instrument='lepi', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd, version=version)
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
        print('RoR of LEPe L2: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepe')
        print('RoR of ERG/LEPi: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepi#Rules_of_the_Road')
        print('')
        print('Contact: erg_lepi_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')


    if type(loaded_data) is dict:
        tplot_variables = []
        v_array = loaded_data['erg_lepi_l2_FPDO']['v']
        v_array = np.where(v_array < 0. , np.nan, v_array) # change minus values to NaN
        store_data('erg_lepi_l2_FPDO', data={'x':loaded_data['erg_lepi_l2_FPDO']['x'],
                                            'y':loaded_data['erg_lepi_l2_FPDO']['y'],
                                            'v':v_array})
        tplot_variables.append('erg_lepi_l2_FPDO')

        v_array = loaded_data['erg_lepi_l2_FHEDO']['v']
        v_array = np.where(v_array < 0. , np.nan, v_array) # change minus values to NaN
        store_data('erg_lepi_l2_FHEDO', data={'x':loaded_data['erg_lepi_l2_FHEDO']['x'],
                                            'y':loaded_data['erg_lepi_l2_FHEDO']['y'],
                                            'v':v_array})
        tplot_variables.append('erg_lepi_l2_FHEDO')

        v_array = loaded_data['erg_lepi_l2_FODO']['v']
        v_array = np.where(v_array < 0. , np.nan, v_array) # change minus values to NaN
        store_data('erg_lepi_l2_FODO', data={'x':loaded_data['erg_lepi_l2_FODO']['x'],
                                            'y':loaded_data['erg_lepi_l2_FODO']['y'],
                                            'v':v_array})
        tplot_variables.append('erg_lepi_l2_FODO')

        # remove minus valuse of y array
        clip('erg_lepi_l2_FPDO', 0., 2.e+16)
        
        # set spectrogram plot option
        options('erg_lepi_l2_FPDO', 'Spec', 1)
        options('erg_lepi_l2_FHEDO', 'Spec', 1)
        options('erg_lepi_l2_FODO', 'Spec', 1)

        # set y axis to logscale
        options('erg_lepi_l2_FPDO', 'ylog', 1)
        options('erg_lepi_l2_FHEDO', 'ylog', 1)
        options('erg_lepi_l2_FODO', 'ylog', 1)

        # set yrange
        options('erg_lepi_l2_FPDO', 'yrange', [0.01, 20.])
        options('erg_lepi_l2_FHEDO', 'yrange', [0.01, 20.])
        options('erg_lepi_l2_FODO', 'yrange', [0.01, 20.])

        # set z axis to logscale
        options('erg_lepi_l2_FPDO', 'zlog', 1)
        options('erg_lepi_l2_FHEDO', 'zlog', 1)
        options('erg_lepi_l2_FODO', 'zlog', 1)

        # set zrange
        options('erg_lepi_l2_FPDO', 'zrange', [1.e+02, 1.e+09])
        options('erg_lepi_l2_FHEDO', 'zrange', [1.e+02, 1.e+09])
        options('erg_lepi_l2_FODO', 'zrange', [1.e+01, 1.e+08])

        # change colormap option
        options('erg_lepi_l2_FPDO', 'Colormap', 'jet')
        options('erg_lepi_l2_FHEDO', 'Colormap', 'jet')
        options('erg_lepi_l2_FODO', 'Colormap', 'jet')

        return tplot_variables

    return loaded_data
