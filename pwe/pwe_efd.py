
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip, ylim, zlim
import cdflib

def pwe_efd(trange=['2017-04-01', '2017-04-02'],
        datatype='E_spin', 
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

    file_res=3600. * 24
    prefix = 'erg_pwe_efd_'+level+'_'+datatype+'_'

    if datatype == 'E256Hz' or datatype == 'E64Hz':
        pathformat = 'satellite/erg/pwe/efd/'+level+'/'+datatype+'/%Y/%m/erg_pwe_efd_'+level+'_'+datatype+'_dsi_%Y%m%d_v??_??.cdf'
        # need if sentence for '_[[wpt]]_%Y%m%d_v??_??.cdf'
    else:
        pathformat = 'satellite/erg/pwe/efd/'+level+'/'+datatype+'/%Y/%m/erg_pwe_efd_'+level+'_'+datatype+'_%Y%m%d_v??_??.cdf'

    loaded_data = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)

    if len(loaded_data) > 0 and ror:

        out_files = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
        cdf_file = cdflib.CDF(out_files[0])
        gatt = cdf_file.globalattsget()

        # --- print PI info and rules of the road

        print(' ')
        print(' ')
        print('**************************************************************************')
        print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
        print('')
        print('Information about ERG PWE EFD')
        print('')        
        print('PI: ', gatt['PI_NAME'])
        print("Affiliation: "+gatt["PI_AFFILIATION"])
        print('')
        print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
        print('RoR of PWE/EFD: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Pwe/Efd')
        print('')
        print('Contact: erg_pwe_info at isee.nagoya-u.ac.jp')
        print('**************************************************************************')


    return loaded_data
