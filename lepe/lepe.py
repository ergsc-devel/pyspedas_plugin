
#from pyspedas.erg.load import load
from load import load
import numpy as np
from pytplot import options, clip, ylim, store_data
import cdflib

def lepe(trange=['2017-04-04', '2017-04-05'],
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
        version = None):
    """
    This function loads data from the LEP-e experiment from the Arase mission
    
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
            Set this value to specify the version of cdf files (such as "v02_02")

    Returns:
        List of tplot variables created.

    """

    if level == 'l3':
        datatype = 'pa'
    
    suffix = '_' + datatype + suffix 

    if level == 'l2' and datatype == 'omniflux':
        notplot=True # to avoid failure of creation plot variables (at store_data.py) of lepe
    
    file_res=3600. * 24
    prefix = 'erg_lepe_'+level+'_'
    pathformat = 'satellite/erg/lepe/'+level+'/'+datatype+'/%Y/%m/erg_lepe_'+level+'_'+datatype+'_%Y%m%d_'

    if version == None:
        pathformat += 'v??_??.cdf'
    else:
        pathformat += version + '.cdf'

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
        print('Information about ERG LEPe')
        print('')
        print('PI: ', gatt['PI_NAME'])
        print("Affiliation: "+gatt["PI_AFFILIATION"])
        print('')
        print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
        if level == 'l2':
            print('RoR of LEPe L2: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepe')
        if level == 'l3':
            print('RoR of LEPe L3: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepe')
            print('RoR of MGF L2: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Mgf')
        print('')
        print('Contact: erg_lepe_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')


    if type(loaded_data) is dict:
        if (level == 'l2' and datatype == 'omniflux'):
            tplot_variables = []
            v_array = (loaded_data['erg_lepe_l2_FEDO' + suffix]['v'][:,0,:] + loaded_data['erg_lepe_l2_FEDO' + suffix]['v'][:,1,:])/ 2.
            v_array = np.where(v_array < 0. , np.nan, v_array) # change minus values to NaN
            store_data('erg_lepe_l2_FEDO' + suffix, data={'x':loaded_data['erg_lepe_l2_FEDO' + suffix]['x'],
                                                'y':loaded_data['erg_lepe_l2_FEDO' + suffix]['y'],
                                                'v':v_array})
            tplot_variables.append('erg_lepe_l2_FEDO' + suffix)

            # change minus values to NaN in y array
            clip('erg_lepe_l2_FEDO' + suffix, 0., 2.e+16)
            # set spectrogram plot option
            options('erg_lepe_l2_FEDO' + suffix, 'Spec', 1)
            # set y axis to logscale
            options('erg_lepe_l2_FEDO' + suffix, 'ylog', 1)
            # set yrange
            options('erg_lepe_l2_FEDO' + suffix, 'yrange', [10., 2.e+04])
            # set z axis to logscale
            options('erg_lepe_l2_FEDO' + suffix, 'zlog', 1)
            # set zrange
            options('erg_lepe_l2_FEDO' + suffix, 'zrange', [1.e-02, 1.e+06])
            # change colormap option
            options('erg_lepe_l2_FEDO' + suffix, 'Colormap', 'jet')

            return tplot_variables

    return loaded_data