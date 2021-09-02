
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip
import cdflib

def mepi(trange=['2017-03-27', '2017-03-28'],
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
        time_clip=False):
    """
    This function loads data from the MEP-i experiment from the Arase mission
    
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

    Returns:
        List of tplot variables created.

    """

    loaded_data = load(instrument='mepi', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)

    if len(loaded_data) > 0:
    
        out_files = load(instrument='mepi', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
        cdf_file = cdflib.CDF(out_files[0])
        gatt = cdf_file.globalattsget()

        # --- print PI info and rules of the road

        print(' ')
        print('**************************************************************************')
        print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
        print('')
        print('PI: ', gatt['PI_NAME'])
        print("Affiliation: "+gatt["PI_AFFILIATION"])
        print('')
        print('- The rules of the road (RoR) common to the ERG project:')
        print('      https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
        print('- RoR for MEP-i data: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Mepi')
        print('')
        print('Contact: erg_mep_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')

    # set spectrogram plot option
    options('erg_mepi_' + level + '_FPDO', 'Spec', 1)
    options('erg_mepi_' + level + '_FHE2DO', 'Spec', 1)
    options('erg_mepi_' + level + '_FHEDO', 'Spec', 1)

    # set y axis to logscale
    options('erg_mepi_' + level + '_FPDO', 'ylog', 1)
    options('erg_mepi_' + level + '_FHE2DO', 'ylog', 1)
    options('erg_mepi_' + level + '_FHEDO', 'ylog', 1)

    # set yrange
    options('erg_mepi_' + level + '_FPDO', 'yrange', [4., 200.])
    options('erg_mepi_' + level + '_FHE2DO', 'yrange', [4., 200.])
    options('erg_mepi_' + level + '_FHEDO', 'yrange', [4., 200.])

    # set z axis to logscale
    options('erg_mepi_' + level + '_FPDO', 'zlog', 1)
    options('erg_mepi_' + level + '_FHE2DO', 'zlog', 1)
    options('erg_mepi_' + level + '_FHEDO', 'zlog', 1)

    # set zrange
    options('erg_mepi_' + level + '_FPDO', 'zrange', [1.e+01, 1.e+06])
    options('erg_mepi_' + level + '_FHE2DO', 'zrange', [6.e+00, 3.e+04])
    options('erg_mepi_' + level + '_FHEDO', 'zrange', [7.e+00, 8.e+04])

    # change colormap option
    options('erg_mepi_' + level + '_FPDO', 'Colormap', 'jet')
    options('erg_mepi_' + level + '_FHE2DO', 'Colormap', 'jet')
    options('erg_mepi_' + level + '_FHEDO', 'Colormap', 'jet')

    return loaded_data