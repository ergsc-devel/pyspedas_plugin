#from pyspedas.erg.load import load
from load import load
import numpy as np
from pytplot import options, clip, ylim,zlim, store_data
import cdflib

def xep(trange=['2017-06-01', '2017-06-02'],
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
        ror=True):
    """
    This function loads data from the XEP-e experiment from the Arase mission
    
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
    if datatype == 'omniflux' or datatype == '2dflux':
        notplot=True # to avoid failure of creation Tplot variables (at store_data.py) of xep
    file_res=3600. * 24
    prefix = 'erg_xep_'+level+'_'
    pathformat = 'satellite/erg/xep/'+level+'/'+datatype+'/%Y/%m/erg_xep_'+level+'_'+datatype+'_%Y%m%d_v??_??.cdf'
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
        print('Information about ERG XEP')
        print('')        
        print('PI: ', gatt['PI_NAME'])
        print("Affiliation: "+gatt["PI_AFFILIATION"])
        print('')
        print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
        print('RoR of XEP: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Xep')
        print('')
        print('Contact: erg_xep_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')


    if type(loaded_data) is dict:

        if datatype == 'omniflux':
            tplot_variables = []
            
            v_vars_min = loaded_data['erg_xep_l2_FEDO_SSD' + suffix]['v'][0]
            v_vars_max = loaded_data['erg_xep_l2_FEDO_SSD' + suffix]['v'][1]
            v_vars = np.sqrt(v_vars_min * v_vars_max) # Geometric mean 
            
            store_data('erg_xep_l2_FEDO_SSD' + suffix, data={'x':loaded_data['erg_xep_l2_FEDO_SSD' + suffix]['x'], 
                                                'y':loaded_data['erg_xep_l2_FEDO_SSD' + suffix]['y'],
                                                'v':v_vars})
            tplot_variables.append('erg_xep_l2_FEDO_SSD' + suffix)
            
            # remove minus valuse of y array
            clip('erg_xep_l2_FEDO_SSD' + suffix, 0., 5000.)
            # set spectrogram plot option
            options('erg_xep_l2_FEDO_SSD' + suffix, 'Spec', 1)
            # set y axis to logscale
            options('erg_xep_l2_FEDO_SSD' + suffix, 'ylog', 1)
            # set yrange
            options('erg_xep_l2_FEDO_SSD' + suffix, 'yrange', [4.0e+02, 4.5e+03])
            # set z axis to logscale
            options('erg_xep_l2_FEDO_SSD' + suffix, 'zlog', 1)
            # set zrange
            options('erg_xep_l2_FEDO_SSD' + suffix, 'zrange', [1.0e-01, 1.0e+3])
            # change colormap option
            options('erg_xep_l2_FEDO_SSD' + suffix, 'Colormap', 'jet')

            # set ztitle
            options('erg_xep_l2_FEDO_SSD' + suffix, 'ztitle', '[/cm^{2}-str-s-keV]')
            # set ytitle
            options('erg_xep_l2_FEDO_SSD' + suffix, 'ytitle', 'XEP\nomniflux\nLv2\nEnergy')
            # set ysubtitle
            options('erg_xep_l2_FEDO_SSD' + suffix, 'ysubtitle', '[keV]')

            ylim('erg_xep_l2_FEDO_SSD' + suffix, 4.0e+02, 4.5e+03)
            zlim('erg_xep_l2_FEDO_SSD' + suffix, 1.0e-01, 1.0e+3)

            return  tplot_variables
        
    return loaded_data