
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip, ylim, zlim
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
    
    if level == 'l2':
        suffix = '_' + mode + suffix # to avoid duplicate Tplot Variable names in different mode argument

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


    if level == 'l2' and mode == 'low':
    
        
        if 'erg_pwe_hfa_'+level+'_spectra_er' + suffix in loaded_data:
            # remove minus values in y array
            clip('erg_pwe_hfa_'+level+'_spectra_er' + suffix, 0., 5000.)
        if 'erg_pwe_hfa_'+level+'_spectra_el' + suffix in loaded_data:
            # remove minus values in y array
            clip('erg_pwe_hfa_'+level+'_spectra_el' + suffix, 0., 5000.)
        if 'erg_pwe_hfa_'+level+'_spectra_eu' + suffix in loaded_data:
            # remove minus values in y array
            clip('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 0., 5000.)
            # set ylim
            ylim('erg_pwe_hfa_'+level+'_spectra_eu' + suffix,  2.0, 10000.0)
            # set zlim
            zlim('erg_pwe_hfa_'+level+'_spectra_eu' + suffix,  1e-10, 1e-3)
        if 'erg_pwe_hfa_'+level+'_spectra_ev' + suffix in loaded_data:
            # remove minus values in y array
            clip('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 0., 5000.)
            # set ylim
            ylim('erg_pwe_hfa_'+level+'_spectra_ev' + suffix,  2.0, 10000.0)
            # set zlim
            zlim('erg_pwe_hfa_'+level+'_spectra_ev' + suffix,  1e-10, 1e-3)

        if 'erg_pwe_hfa_'+level+'_spectra_esum' + suffix in loaded_data:
            # set ylim
            ylim('erg_pwe_hfa_'+level+'_spectra_esum' + suffix,  2.0, 10000.0)
            # set zlim
            zlim('erg_pwe_hfa_'+level+'_spectra_esum' + suffix,  1e-10, 1e-3)

        if 'erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix in loaded_data:
            # set ylim
            ylim('erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix,  2.0, 10000.0)
            # set zlim
            zlim('erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix, -1, 1)


        # set spectrogram plot option
        options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'Spec', 1)
        options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'Spec', 1)
        options('erg_pwe_hfa_'+level+'_spectra_bgamma' + suffix, 'Spec', 1)
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'Spec', 1)
        options('erg_pwe_hfa_'+level+'_spectra_er' + suffix, 'Spec', 1)
        options('erg_pwe_hfa_'+level+'_spectra_el' + suffix, 'Spec', 1)
        options('erg_pwe_hfa_'+level+'_spectra_e_mix' + suffix, 'Spec', 1)
        options('erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix, 'Spec', 1)

        # set y axis to logscale
        options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'ylog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'ylog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_bgamma' + suffix, 'ylog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'ylog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_er' + suffix, 'ylog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_el' + suffix, 'ylog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_e_mix' + suffix, 'ylog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix, 'ylog', 1)

        # set yrange
        #options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'yrange', [2., 1000.])
        #options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'yrange', [2., 1000.])
        options('erg_pwe_hfa_'+level+'_spectra_bgamma' + suffix, 'yrange', [2., 300.])
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'yrange', [2., 1000.])
        options('erg_pwe_hfa_'+level+'_spectra_er' + suffix, 'yrange', [2., 1000.])
        options('erg_pwe_hfa_'+level+'_spectra_el' + suffix, 'yrange', [2., 1000.])
        options('erg_pwe_hfa_'+level+'_spectra_e_mix' + suffix, 'yrange', [2., 1000.])

        # set ytitle
        options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'ytitle', 'ERG PWE/HFA (EU)')
        options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'ytitle', 'ERG PWE/HFA (EV)')
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'ytitle', 'ERG PWE/HFA (ESUM)')
        options('erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix, 'ytitle', 'ERG PWE/HFA (E_AR)')

        # set ysubtitle
        options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'ysubtitle', 'frequency [Hz]')
        options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'ysubtitle', 'frequency [Hz]')
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'ysubtitle', 'frequency [Hz]')
        options('erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix, 'ysubtitle', 'frequency [Hz]')

        # set z axis to logscale
        options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'zlog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'zlog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_bgamma' + suffix, 'zlog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'zlog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_er' + suffix, 'zlog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_el' + suffix, 'zlog', 1)
        options('erg_pwe_hfa_'+level+'_spectra_e_mix' + suffix, 'zlog', 1)


        # set zrange
        #options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'zrange', [1.e-10, 1.e-03])
        #options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'zrange', [1.e-10, 1.e-03])
        options('erg_pwe_hfa_'+level+'_spectra_bgamma' + suffix, 'zrange', [1.e-04, 1.e+02])
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'zrange', [1.e-10, 1.e-03])
        options('erg_pwe_hfa_'+level+'_spectra_er' + suffix, 'zrange', [1.e-10, 1.e-03])
        options('erg_pwe_hfa_'+level+'_spectra_el' + suffix, 'zrange', [1.e-10, 1.e-03])
        options('erg_pwe_hfa_'+level+'_spectra_e_mix' + suffix, 'zrange', [1.e-10, 1.e-03])

        # set ztitle
        options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'ztitle', 'mV^2/m^2/Hz')
        options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'ztitle', 'mV^2/m^2/Hz')
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'ztitle', 'mV^2/m^2/Hz')
        options('erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix, 'ztitle', 'LH:-1/RH:+1')

        # change colormap option
        options('erg_pwe_hfa_'+level+'_spectra_eu' + suffix, 'Colormap', 'jet')
        options('erg_pwe_hfa_'+level+'_spectra_ev' + suffix, 'Colormap', 'jet')
        options('erg_pwe_hfa_'+level+'_spectra_bgamma' + suffix, 'Colormap', 'jet')
        options('erg_pwe_hfa_'+level+'_spectra_esum' + suffix, 'Colormap', 'jet')
        options('erg_pwe_hfa_'+level+'_spectra_er' + suffix, 'Colormap', 'jet')
        options('erg_pwe_hfa_'+level+'_spectra_el' + suffix, 'Colormap', 'jet')
        options('erg_pwe_hfa_'+level+'_spectra_e_mix' + suffix, 'Colormap', 'jet')
        options('erg_pwe_hfa_'+level+'_spectra_e_ar' + suffix, 'Colormap', 'jet')

    return loaded_data
