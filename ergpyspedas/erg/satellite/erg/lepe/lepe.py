import numpy as np
from pyspedas import tplot_rename
from pytplot import clip, get_data, options, store_data, ylim, zlim

from pytplot import time_double


from ..load import load
from ..get_gatt_ror import get_gatt_ror

from typing import List, Optional

def lepe(
    trange: List[str] = ['2017-04-04', '2017-04-05'],
    datatype: str = 'omniflux',
    level: str = 'l2',
    suffix: str = '',
    get_support_data: bool = False,
    varformat: Optional[str] = None,
    varnames: List[str] = [],
    downloadonly: bool = False,
    notplot: bool = False,
    no_update: bool = False,
    uname: Optional[str] = None,
    passwd: Optional[str] = None,
    time_clip: bool = False,
    ror: bool = True,
    version: Optional[str] = None,
    only_fedu: bool = False,
    et_diagram: bool = False,
    force_download: bool = False,
    fine: bool = False,
) -> List[str]:
    """
    This function loads data from the LEP-e experiment from the Arase mission

    Parameters
    ----------
        trange : list of str
            time range of interest [starttime, endtime] with the format
            'YYYY-MM-DD','YYYY-MM-DD'] or to specify more or less than a day
            ['YYYY-MM-DD/hh:mm:ss','YYYY-MM-DD/hh:mm:ss']
            Default: ['2017-04-04','2017-04-05']

        datatype: str
            Data type; Valid 'l1' options: None
            Valid 'l2' options: 'omniflux', '3dflux', '3dflux_finech'
            Valid 'l3' options: 'pa'
            Default: 'omniflux'

        level: str
            Data level; Valid options: 'l1','l2','l3'   Default: 'l2'

        suffix: str
            The tplot variable names will be given this suffix.  Default: None

        get_support_data: bool
            Data with an attribute "VAR_TYPE" with a value of "support_data"
            will be loaded into tplot.  Default: False

        varformat: str
            The file variable formats to load into tplot.  Wildcard character
            "*" is accepted.  Default: None (all variables are loaded)

        varnames: list of str
            List of variable names to load
            Default: [] (all data variables are loaded)

        downloadonly: bool
            Set this flag to download the CDF files, but not load them into
            tplot variables. Default: False

        notplot: bool
            Return the data in hash tables instead of creating tplot variables. Default: False

        no_update: bool
            If set, only load data from your local cache. Default: False

        time_clip: bool
            Time clip the variables to exactly the range specified in the trange keyword. Default: False

        ror: bool
            If set, print PI info and rules of the road. Default: True

        version: str
            Set this value to specify the version of cdf files (such as "v02_02")
            Default: None

        only_fedu: bool
            If set, not make erg_lepe_l3_pa_enech ??(??:01,01,..32)_FEDU Tplot Variables
            Default: False

        et_diagram: bool
            If set, make erg_lepe_l3_pa_pabin ??(??:01,01,..16)_FEDU Tplot Variables
            Default: False

        et_diagram: bool
            If set, make erg_lepe_l3_pa_pabin ??(??:01,01,..16)_FEDU Tplot Variables
            Default: False    

        uname: str
            User name.  Default: None

        passwd: str
            Password.  Default: None

        force_download: bool
            Download file even if local version is more recent than server version
            Default: False


    Returns
    -------
        List of tplot variables created.

    Examples
    --------
    >>> import pyspedas
    >>> from pyspedas import tplot
    >>> lepe_vars = pyspedas.projects.erg.lepe(trange=['2017-03-27', '2017-03-28'])
    >>> tplot('erg_lepe_l2_omniflux_FEDO')


    """
    initial_notplot_flag = False
    if notplot:
        initial_notplot_flag = True

    if level == 'l3':
        datatype = 'pa'

    if fine:
        if (level == 'l2'):
            datatype = '3dflux_finech'
        if (level == 'l3'):
            datatype = 'pa_fine'

    file_res = 3600. * 24
    prefix = 'erg_lepe_'+level+'_' + datatype + '_'
    pathformat = 'satellite/erg/lepe/'+level+'/'+datatype + \
        '/%Y/%m/erg_lepe_'+level+'_'+datatype+'_%Y%m%d_'

    if version is None:
        pathformat += 'v??_??.cdf'
    else:
        pathformat += version + '.cdf'

    loaded_data = load(pathformat=pathformat, trange=trange, level=level, datatype=datatype, file_res=file_res, prefix=prefix, suffix=suffix, get_support_data=get_support_data,
                       varformat=varformat, varnames=varnames, downloadonly=downloadonly, notplot=notplot, time_clip=time_clip, no_update=no_update, uname=uname, passwd=passwd, force_download=force_download)

    if (len(loaded_data) > 0) and ror:

        try:
            gatt = get_gatt_ror(downloadonly, loaded_data)

            # --- print PI info and rules of the road

            print(' ')
            print(
                '**************************************************************************')
            print(gatt["LOGICAL_SOURCE_DESCRIPTION"])
            print('')
            print('Information about ERG LEPe')
            print('')
            print('PI: ', gatt['PI_NAME'])
            print("Affiliation: ",gatt["PI_AFFILIATION"])
            print('')
            print('RoR of ERG project common: https://ergsc.isee.nagoya-u.ac.jp/data_info/rules_of_the_road.shtml.en')
            if level == 'l2':
                print(
                    'RoR of LEPe L2: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepe')
            if level == 'l3':
                print(
                    'RoR of LEPe L3: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Lepe')
                print(
                    'RoR of MGF L2: https://ergsc.isee.nagoya-u.ac.jp/mw/index.php/ErgSat/Mgf')
            print('')
            print('Contact: erg_lepe_info at isee.nagoya-u.ac.jp')
            print(
                '**************************************************************************')
        except:
            print('printing PI info and rules of the road was failed')

    if initial_notplot_flag or downloadonly:
        return loaded_data

    if datatype == 'omniflux':
        tplot_rename(prefix + 'fedo' + suffix,prefix + 'FEDO' + suffix)

        # set spectrogram plot option
        options(prefix + 'FEDO' + suffix, 'Spec', 1)
        # set y axis to logscale
        options(prefix + 'FEDO' + suffix, 'ylog', 1)
        # set ytitle
        options(prefix + 'FEDO' + suffix, 'ytitle', 'ERG\nLEP-e\nFEDO\nEnergy')
        # set ysubtitle
        options(prefix + 'FEDO' + suffix, 'ysubtitle', '[eV]')
        # set ylim
        ylim(prefix + 'FEDO' + suffix, 19, 21*1e3)

        # set z axis to logscale
        options(prefix + 'FEDO' + suffix, 'zlog', 1)
        # set zlim
        zlim(prefix + 'FEDO' + suffix,  1, 1e6)
        # set ztitle
        options(prefix + 'FEDO' + suffix, 'ztitle', '[/s-cm^{2}-sr-eV]')
        # change colormap option
        options(prefix + 'FEDO' + suffix, 'Colormap', 'jet')

        return loaded_data

        
    elif (datatype == '3dflux') or (datatype == '3dflux_finech') and (level == 'l2'):
        tplot_rename(prefix + 'fedu' + suffix,prefix + 'FEDU' + suffix)

        tplot_variables = []

        tplot_variables.append(prefix + 'FEDU' + suffix)
        tplot_variables.append(prefix + 'count_rate' + suffix)
        tplot_variables.append(prefix + 'count_rate_bg' + suffix)

        # set spectrogram plot option
        options(prefix + 'FEDU' + suffix, 'Spec', 1)
        options(prefix + 'count_rate' + suffix, 'Spec', 1)
        options(prefix + 'count_rate_bg' + suffix, 'Spec', 1)

        # set y axis to logscale
        options(prefix + 'FEDU' + suffix, 'ylog', 1)
        options(prefix + 'count_rate' + suffix, 'ylog', 1)
        options(prefix + 'count_rate_bg' + suffix, 'ylog', 1)
        
        # set ysubtitle
        options(prefix + 'FEDU' + suffix, 'ysubtitle', '[eV]')
        options(prefix + 'count_rate' + suffix, 'ysubtitle', '[eV]')
        options(prefix + 'count_rate_bg' + suffix, 'ysubtitle', '[eV]')

        # set ylim
        ylim(prefix + 'FEDU' + suffix, 19, 21*1e3)
        ylim(prefix + 'count_rate' + suffix, 19, 21*1e3)
        ylim(prefix + 'count_rate_bg' + suffix, 19, 21*1e3)

        # set z axis to logscale
        options(prefix + 'FEDU' + suffix, 'zlog', 1)
        options(prefix + 'count_rate' + suffix, 'zlog', 1)
        options(prefix + 'count_rate_bg' + suffix, 'zlog', 1)

        # set ztitle
        options(prefix + 'FEDU' + suffix, 'ztitle', '[/s-cm^{2}-sr-keV]')

        # change colormap option
        options(prefix + 'FEDU' + suffix, 'Colormap', 'jet')
        options(prefix + 'count_rate' + suffix, 'Colormap', 'jet')
        options(prefix + 'count_rate_bg' + suffix, 'Colormap', 'jet')

        return tplot_variables

    elif (level == 'l3'):
        tplot_rename(prefix + 'fedu' + suffix,prefix + 'FEDU' + suffix)
        # set spectrogram plot option
        options(prefix + 'FEDU' + suffix, 'Spec', 1)
        # set z axis to logscale
        options(prefix + 'FEDU' + suffix, 'zlog', 1)
        
        # set ztitle
        options(prefix + 'FEDU' + suffix, 'ztitle', '[/s-cm^{2}-sr-keV]')

        # change colormap option
        options(prefix + 'FEDU' + suffix, 'Colormap', 'jet')

        # set y axis to logscale
        options(prefix + 'FEDU' + suffix, 'ylog', 1)
        
        # set ysubtitle
        options(prefix + 'FEDU' + suffix, 'ysubtitle', '[eV]')
        
        # set ylim
        ylim(prefix + 'FEDU' + suffix, 19, 21*1e3)

        # only_FEDU
        if only_fedu:
            return loaded_data

        elif et_diagram:  # energy-time diagram at pitch-angle bins
            tplot_variables = []
            tplot_variables.append(prefix + 'FEDU' + suffix)
            get_data_vars = get_data(prefix + 'FEDU' + suffix)
            zlim(prefix + 'FEDU' + suffix, 1e2, 1e5)
            options(prefix + 'FEDU' + suffix, 'spec', 1)
            ytitle_pa_array = np.round(np.nan_to_num(get_data_vars[3]), 2)
            for i in range(get_data_vars[1].shape[1]):
                tplot_name = prefix + 'pabin_' + \
                    str(i).zfill(2) + '_FPDU' + suffix
                store_data(tplot_name, data={'x': get_data_vars[0],
                                                'y': get_data_vars[1][:, :, i],
                                                'v': get_data_vars[2]})
                options(tplot_name, 'spec', 1)
                ylim(tplot_name, 19, 21*1e3)
                zlim(tplot_name, 1e0, 1e6)
                options(tplot_name, 'zlog', 1)

                options(tplot_name, 'ytitle', 'ERG LEP-e e\n' +
                        str(ytitle_pa_array[i]) + ' Pitch angle\n eV')
                tplot_variables.append(tplot_name)
            return tplot_variables

        else: # Pitch-angle distributions at energy steps
            tplot_variables = []
            tplot_variables.append(prefix + 'FEDU' + suffix)
            get_data_vars = get_data(prefix + 'FEDU' + suffix)
            zlim(prefix + 'FEDU' + suffix, 1e0, 1e6)
            options(prefix + 'FEDU' + suffix, 'spec', 1)
            ytitle_eV_array = np.round(np.nan_to_num(get_data_vars[2]), 2)
            for i in range(get_data_vars[1].shape[1]):
                tplot_name = prefix + 'engch_' + \
                    str(i).zfill(2) + '_FEDU' + suffix
                store_data(tplot_name, data={'x': get_data_vars[0],
                                                'y': get_data_vars[1][:, i, :],
                                                'v': get_data_vars[3]})
                options(tplot_name, 'spec', 1)
                ylim(tplot_name, 0, 180)
                zlim(tplot_name, 1e2, 1e5)
                options(tplot_name, 'zlog', 1)

                options(tplot_name, 'ytitle', 'ERG LEP-i P\n' +
                        str(ytitle_eV_array[i]) + ' eV\nPitch angle')
                tplot_variables.append(tplot_name)
            return tplot_variables

    