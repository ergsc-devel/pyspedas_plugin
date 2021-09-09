
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip
import cdflib

def pwe_hfa(trange=['2017-04-01', '2017-04-02'],
        datatype='spec', 
        mode='low',
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
        ror=True):
    """
    This function loads data from the PWE experiment from the Arase mission
    
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

    Returns:
        List of tplot variables created.

    """
    loaded_data = load(instrument='pwe_hfa', mode=mode, trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
    
    if len(loaded_data) > 0 and ror:

    
        out_files = load(instrument='pwe_hfa', mode=mode, trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
        cdf_file = cdflib.CDF(out_files[0])
        gatt = cdf_file.globalattsget()

        # --- print PI info and rules of the road

        print(' ')
        print(' ')
        print('**************************************************************************')
        print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
        print('')
        print('Information about ERG PWE HFA')
        print('')        
        print('PI: ', gatt['PI_NAME'])
        print("Affiliation: "+gatt["PI_AFFILIATION"])
        print('')
        print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
        print('RoR of PWE/HFA: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Pwe/Hfa')
        print('')
        print('Contact: erg_pwe_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')


    # remove minus values in y array
    clip('erg_pwe_hfa_'+level+'_spectra_er', 0., 5000.)
    clip('erg_pwe_hfa_'+level+'_spectra_el', 0., 5000.)

    # set spectrogram plot option
    options('erg_pwe_hfa_'+level+'_spectra_eu', 'Spec', 1)
    options('erg_pwe_hfa_'+level+'_spectra_ev', 'Spec', 1)
    options('erg_pwe_hfa_'+level+'_spectra_bgamma', 'Spec', 1)
    options('erg_pwe_hfa_'+level+'_spectra_esum', 'Spec', 1)
    options('erg_pwe_hfa_'+level+'_spectra_er', 'Spec', 1)
    options('erg_pwe_hfa_'+level+'_spectra_el', 'Spec', 1)
    options('erg_pwe_hfa_'+level+'_spectra_e_mix', 'Spec', 1)

    # set y axis to logscale
    options('erg_pwe_hfa_'+level+'_spectra_eu', 'ylog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_ev', 'ylog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_bgamma', 'ylog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_esum', 'ylog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_er', 'ylog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_el', 'ylog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_e_mix', 'ylog', 1)

    # set yrange
    options('erg_pwe_hfa_'+level+'_spectra_eu', 'yrange', [2., 1000.])
    options('erg_pwe_hfa_'+level+'_spectra_ev', 'yrange', [2., 1000.])
    options('erg_pwe_hfa_'+level+'_spectra_bgamma', 'yrange', [2., 300.])
    options('erg_pwe_hfa_'+level+'_spectra_esum', 'yrange', [2., 1000.])
    options('erg_pwe_hfa_'+level+'_spectra_er', 'yrange', [2., 1000.])
    options('erg_pwe_hfa_'+level+'_spectra_el', 'yrange', [2., 1000.])
    options('erg_pwe_hfa_'+level+'_spectra_e_mix', 'yrange', [2., 1000.])

    # set z axis to logscale
    options('erg_pwe_hfa_'+level+'_spectra_eu', 'zlog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_ev', 'zlog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_bgamma', 'zlog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_esum', 'zlog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_er', 'zlog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_el', 'zlog', 1)
    options('erg_pwe_hfa_'+level+'_spectra_e_mix', 'zlog', 1)

    # set zrange
    options('erg_pwe_hfa_'+level+'_spectra_eu', 'zrange', [1.e-10, 1.e-03])
    options('erg_pwe_hfa_'+level+'_spectra_ev', 'zrange', [1.e-10, 1.e-03])
    options('erg_pwe_hfa_'+level+'_spectra_bgamma', 'zrange', [1.e-04, 1.e+02])
    options('erg_pwe_hfa_'+level+'_spectra_esum', 'zrange', [1.e-10, 1.e-03])
    options('erg_pwe_hfa_'+level+'_spectra_er', 'zrange', [1.e-10, 1.e-03])
    options('erg_pwe_hfa_'+level+'_spectra_el', 'zrange', [1.e-10, 1.e-03])
    options('erg_pwe_hfa_'+level+'_spectra_e_mix', 'zrange', [1.e-10, 1.e-03])

    # change colormap option
    options('erg_pwe_hfa_'+level+'_spectra_eu', 'Colormap', 'jet')
    options('erg_pwe_hfa_'+level+'_spectra_ev', 'Colormap', 'jet')
    options('erg_pwe_hfa_'+level+'_spectra_bgamma', 'Colormap', 'jet')
    options('erg_pwe_hfa_'+level+'_spectra_esum', 'Colormap', 'jet')
    options('erg_pwe_hfa_'+level+'_spectra_er', 'Colormap', 'jet')
    options('erg_pwe_hfa_'+level+'_spectra_el', 'Colormap', 'jet')
    options('erg_pwe_hfa_'+level+'_spectra_e_mix', 'Colormap', 'jet')

    return loaded_data
