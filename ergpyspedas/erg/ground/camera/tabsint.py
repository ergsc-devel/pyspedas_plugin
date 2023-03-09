
from pytplot import tplot_names, get_data
from pyspedas.utilities.download import download
from pyspedas.erg.config import CONFIG
from pyspedas.utilities.dailynames import dailynames


def tabsint(
    site, 
    wavelength=[6300,5725]
    ):
    """
    Calculates the absolute intensity [R] with raw, background, and calibration data, and store tplot variable.
    
    @site: ABB code of observation site
    @wavelength: wavelength of airglow and background image data
    """
    if f'omti_asi_{site}_{wavelength[0]}_image_raw' not in tplot_names():
        return
    
    # airglow image data
    ag_data = get_data(f'omti_asi_{site}_{wavelength[0]}_image_raw')
    # background image data
    bg_data = get_data(f'omti_asi_{site}_{wavelength[1]}_image_raw')
    # airglow exposure time data
    exp_ag_data = get_data(f'omti_asi_{site}_{wavelength[0]}_exposure_time')
    # background exposure time data
    exp_bg_data = get_data(f'omti_asi_{site}_{wavelength[1]}_exposure_time')

    vname1 = f'omti_asi_{site}_{wavelength[0]}_image_raw'

    wid_cdf = ag_data.y.shape[1]

    # Definition of maximum intensity value
    max_int = 65535.0

    #   =================================================================
    #   ---Download calibration data if they do not exist or are updated:
    #   =================================================================

    local_data_dir = CONFIG['local_data_dir']+'ergsc/ground/camera/omti/asi/calibrated_files/'
    remote_data_dir = 'https://stdb2.isee.nagoya-u.ac.jp/omti/data/'
    file_name = 'calibrated_files.zip'

    files = download(remote_file=file_name, remote_path=remote_data_dir, local_path=local_data_dir)
    print(files)
