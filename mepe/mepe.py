
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip, ylim, zlim
import cdflib

def mepe(trange=['2017-03-27', '2017-03-28'],
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
    This function loads data from the MEP-e experiment from the Arase mission
    
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
    
    if level == 'l3':
        datatype = '3dflux'

    loaded_data = load(instrument='mepe', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
    
    if len(loaded_data) > 0:

    
        out_files = load(instrument='mepe', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
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
        print('- RoR for MEP-e data:  https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Mepe')
        print('')
        print('Contact: erg_mep_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')

    if datatype == 'omniflux':
        # set spectrogram plot option
        options('erg_mepe_' + level + '_FEDO' + suffix, 'Spec', 1)
        # set y axis to logscale
        options('erg_mepe_' + level + '_FEDO' + suffix, 'ylog', 1)
        # set yrange
        options('erg_mepe_' + level + '_FEDO' + suffix, 'yrange', [6., 90.])
        # set z axis to logscale
        options('erg_mepe_' + level + '_FEDO' + suffix, 'zlog', 1)
        # set zrange
        options('erg_mepe_' + level + '_FEDO' + suffix, 'zrange', [1.e+01, 1.e+07])
        # change colormap option
        options('erg_mepe_' + level + '_FEDO' + suffix, 'Colormap', 'jet')
    elif datatype == '3dflux' and level == 'l2':
        # set spectrogram plot option
        options('erg_mepe_' + level + '_FEDU' + suffix, 'Spec', 1)
        options('erg_mepe_' + level + '_FEDU_n' + suffix, 'Spec', 1)
        options('erg_mepe_' + level + '_FEEDU' + suffix, 'Spec', 1)
        options('erg_mepe_' + level + '_count_raw' + suffix, 'Spec', 1)

        # set y axis to logscale
        options('erg_mepe_' + level + '_FEDU' + suffix, 'ylog', 1)
        options('erg_mepe_' + level + '_FEDU_n' + suffix, 'ylog', 1)
        options('erg_mepe_' + level + '_FEEDU' + suffix, 'ylog', 1)
        options('erg_mepe_' + level + '_count_raw' + suffix, 'ylog', 1)

        # set yrange
        options('erg_mepe_' + level + '_FEDU' + suffix, 'yrange', [6., 100.])
        options('erg_mepe_' + level + '_FEDU_n' + suffix, 'yrange', [6., 100.])
        options('erg_mepe_' + level + '_FEEDU' + suffix, 'yrange', [6., 100.])
        options('erg_mepe_' + level + '_count_raw' + suffix, 'yrange', [6., 100.])

        # set ysubtitle
        options('erg_mepe_' + level + '_FEDU' + suffix, 'ysubtitle', '[keV]')
        options('erg_mepe_' + level + '_FEDU_n' + suffix, 'ysubtitle', '[keV]')
        options('erg_mepe_' + level + '_count_raw' + suffix, 'ysubtitle', '[keV]')

        # set ylim
        ylim('erg_mepe_' + level + '_FEDU' + suffix, 6., 100.)
        ylim('erg_mepe_' + level + '_FEDU_n' + suffix, 6., 100.)

        # set z axis to logscale
        options('erg_mepe_' + level + '_FEDU' + suffix, 'zlog', 1)
        options('erg_mepe_' + level + '_FEDU_n' + suffix, 'zlog', 1)
        options('erg_mepe_' + level + '_FEEDU' + suffix, 'zlog', 1)
        options('erg_mepe_' + level + '_count_raw' + suffix, 'zlog', 1)

        # set zrange
        options('erg_mepe_' + level + '_FEDU' + suffix, 'zrange', [1.05*1.0e+4 , 2.0*1.0e+9])
        options('erg_mepe_' + level + '_FEDU_n' + suffix, 'zrange', [.95e+4 , 1.05e+9])
        options('erg_mepe_' + level + '_FEEDU' + suffix, 'zrange', [6.0e+5 , 1.0e+10])
        options('erg_mepe_' + level + '_count_raw' + suffix, 'zrange', [1.0e+0 , 1.0e+4])

        # set ztitle
        options('erg_mepe_' + level + '_FEDU' + suffix, 'ztitle', '[/s-cm^{2}-sr-keV]')
        options('erg_mepe_' + level + '_FEDU_n' + suffix, 'ztitle', '[/s-cm^{2}-sr-keV]')

        # change colormap option
        options('erg_mepe_' + level + '_FEDU' + suffix, 'Colormap', 'jet')
        options('erg_mepe_' + level + '_FEDU_n' + suffix, 'Colormap', 'jet')
        options('erg_mepe_' + level + '_FEEDU' + suffix, 'Colormap', 'jet')
        options('erg_mepe_' + level + '_count_raw' + suffix, 'Colormap', 'jet')

    return loaded_data
