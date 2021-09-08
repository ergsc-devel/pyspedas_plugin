
#from pyspedas.erg.load import load
from load import load
from pytplot import options, clip
import cdflib

def orb(trange=['2017-03-27', '2017-03-28'],
        datatype='def',
        level='l2',
        model="op",
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
        version=None):
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

        version: str
            Set this value to specify the version of cdf files (such as "v03")

    Returns:
        List of tplot variables created.

    """

    loaded_data = load(instrument='orb', trange=trange, level=level, datatype=datatype, model=model,suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd, version=version)

    if len(loaded_data) > 0:
    
        out_files = load(instrument='orb', trange=trange, level=level, datatype=datatype, model=model, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd,version=version)
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


    # set labels
    options('erg_orb_l2_pos_gse' + suffix, 'legend_names', ['X','Y','Z'])
    options('erg_orb_l2_pos_gsm' + suffix, 'legend_names', ['X','Y','Z'])
    options('erg_orb_l2_pos_sm' + suffix, 'legend_names', ['X','Y','Z'])

    options('erg_orb_l2_pos_rmlatmlt' + suffix, 'legend_names', ['Re','MLAT','MLT'])

    options('erg_orb_l2_pos_eq' + suffix, 'legend_names', ['Req','MLT'])

    options('erg_orb_l2_pos_iono_north' + suffix, 'legend_names', ['GLAT','GLON'])
    options('erg_orb_l2_pos_iono_south' + suffix, 'legend_names', ['GLAT','GLON'])

    options('erg_orb_l2_pos_blocal' + suffix, 'legend_names', ['X','Y','Z'])

    options('erg_orb_l2_pos_blocal_mag' + suffix, 'legend_names', ['B(model)_at_ERG'])
    #options('erg_orb_l2_pos_blocal_mag' + suffix, 'legend_names', ['B(model)\n_at_ERG']) # Can't break?

    # set color
    options('erg_orb_l2_pos_gse' + suffix, 'Color', ['b', 'g', 'r'])
    options('erg_orb_l2_pos_gsm' + suffix, 'Color', ['b', 'g', 'r'])
    options('erg_orb_l2_pos_sm' + suffix, 'Color', ['b', 'g', 'r'])

    options('erg_orb_l2_pos_rmlatmlt' + suffix, 'Color', ['b', 'g', 'r'])

    options('erg_orb_l2_pos_blocal' + suffix, 'Color', ['b', 'g', 'r'])

    # set y axis to logscale
    options('erg_orb_l2_pos_blocal_mag' + suffix, 'ylog', 1)

    return loaded_data
