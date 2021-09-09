from pyspedas.utilities.dailynames import dailynames
from pyspedas.utilities.download import download
from pyspedas.analysis.time_clip import time_clip as tclip
from pytplot import cdf_to_tplot

#from .config import CONFIG
from config import CONFIG

def load(trange=['2017-03-27', '2017-03-28'], 
         pathformat=None,
         instrument='mgf',
         datatype='8sec', 
         mode=None,
         site=None,
         model=None,
         level='l2', 
         prefix='',
         suffix='',
         file_res=24*3600.,
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
    This function is not meant to be called directly; please see the instrument specific wrappers:
        pyspedas.erg.mgf()
        pyspedas.erg.hep()
        pyspedas.erg.orb()
        pyspedas.erg.lepe()
        pyspedas.erg.lepi()
        pyspedas.erg.mepe()
        pyspedas.erg.mepi()
        pyspedas.erg.pwe_ofa()
        pyspedas.erg.pwe_efd()
        pyspedas.erg.pwe_hfa()
        pyspedas.erg.xep()
    """

    if prefix == None:
        print('prefix == None:')
        prefix = 'erg_'+instrument+'_'+level+'_'

    if pathformat == None:
        print('pathformat == None')
        print('pathformat == None')
        print('pathformat == None')
        print('pathformat == None')
        file_res=24*3600.
        if instrument == 'mgf':
            if datatype == '8sec':
                pathformat = 'satellite/erg/'+instrument+'/'+level+'/'+datatype+'/%Y/%m/erg_'+instrument+'_'+level+'_'+datatype+'_%Y%m%d_v??.??.cdf'
            else:
                file_res=3600.
                pathformat = 'satellite/erg/'+instrument+'/'+level+'/'+datatype+'/%Y/%m/erg_'+instrument+'_'+level+'_'+datatype+'_dsi_%Y%m%d%H_v??.??.cdf'

        elif instrument == 'orb':
            if level == 'l3':
                if model == 'op':
                    pathformat = 'satellite/erg/'+instrument+'/'+level+'/opq/%Y/%m/erg_'+instrument+'_'+level+'_op_%Y%m%d_'
                else:
                    pathformat = 'satellite/erg/'+instrument+'/'+level+'/'+model+'/%Y/%m/erg_'+instrument+'_'+level+'_'+model+'_%Y%m%d_'
            elif level == 'l2':
                if datatype == 'def':
                    pathformat = 'satellite/erg/'+instrument+'/'+ datatype +'/%Y/erg_'+instrument+'_'+level+'_%Y%m%d_'
                else:
                    pathformat = 'satellite/erg/'+instrument+'/'+ datatype +'/%Y/erg_'+instrument+'_'+ datatype + '_'+level+'_%Y%m%d_'


            if version == None:
                pathformat += 'v??.cdf'
            else:
                pathformat += version + '.cdf'


        elif instrument == 'pwe_efd':
            pathformat = 'satellite/erg/pwe/efd/'+level+'/'+datatype+'/%Y/%m/erg_'+instrument+'_'+level+'_'+datatype+'_%Y%m%d_v??_??.cdf'
        elif instrument == 'pwe_hfa':
            if level == 'l2':
                pathformat = 'satellite/erg/pwe/hfa/'+level+'/'+datatype+'/'+mode+'/%Y/%m/erg_'+instrument+'_'+level+'_'+datatype+'_'+mode+'_%Y%m%d_v??_??.cdf'
            elif level == 'l3':
                pathformat = 'satellite/erg/pwe/hfa/'+level+'/%Y/%m/erg_'+instrument+'_'+level+'_1min_%Y%m%d_v??_??.cdf'
        elif instrument == 'xep':
            pathformat = 'satellite/erg/'+instrument+'/'+level+'/'+datatype+'/%Y/%m/erg_'+instrument+'_'+level+'_'+datatype+'_%Y%m%d_v??_??.cdf'

    # find the full remote path names using the trange
    remote_names = dailynames(file_format=pathformat, trange=trange, res=file_res)

    out_files = []

    files = download(remote_file=remote_names, remote_path=CONFIG['remote_data_dir'], local_path=CONFIG['local_data_dir'], no_download=no_update, last_version=True, username=uname, password=passwd)
    if files is not None:
        for file in files:
            out_files.append(file)

    out_files = sorted(out_files)

    if downloadonly:
        return out_files

    tvars = cdf_to_tplot(out_files, prefix=prefix, suffix=suffix, get_support_data=get_support_data, varformat=varformat, varnames=varnames, notplot=notplot)
    
    if notplot:
        return tvars

    if time_clip:
        for new_var in tvars:
            tclip(new_var, trange[0], trange[1], suffix='')

    return tvars