
#from pyspedas.erg.load import load
from load import load
from pytplot import get_data, options, clip, ylim
import cdflib
import numpy as np

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
    file_res=3600. * 24
    prefix = 'erg_orb_'+level+'_'
    if level == 'l3':
        if model == 'op':
            pathformat = 'satellite/erg/orb/'+level+'/opq/%Y/%m/erg_orb_'+level+'_op_%Y%m%d_'
        else:
            pathformat = 'satellite/erg/orb/'+level+'/'+model+'/%Y/%m/erg_orb_'+level+'_'+model+'_%Y%m%d_'
    elif level == 'l2':
        if datatype == 'def':
            pathformat = 'satellite/erg/orb/'+ datatype +'/%Y/erg_orb_'+level+'_%Y%m%d_'
        else:
            pathformat = 'satellite/erg/orb/'+ datatype +'/%Y/erg_orb_'+ datatype + '_'+level+'_%Y%m%d_'
    if version == None:
        pathformat += 'v??.cdf'
    else:
        pathformat += version + '.cdf'

    loaded_data = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix,suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd, version=version)

    if len(loaded_data) > 0:
    
        out_files = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype,file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, downloadonly=True, notplot=notplot, time_clip=time_clip, no_update=True, uname=uname, passwd=passwd,version=version)
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


    if level == 'l2' and datatype=='def':

        # remove -1.0e+30
        if prefix + 'pos_Lm' + suffix in loaded_data:
            clip(prefix + 'pos_Lm' + suffix, -1e+6, 1e6)
            times, bdata = get_data(prefix + 'pos_Lm' + suffix)
            ylim(prefix + 'pos_Lm' + suffix, np.nanmin(bdata), np.nanmax(bdata))


        # set labels
        options(prefix + 'pos_gse' + suffix, 'legend_names', ['X','Y','Z'])
        options(prefix + 'pos_gsm' + suffix, 'legend_names', ['X','Y','Z'])
        options(prefix + 'pos_sm' + suffix, 'legend_names', ['X','Y','Z'])

        options(prefix + 'pos_rmlatmlt' + suffix, 'legend_names', ['Re','MLAT','MLT'])

        options(prefix + 'pos_eq' + suffix, 'legend_names', ['Req','MLT'])

        options(prefix + 'pos_iono_north' + suffix, 'legend_names', ['GLAT','GLON'])
        options(prefix + 'pos_iono_south' + suffix, 'legend_names', ['GLAT','GLON'])

        options(prefix + 'pos_blocal' + suffix, 'legend_names', ['X','Y','Z'])

        options(prefix + 'pos_blocal_mag' + suffix, 'legend_names', ['B(model)_at_ERG'])
        #options(prefix + 'pos_blocal_mag' + suffix, 'legend_names', ['B(model)\n_at_ERG']) # Can't break?

        options(prefix + 'pos_beq' + suffix, 'legend_names', ['X','Y','Z'])

        options(prefix + 'pos_Lm' + suffix, 'legend_names', ['90deg','60deg','30deg'])

        options(prefix + 'vel_gse' + suffix, 'legend_names', ['X[km/s]','Y[km/s]','Z[km/s]'])
        options(prefix + 'vel_gsm' + suffix, 'legend_names', ['X[km/s]','Y[km/s]','Z[km/s]'])
        options(prefix + 'vel_sm' + suffix, 'legend_names', ['X[km/s]','Y[km/s]','Z[km/s]'])

        # set color
        options(prefix + 'pos_gse' + suffix, 'Color', ['b', 'g', 'r'])
        options(prefix + 'pos_gsm' + suffix, 'Color', ['b', 'g', 'r'])
        options(prefix + 'pos_sm' + suffix, 'Color', ['b', 'g', 'r'])

        options(prefix + 'pos_rmlatmlt' + suffix, 'Color', ['b', 'g', 'r'])

        options(prefix + 'pos_blocal' + suffix, 'Color', ['b', 'g', 'r'])

        options(prefix + 'pos_beq' + suffix, 'Color', ['b', 'g', 'r'])

        options(prefix + 'pos_Lm' + suffix, 'Color', ['b', 'g', 'r'])

        options(prefix + 'vel_gse' + suffix, 'Color', ['b', 'g', 'r'])
        options(prefix + 'vel_gsm' + suffix, 'Color', ['b', 'g', 'r'])
        options(prefix + 'vel_sm' + suffix, 'Color', ['b', 'g', 'r'])

        # set y axis to logscale
        options(prefix + 'pos_blocal_mag' + suffix, 'ylog', 1)

        options(prefix + 'pos_beq' + suffix, 'ylog', 1)
    
    elif level == 'l3':

        # remove -1.0e+30
        for i in range(len(loaded_data)):
            get_data_vars = get_data(loaded_data[i])
            if len(get_data_vars) < 3:
                if np.nanmin(get_data_vars[1]) < -1.0e+29:
                    clip(loaded_data[i], -1e+6, 1e6)
                    times, bdata = get_data(loaded_data[i])
                    ylim(loaded_data[i], np.nanmin(bdata), np.nanmax(bdata))

        if model == 'op':
        
            # set ytitle
            options(prefix + 'pos_lmc_op' + suffix, 'ytitle', 'Lmc (op)')
            options(prefix + 'pos_lstar_op' + suffix, 'ytitle', 'Lstar (op)')
            options(prefix + 'pos_I_op' + suffix, 'ytitle', 'I (op)')
            options(prefix + 'pos_blocal_op' + suffix, 'ytitle', 'Blocal (op)')
            options(prefix + 'pos_beq_op' + suffix, 'ytitle', 'Beq (op)')
            options(prefix + 'pos_eq_op' + suffix, 'ytitle', 'Eq_pos (op)')
            options(prefix + 'pos_iono_north_op' + suffix, 'ytitle', 'footprint_north (op)')
            options(prefix + 'pos_iono_south_op' + suffix, 'ytitle', 'footprint_south (op)')

            # set ysubtitle
            options(prefix + 'pos_lmc_op' + suffix, 'ysubtitle', '[dimensionless]')
            options(prefix + 'pos_lstar_op' + suffix, 'ysubtitle', '[dimensionless]')
            options(prefix + 'pos_I_op' + suffix, 'ysubtitle', '[Re]')
            options(prefix + 'pos_blocal_op' + suffix, 'ysubtitle', '[nT]')
            options(prefix + 'pos_beq_op' + suffix, 'ysubtitle', '[nT]')
            options(prefix + 'pos_eq_op' + suffix, 'ysubtitle', '[Re Hour]')
            options(prefix + 'pos_iono_north_op' + suffix, 'ysubtitle', '[deg. deg.]')
            options(prefix + 'pos_iono_south_op' + suffix, 'ysubtitle', '[deg. deg.]')

            # set ylabels
            options(prefix + 'pos_lmc_op' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                        '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_lstar_op' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                        '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_I_op' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                        '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_blocal_op' + suffix, 'legend_names', '|B|')
            options(prefix + 'pos_beq_op' + suffix, 'legend_names', '|B|')
            options(prefix + 'pos_eq_op' + suffix, 'legend_names', ['Re','MLT'])
            options(prefix + 'pos_iono_north_op' + suffix, 'legend_names', ['GLAT','GLON'])
            options(prefix + 'pos_iono_south_op' + suffix, 'legend_names', ['GLAT','GLON'])

            # set y axis to logscale
            options(prefix + 'pos_blocal_op' + suffix, 'ylog', 1)
            options(prefix + 'pos_beq_op' + suffix, 'ylog', 1)

        elif model == 't89':

            # set ytitle
            options(prefix + 'pos_lmc_t89' + suffix, 'ytitle', 'Lmc (t89)')
            options(prefix + 'pos_lstar_t89' + suffix, 'ytitle', 'Lstar (t89)')
            options(prefix + 'pos_I_t89' + suffix, 'ytitle', 'I (t89)')
            options(prefix + 'pos_blocal_t89' + suffix, 'ytitle', 'Blocal (t89)')
            options(prefix + 'pos_beq_t89' + suffix, 'ytitle', 'Beq (t89)')
            options(prefix + 'pos_eq_t89' + suffix, 'ytitle', 'Eq_pos (t89)')
            options(prefix + 'pos_iono_north_t89' + suffix, 'ytitle', 'footprint_north (t89)')
            options(prefix + 'pos_iono_south_t89' + suffix, 'ytitle', 'footprint_south (t89)')

            # set ysubtitle
            options(prefix + 'pos_lmc_t89' + suffix, 'ysubtitle', '[dimensionless]')
            options(prefix + 'pos_lstar_t89' + suffix, 'ysubtitle', '[dimensionless]')
            options(prefix + 'pos_I_t89' + suffix, 'ysubtitle', '[Re]')
            options(prefix + 'pos_blocal_t89' + suffix, 'ysubtitle', '[nT]')
            options(prefix + 'pos_beq_t89' + suffix, 'ysubtitle', '[nT]')
            options(prefix + 'pos_eq_t89' + suffix, 'ysubtitle', '[Re Hour]')
            options(prefix + 'pos_iono_north_t89' + suffix, 'ysubtitle', '[deg. deg.]')
            options(prefix + 'pos_iono_south_t89' + suffix, 'ysubtitle', '[deg. deg.]')

            # set labels
            options(prefix + 'pos_lmc_t89' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                            '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_lstar_t89' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                            '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_I_t89' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                            '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_blocal_t89' + suffix, 'legend_names', '|B|')
            options(prefix + 'pos_beq_t89' + suffix, 'legend_names', '|B|')
            options(prefix + 'pos_eq_t89' + suffix, 'legend_names', ['Re','MLT'])
            options(prefix + 'pos_iono_north_t89' + suffix, 'legend_names', ['GLAT','GLON'])
            options(prefix + 'pos_iono_south_t89' + suffix, 'legend_names', ['GLAT','GLON'])

            # set y axis to logscale
            options(prefix + 'pos_blocal_t89' + suffix, 'ylog', 1)
            options(prefix + 'pos_beq_t89' + suffix, 'ylog', 1)

        elif model == 'ts04':

            # set ytitle
            options(prefix + 'pos_lmc_TS04' + suffix, 'ytitle', 'Lmc (TS04)')
            options(prefix + 'pos_lstar_TS04' + suffix, 'ytitle', 'Lstar (TS04)')
            options(prefix + 'pos_I_TS04' + suffix, 'ytitle', 'I (TS04)')
            options(prefix + 'pos_blocal_TS04' + suffix, 'ytitle', 'Blocal (TS04)')
            options(prefix + 'pos_beq_TS04' + suffix, 'ytitle', 'Beq (TS04)')
            options(prefix + 'pos_eq_TS04' + suffix, 'ytitle', 'Eq_pos (TS04)')
            options(prefix + 'pos_iono_north_TS04' + suffix, 'ytitle', 'footprint_north (TS04)')
            options(prefix + 'pos_iono_south_TS04' + suffix, 'ytitle', 'footprint_south (TS04)')

            # set ysubtitle
            options(prefix + 'pos_lmc_TS04' + suffix, 'ysubtitle', '[dimensionless]')
            options(prefix + 'pos_lstar_TS04' + suffix, 'ysubtitle', '[dimensionless]')
            options(prefix + 'pos_I_TS04' + suffix, 'ysubtitle', '[Re]')
            options(prefix + 'pos_blocal_TS04' + suffix, 'ysubtitle', '[nT]')
            options(prefix + 'pos_beq_TS04' + suffix, 'ysubtitle', '[nT]')
            options(prefix + 'pos_eq_TS04' + suffix, 'ysubtitle', '[Re Hour]')
            options(prefix + 'pos_iono_north_TS04' + suffix, 'ysubtitle', '[deg. deg.]')
            options(prefix + 'pos_iono_south_TS04' + suffix, 'ysubtitle', '[deg. deg.]')

            # set labels
            options(prefix + 'pos_lmc_TS04' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                            '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_lstar_TS04' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                            '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_I_TS04' + suffix, 'legend_names', ['90deg','80deg','70deg','60deg','50deg',
                                                                            '40deg','30deg','20deg','10deg'])
            options(prefix + 'pos_blocal_TS04' + suffix, 'legend_names', '|B|')
            options(prefix + 'pos_beq_TS04' + suffix, 'legend_names', '|B|')
            options(prefix + 'pos_eq_TS04' + suffix, 'legend_names', ['Re','MLT'])
            options(prefix + 'pos_iono_north_TS04' + suffix, 'legend_names',  ['GLAT','GLON'])
            options(prefix + 'pos_iono_south_TS04' + suffix, 'legend_names',  ['GLAT','GLON'])

            # set y axis to logscale
            options(prefix + 'pos_blocal_TS04' + suffix, 'ylog', 1)
            options(prefix + 'pos_beq_TS04' + suffix, 'ylog', 1)

    return loaded_data
