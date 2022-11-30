import cdflib
from pyspedas import tnames
from pytplot import clip, options, ylim, zlim, get_data, store_data, tplot_options

from ..load import load


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

    initial_notplot_flag = False
    if notplot:
        initial_notplot_flag = True

    file_res = 3600. * 24

    if mode == 'low': 
        modenm = ['low','monit']
    elif mode == 'all':
        modenm = ['low','monit','high']
    
    loaded_data = []
    for md in modenm:
        if level == 'l2':
            prefix = 'erg_pwe_hfa_'+level+'_' + md + '_'

        if level == 'l2':
            pathformat = 'satellite/erg/pwe/hfa/'+level+'/'+datatype+'/'+md + \
                '/%Y/%m/erg_pwe_hfa_'+level+'_'+datatype+'_'+md+'_%Y%m%d_v??_??.cdf'
        elif level == 'l3':
            prefix = 'erg_pwe_hfa_'+level+'_1min_'
            pathformat = 'satellite/erg/pwe/hfa/'+level + \
                '/%Y/%m/erg_pwe_hfa_'+level+'_1min_%Y%m%d_v??_??.cdf'

        loaded = load(pathformat=pathformat, trange=trange, level=level, 
            datatype=datatype,file_res=file_res,   prefix=prefix, suffix=suffix, get_support_data=get_support_data,
            varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
        
        if loaded:
            loaded_data.extend( loaded )

    if (len(loaded_data) > 0) and ror:

        try:
            if isinstance(loaded_data, list):
                if downloadonly:
                    cdf_file = cdflib.CDF(loaded_data[-1])
                    gatt = cdf_file.globalattsget()
                else:
                    gatt = get_data(loaded_data[-1], metadata=True)['CDF']['GATT']
            elif isinstance(loaded_data, dict):
                gatt = loaded_data[list(loaded_data.keys())[-1]]['CDF']['GATT']

            # --- print PI info and rules of the road

            print(' ')
            print(' ')
            print(
                '**************************************************************************')
            print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
            print('')
            print('Information about ERG PWE HFA')
            print('')
            print('PI: ', gatt['PI_NAME'])
            print("Affiliation: "+gatt["PI_AFFILIATION"])
            print('')
            print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
            print(
                'RoR of PWE/HFA: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Pwe/Hfa')
            print('')
            print('Contact: erg_pwe_info at isee.nagoya-u.ac.jp')
            print(
                '**************************************************************************')
        except:
            print('printing PI info and rules of the road was failed')

    if initial_notplot_flag or downloadonly:
        return loaded_data

    if (level == 'l2') and (not notplot):

        l2prefix = 'erg_pwe_hfa_' + level + '_'
        #Create combined variables
        spec_coms = ['eu','ev','bgamma','esum','er','el','e_mix','e_ar'] 
        coms = spec_coms + ['eu_ev','eu_bg','ev_bg']
        if 'low' in modenm and 'monit' in modenm:
            for com in coms:
                vn = l2prefix+'lm_spectra_'+com
                #store_data( vn, data=l2prefix+'low_spectra_'+com + ' ' + l2prefix+'monit_spectra_'+com )
        if 'low' in modenm and 'high' in modenm:
            for com in coms:
                vn = l2prefix+'lh_spectra_'+com
                #store_data( vn, data=l2prefix+'low_spectra_'+com + ' ' + l2prefix+'high_spectra_'+com )

        # add ytitle for all variables
        for com in coms:
            vns = tnames(l2prefix+'*spectra_'+com)
            options( vns, 'ytitle', 'ERG PWE/HFA\n'+com.upper() )
        
        # set spectrogram plot option
        vns = tnames( [ l2prefix+'*spectra_'+x for x in spec_coms ])
        options( vns, 'Spec', 1 )

        # misc. decolation
        options(tnames(l2prefix+'*spectra_*'), 'ysubtitle', 'freq. [kHz]')
        options(tnames(l2prefix+'*spectra_e*'), 'ztitle', '$mV^{2}/m^{2}/Hz$')
        options(tnames(l2prefix+'*spectra_bgamma'), 'ztitle', '$pT^{2}/Hz$')
        options(tnames(l2prefix+'*spectra_e_ar'), 'ztitle', 'LH:-1/RH:+1')
        options(tnames(l2prefix+'*spectra_e*_bg'), 'ztitle', 'mV/m pT/Hz')

        for vn in tnames(l2prefix+'*spectra_e*'):
            ylim( vn, 2.0, 10000. )
        for vn in tnames(l2prefix+'*spectra_bgamma'):
            ylim( vn, 2.0, 200.0 )
        for vn in tnames( [ l2prefix+'*spectra_'+x for x in ['eu', 'ev', 'esum', 'er', 'el', 'e_mix'] ] ):
            zlim( vn, 1e-10, 1e-3 )
        for vn in tnames(l2prefix+'*spectra_bgamma'):
            zlim( vn, 1e-4, 1e+2 )
        for vn in tnames(l2prefix+'*spectra_e_ar'):
            zlim( vn, -1, 1)

        vns = tnames([l2prefix+'*spectra_e*', l2prefix+'*spectra_bgamma'])
        options( vns, 'ylog', 1 )
        for com in ['eu','ev','esum','er','el','e_mix','bgamma']:
            options( tnames( l2prefix+'*spectra_'+com ), 'zlog', 1 )

        tplot_options( 'data_gap', 70. )
        

        

    elif level == 'l3':

        # set ytitle
        options(prefix + 'Fuhr' + suffix, 'ytitle', 'UHR frequency [Mhz]')
        options(prefix + 'ne_mgf' + suffix,
                'ytitle', 'eletctorn density [/cc]')

        # set y axis to logscale
        options(prefix + 'Fuhr' + suffix, 'ylog', 1)
        options(prefix + 'ne_mgf' + suffix, 'ylog', 1)

    return loaded_data
