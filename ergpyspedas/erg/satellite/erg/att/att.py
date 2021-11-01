import pandas as pd
from pyspedas.analysis.time_clip import time_clip as tclip
from pyspedas.utilities.dailynames import dailynames
from pyspedas.utilities.download import download
from pyspedas.utilities.time_double import time_float
from pytplot import store_data
from ..config import CONFIG


def att(trange=['2017-04-01', '2017-04-02'],
        level='l2',
        downloadonly=False,
        no_update=False,
        uname=None,
        passwd=None):
    """
    This function loads attitude data from the Arase mission

    Parameters:
        trange : list of str
            time range of interest [starttime, endtime] with the format 
            'YYYY-MM-DD','YYYY-MM-DD'] or to specify more or less than a day 
            ['YYYY-MM-DD/hh:mm:ss','YYYY-MM-DD/hh:mm:ss']

        level: str
            Data level; Valid options:

        downloadonly: bool
            Set this flag to download the files, but not load them into 
            tplot variables

        no_update: bool
            If set, only load data from your local cache

    Returns:
        None

    """
    file_res = 24*3600.
    pathformat = 'satellite/erg/att/txt/erg_att_'+level+'_%Y%m%d_v??.txt'
    remote_names = dailynames(file_format=pathformat,
                              trange=trange, res=file_res)
    files = download(remote_file=remote_names, remote_path=CONFIG['remote_data_dir'], local_path=CONFIG[
                     'local_data_dir'], no_download=no_update, last_version=True, username=uname, password=passwd)
    out_files = []

    if files is not None:
        for file in files:
            out_files.append(file)

    out_files = sorted(out_files)

    if downloadonly:
        return out_files

    data_flame_list = []
    for file in out_files:
        raw_read_table = pd.read_table(file)
        data_flame_list.append(
            raw_read_table[10:][raw_read_table.keys()[0]].str.split(expand=True))

    concat_frame_for_tplot = pd.concat(data_flame_list)
    time_float_array = time_float(concat_frame_for_tplot.iloc[:, 0])

    Omega_float_array = concat_frame_for_tplot.iloc[:, 1].astype(float)
    Phase_float_array = concat_frame_for_tplot.iloc[:, 9].astype(float)
    I_Alpha_float_array = concat_frame_for_tplot.iloc[:, 2].astype(float)
    I_Delta_float_array = concat_frame_for_tplot.iloc[:, 3].astype(float)
    GX_Alpha_float_array = concat_frame_for_tplot.iloc[:, 10].astype(float)
    GX_Delta_float_array = concat_frame_for_tplot.iloc[:, 11].astype(float)
    GZ_Alpha_float_array = concat_frame_for_tplot.iloc[:, 12].astype(float)
    GZ_Delta_float_array = concat_frame_for_tplot.iloc[:, 13].astype(float)

    store_data('erg_att_sprate', data={
               'x': time_float_array, 'y': Omega_float_array})
    store_data('erg_att_spphase', data={
               'x': time_float_array, 'y': Phase_float_array})
    store_data('erg_att_izras', data={
               'x': time_float_array, 'y': I_Alpha_float_array})
    store_data('erg_att_izdec', data={
               'x': time_float_array, 'y': I_Delta_float_array})
    store_data('erg_att_gxras', data={
               'x': time_float_array, 'y': GX_Alpha_float_array})
    store_data('erg_att_gxdec', data={
               'x': time_float_array, 'y': GX_Delta_float_array})
    store_data('erg_att_gzras', data={
               'x': time_float_array, 'y': GZ_Alpha_float_array})
    store_data('erg_att_gzdec', data={
               'x': time_float_array, 'y': GZ_Delta_float_array})

    return None
