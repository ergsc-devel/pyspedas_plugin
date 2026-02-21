import numpy as np
import zipfile
from pyspedas import tplot_names, get_data, store_data
from pyspedas.utilities.download import download
from pyspedas import time_string
from pyspedas.projects.erg.config import CONFIG
from ....ground.camera.omti.search_omti_calibration_file import search_omti_calibration_file
from ....ground.camera.omti.rm_star_absint import rm_star_absint


def tabsint(
        site,
        wavelength=(6300, 5725)
):
    """
    Calculates the absolute intensity [R] with raw, background, and calibration data, and store tplot variable.
    
    @site: ABB code of observation site
    @wavelength: wavelength of airglow and background image data
    """

    # search for tplot variable with raw data
    v_name1 = f'omti_asi_{site}_{wavelength[0]}_image_raw'

    if v_name1 not in tplot_names():
        print(f"The tplot variable '{v_name1}' is not found")
        return

    # airglow image data
    times_ag, ag_data = get_data(v_name1)
    var_attrs = get_data(v_name1, metadata=True)

    # background image data
    times_bg, bg_data = get_data(f'omti_asi_{site}_{wavelength[1]}_image_raw')

    # airglow exposure time data
    _, exp_ag_data = get_data(f'omti_asi_{site}_{wavelength[0]}_exposure_time')

    # background exposure time data
    _, exp_bg_data = get_data(f'omti_asi_{site}_{wavelength[1]}_exposure_time')

    # get the image size from tplot variables:
    wid_cdf = ag_data.shape[1]

    # definition of maximum intensity value
    max_int = 65535.0

    #   =================================================================
    #   Download calibration data if they do not exist or are updated:
    #   =================================================================

    local_data_dir = CONFIG['local_data_dir'] + 'ergsc/ground/camera/omti/asi/calibrated_files/'
    remote_data_dir = 'https://stdb2.isee.nagoya-u.ac.jp/omti/data/'
    file_name = 'calibrated_files.zip'

    files = download(remote_file=file_name, remote_path=remote_data_dir, local_path=local_data_dir)

    # UNIX time in UT
    date = times_ag[0]
    # obtain the search result of OMTI calibration file
    calibration = search_omti_calibration_file(date, site, wavelength[0], wid_cdf)

    # calibration image width
    wid0 = calibration.width

    # definition of absolute image data array from time and cdf image size
    abs_img_ag_int = np.zeros((len(times_ag), wid_cdf, wid_cdf), dtype=float)

    with zipfile.ZipFile(local_data_dir + file_name, mode='r') as archive:
        file_data = [s.decode() for s in archive.read(calibration.filename_ch).split(b'\n')][1:]

    # bandwidth of airglow filter and transmission at wl (airglow)
    _, bandwidth_airglow, transmission_airglow = [float(c) for c in file_data[0].split()]

    airglow_cal_data = np.array([[float(c) for c in line.split()] for line in file_data[1:] if line])
    data_length = airglow_cal_data.shape[0]
    if data_length < int(wid0) * int(wid0) // 4:
        wid0 /= 2

    # calibration image (A [cnt/R/s]) airglow filter
    cal_ag = np.zeros((wid_cdf, wid_cdf), dtype=float)
    cal_ag0 = airglow_cal_data.reshape(wid0, wid0)

    # calibration image (Ab [cnt/R/s]) background filter
    cal_bg = np.zeros((wid_cdf, wid_cdf), dtype=float)

    with zipfile.ZipFile(local_data_dir + file_name, mode='r') as archive:
        file_data = [s.decode() for s in archive.read(calibration.filename_5).split(b'\n')][1:]

    # bandwidth of background filter and transmission at wl(background)
    _, bandwidth_background, transmission_background = [float(c) for c in file_data[0].split()]

    background_cal_data = np.array([[float(c) for c in line.split()] for line in file_data[1:] if line])
    data_length = background_cal_data.shape[0]
    if data_length < int(wid0) * int(wid0) // 4:
        wid0 /= 2

    cal_bg0 = background_cal_data.reshape(wid0, wid0)

    if wid0 == wid_cdf:  # no binning for airglow and background filters
        cal_ag = np.copy(cal_ag0)
        cal_bg = np.copy(cal_bg0)
    elif wid0 // wid_cdf == 2:  # 2x2 binning
        for i in range(wid_cdf):
            for j in range(wid_cdf):
                cal_ag[i][j] = (cal_ag0[i * 2][j * 2] + cal_ag0[i * 2 + 1][j * 2] + cal_ag0[i * 2][j * 2 + 1] +
                                cal_ag0[i * 2 + 1][j * 2 + 1]) / 4.0
                cal_bg[i][j] = (cal_bg0[i * 2][j * 2] + cal_bg0[i * 2 + 1][j * 2] + cal_bg0[i * 2][j * 2 + 1] +
                                cal_bg0[i * 2 + 1][j * 2 + 1]) / 4.0
    elif wid0 // wid_cdf == 4:  # 4x4 binning
        for i in range(wid_cdf):
            for j in range(wid_cdf):
                cal_ag[i][j] = (cal_ag0[i * 4][j * 4] + cal_ag0[i * 4 + 1][j * 4] + cal_ag0[i * 4 + 2][j * 4] +
                                cal_ag0[i * 4 + 3][j * 4] +
                                cal_ag0[i * 4][j * 4 + 1] + cal_ag0[i * 4 + 1][j * 4 + 1] +
                                cal_ag0[i * 4 + 2][j * 4 + 1] + cal_ag0[i * 4 + 3][j * 4 + 1] +
                                cal_ag0[i * 4][j * 4 + 2] + cal_ag0[i * 4 + 1][j * 4 + 2] +
                                cal_ag0[i * 4 + 2][j * 4 + 2] + cal_ag0[i * 4 + 3][j * 4 + 2] +
                                cal_ag0[i * 4][j * 4 + 3] + cal_ag0[i * 4 + 1][j * 4 + 3] +
                                cal_ag0[i * 4 + 2][j * 4 + 3] + cal_ag0[i * 4 + 3][j * 4 + 3]) / 16.0
                cal_bg[i][j] = (cal_bg0[i * 4][j * 4] + cal_bg0[i * 4 + 1][j * 4] + cal_bg0[i * 4 + 2][j * 4] +
                                cal_bg0[i * 4 + 3][j * 4] +
                                cal_bg0[i * 4][j * 4 + 1] + cal_bg0[i * 4 + 1][j * 4 + 1] +
                                cal_bg0[i * 4 + 2][j * 4 + 1] + cal_bg0[i * 4 + 3][j * 4 + 1] +
                                cal_bg0[i * 4][j * 4 + 2] + cal_bg0[i * 4 + 1][j * 4 + 2] +
                                cal_bg0[i * 4 + 2][j * 4 + 2] + cal_bg0[i * 4 + 3][j * 4 + 2] +
                                cal_bg0[i * 4][j * 4 + 3] + cal_bg0[i * 4 + 1][j * 4 + 3] +
                                cal_bg0[i * 4 + 2][j * 4 + 3] + cal_bg0[i * 4 + 3][j * 4 + 3]) / 16.0

    # ;============================================
    # ;---Conversion from count rate to intensity:
    # ;============================================

    debin = 4.0 if wid_cdf == wid0 // 2 else 1.0

    for i in range(len(times_ag)):

        # star remover
        img_ag0 = ag_data[i]
        img_ag = rm_star_absint(img_ag0, wid_cdf)

        # 2x2 binning
        img_ag = img_ag / debin

        # dark count (airglow image)
        dc_ag = np.median(img_ag[5:10, 5:10])

        # Initialize the value:
        ref_bg1 = -1
        ref_bg2 = -1

        if times_ag[i] <= times_bg[0]:
            ref_bg1 = 0
            ref_bg2 = 0
        elif times_ag[i] >= times_bg[-1]:
            ref_bg1 = len(times_bg) - 1
            ref_bg2 = len(times_bg) - 1
        else:
            for ib in range(len(times_bg)):
                if times_bg[ib] >= times_ag[i]:
                    ref_bg1 = ib - 1
                    ref_bg2 = ib
                    break

        # exposure time of airglow and background image data
        exp_ag = exp_ag_data[i]
        exp_bg = exp_bg_data[ref_bg1]

        img_bg_ref = np.zeros((wid_cdf, wid_cdf, 2), dtype=float)
 #       img_bg_int = np.zeros((wid_cdf, wid_cdf), dtype=float)

        # background image 1
        img_bg0 = bg_data[ref_bg1]

        # 2x2 binning
        img_bg0 = img_bg0 / debin

        # star remover
        img_bgs = rm_star_absint(img_bg0, wid_cdf)
        if site == 'syo' and wavelength != 5893:
            img_bg_ref[:, :, 0] = np.copy(img_bgs[:wid_cdf, :wid_cdf])
        else:
            img_bg_ref[:, :, 0] = np.copy(img_bgs)

        # background image 2
        img_bg0 = bg_data[ref_bg2]

        # 2x2 binning
        img_bg0 = img_bg0 / debin

        # star remover
        img_bgs = rm_star_absint(img_bg0, wid_cdf)
        if site == 'syo' and wavelength != 5893:
            img_bg_ref[:, :, 1] = np.copy(img_bgs[:wid_cdf, :wid_cdf])
        else:
            img_bg_ref[:, :, 1] = np.copy(img_bgs)

        # dark count (airglow image)
        dc_bg = np.median(img_bg_ref[5:10, 5:10, :])

        # =======================================================================
        # ---Background / airglow calculation (absolute intensity [R])
        # =======================================================================

        # background count correction (linear interpolation)
        ktm = 0
        if times_bg[ref_bg2] != times_bg[ref_bg1]:
            ktm = (img_bg_ref[:, :, 1] - img_bg_ref[:, :, 0]) / (times_bg[ref_bg2] - times_bg[ref_bg1])
        mod_bg = img_bg_ref[:, :, 0] + (times_ag[i] - times_bg[ref_bg1]) * ktm

        # Ibg [R/nm] = ( Nb - DKb ) * T(lb) / ( Ab * tb * dFb )
        bg_int = (mod_bg - dc_bg) * transmission_background / (cal_bg * exp_bg * bandwidth_background)

        # cal_bg <= 0 ---> bg_int = 0.0
        idx = np.where(cal_bg <= 0)
        bg_int[idx] = 0

        # bg_int < 0 ---> bg_int = 0.0 
        idx = np.where(bg_int < 0)
        bg_int[idx] = 0

        # bg_int >  max_int ---> bg_int = max_int
        idx = np.where(bg_int > max_int)
        bg_int[idx] = max_int

        # create airglow image (absolute intensity [R])
        ag_int = (img_ag - cal_ag * exp_ag * bg_int * bandwidth_airglow / transmission_airglow - dc_ag) \
            / (cal_ag * exp_ag)

        # cal_ag <= 0 and bg_int <= 0 ---> ag_int = 0.0
        idx = np.where((cal_ag <= 0) & (bg_int <= 0))
        ag_int[idx] = 0

        # ag_int < 0 ---> ag_int = 0.0 
        idx = np.where(ag_int < 0)
        ag_int[idx] = 0

        # ag_int >  max_int ---> ag_int = max_int
        idx = np.where(ag_int > max_int)
        ag_int[idx] = max_int

        ag_int[0][0] = max_int
        ag_int[wid_cdf - 1][wid_cdf - 1] = max_int

        # abs_img_ag_int[i, :, :] = np.copy(ag_int)
        abs_img_ag_int[i] = np.copy(ag_int)
        print('now converting...:', time_string(times_ag[i]))

    # storing data to several plots
    store_data(f'{v_name1[:24]}abs', data={'x': times_ag, 'y': abs_img_ag_int}, attr_dict=var_attrs)
