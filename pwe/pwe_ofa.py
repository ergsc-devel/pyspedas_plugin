
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip, ylim, zlim
import cdflib

def pwe_ofa(trange=['2017-04-01', '2017-04-02'],
        datatype='spec', 
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

    Returns:
        List of tplot variables created.

    """
    loaded_data = load(instrument='pwe_ofa', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
    
    if len(loaded_data) > 0:

    
        out_files = load(instrument='pwe_ofa', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
        cdf_file = cdflib.CDF(out_files[0])
        gatt = cdf_file.globalattsget()

        # --- print PI info and rules of the road

        print(' ')
        print(' ')
        print('**************************************************************************')
        print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
        print('')
        print('Information about ERG PWE OFA')
        print('')        
        print('PI: ', gatt['PI_NAME'])
        print("Affiliation: "+gatt["PI_AFFILIATION"])
        print('')
        print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
        print('RoR of PWE/OFA: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Pwe/Ofa')
        print('')
        print('Contact: erg_pwe_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')


    # set spectrogram plot option
    options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'Spec', 1)
    options('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix,  'Spec', 1)

    # set y axis to logscale
    options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'ylog', 1)
    options('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix,  'ylog', 1)
    
    if 'erg_pwe_ofa_'+level+'_E_spectra_132'+suffix in loaded_data:
        # set ylim
        ylim('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix, 32e-3, 20.)
        # set zlim
        zlim('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix, 1e-9, 1e-2)

    if 'erg_pwe_ofa_'+level+'_B_spectra_132'+suffix in loaded_data:
        # set ylim
        ylim('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix, 32e-3, 20.)
        # set zlim
        zlim('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix, 1e-4, 1e2)

    # set ytitle
    options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'ytitle', 'ERG PWE/OFA-SPEC (E)')
    options('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix,  'ytitle', 'ERG PWE/OFA-SPEC (B)')

    # set ysubtitle
    options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'ysubtitle', 'frequency [kHz]')
    options('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix,  'ysubtitle', 'frequency [kHz]')

    # set ztitle
    options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'ztitle', 'mV^2/m^2/Hz')

    # set yrange
    #options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'yrange', [0., 10.])
    #options('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix,  'yrange', [0., 11.])
    
    # set z axis to logscale
    options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'zlog', 1)
    options('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix,  'zlog', 1)
    
    # set zrange
    #options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'zrange', [1.0e-08, 1.0e-02])
    #options('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix,  'zrange', [1.0e-04, 1.0e+02])
    
    # change colormap option
    options('erg_pwe_ofa_'+level+'_E_spectra_132'+suffix,  'Colormap', 'jet')
    options('erg_pwe_ofa_'+level+'_B_spectra_132'+suffix,  'Colormap', 'jet')
    
    
    return loaded_data
