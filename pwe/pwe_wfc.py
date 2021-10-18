
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip, ylim, zlim
from pyspedas import tnames
import cdflib

def pwe_wfc(trange=['2017-04-01/12:00:00', '2017-04-01/13:00:00'],
        datatype='waveform', 
        mode='65khz',
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
    
    file_res=3600.
    
    if level == 'l2':
        prefix = 'erg_pwe_wfc_'+level+'_' + mode +'_'
    
    loaded_data = []
    if level == 'l2':
        if datatype == 'waveform':
            for com in ['e', 'b']:
                prefix = 'erg_pwe_wfc_' + level + '_' + com + '_' + mode +'_'
                pathformat = 'satellite/erg/pwe/wfc/'+level+'/'+datatype+'/%Y/%m/erg_pwe_wfc_'+level+'_'+com+'_'+datatype+'_'+mode+'_sgi_%Y%m%d%H_v??_??.cdf'
                loaded_data +=load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
        elif datatype == 'spec':
            prefix_list = []
            for com in ['e', 'b']:
                prefix = 'erg_pwe_wfc_' + level + '_' + com + '_' + mode +'_'
                pathformat = 'satellite/erg/pwe/wfc/'+level+'/'+datatype+'/%Y/%m/erg_pwe_wfc_'+level+'_'+com+'_'+datatype+'_'+mode+'_%Y%m%d%H_v??_??.cdf'
                loaded_data +=load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)
                prefix_list.append(prefix)

    
    
    if len(loaded_data) > 0 and ror:

    
        out_files = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
        cdf_file = cdflib.CDF(out_files[0])
        try:
            # --- print PI info and rules of the road
            gatt = cdf_file.globalattsget()
            print(' ')
            print(' ')
            print('**************************************************************************')
            print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
            print('')
            print('Information about ERG PWE WFC')
            print('')        
            print('PI: ', gatt['PI_NAME'])
            print("Affiliation: "+gatt["PI_AFFILIATION"])
            print('')
            print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
            print('RoR of PWE/WFC: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Pwe/Wfc')
            print('')
            print('Contact: erg_pwe_info at isee.nagoya-u.ac.jp')
            print('**************************************************************************')
        except:
            print('printing PI info and rules of the road was failed')

    tplot_names_list = []
    if datatype == 'spec':
        options(prefix_list[0] + 'E_spectra', 'spec', 1)
        options(prefix_list[0] + 'E_spectra', 'colormap', 'jet')
        options(prefix_list[0] + 'E_spectra','ylog', 1)
        options(prefix_list[0] + 'E_spectra','zlog', 1)
        options(prefix_list[0] + 'E_spectra','ysubtitle', 'Hz')
        ylim(prefix_list[0] + 'E_spectra', 32., 2e4)
        zlim(prefix_list[0] + 'E_spectra', 1e-9, 1e-2)
        options(prefix_list[0] + 'E_spectra', 'ztitle', '[mV^2/m^2/Hz]')
        options(prefix_list[0] + 'E_spectra', 'ytitle', 'E/nspectra')
        options(prefix_list[1] + 'B_spectra', 'spec', 1)
        options(prefix_list[1] + 'B_spectra', 'colormap', 'jet')
        options(prefix_list[1] + 'B_spectra', 'ylog', 1)
        options(prefix_list[1] + 'B_spectra', 'zlog', 1)
        options(prefix_list[1] + 'B_spectra', 'ysubtitle', 'Hz')
        ylim(prefix_list[1] + 'B_spectra', 32., 2e4)
        zlim(prefix_list[1] + 'B_spectra', 1e-4, 1e2)
        options(prefix_list[1] + 'B_spectra', 'ztitle', '[pT^2/Hz]')
        options(prefix_list[1] + 'B_spectra', 'ytitle', 'B/nspectra')


    return loaded_data
