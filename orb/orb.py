
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip
import cdflib

def orb(trange=['2017-03-27', '2017-03-28'],
        datatype='8sec', 
        level='l3', 
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
    This function loads orbit data from the Arase mission
    
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

    loaded_data = load(instrument='orb', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd)

    if len(loaded_data) > 0:
    
        out_files = load(instrument='orb', trange=trange, level=level, datatype=datatype, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd)
        cdf_file = cdflib.CDF(out_files[0])
        try:
            gatt = cdf_file.globalattsget()
        except:
            gatt = None

        if gatt is not None:

            # --- print PI info and rules of the road

            print(' ')
            print('**************************************************************************')
            print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
            print('')
            #print('Information about ERG L3 orbit')
            print('Information about ERG orbit')
            print('')
            #print('PI: ', gatt['PI_NAME']) # not need?
            #print("Affiliation: "+gatt["PI_AFFILIATION"]) # not need?
            print('')
            print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
            print('')
            print('Contact: erg-sc-core at isee.nagoya-u.ac.jp')
            print('**************************************************************************')


    return loaded_data
