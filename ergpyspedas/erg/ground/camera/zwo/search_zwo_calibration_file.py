import numpy as np
import datetime
from collections import namedtuple


def search_zwo_calibration_file(
    date, 
    site, 
    wavelength, 
    wid_cdf 
    ):
    """
    Select the ZWO camera calibration file for site and wavelength at the specified date.
    
    @date: Unix time
    @site: Site name (ABB code)
    @wavelength: Observed wavelength for airglow
    @wid_cdf: width of image
    """

    site = site.lower()
    wavelength = int(wavelength)

    if not isinstance(date, datetime.datetime):
        if isinstance(date, str):
            date = datetime.datetime.fromisoformat(date)
        elif isinstance(date, (int, float, np.integer, np.float64)):
            date = datetime.datetime.utcfromtimestamp(date)

    Calibration = namedtuple('Calibration',
                             [
                              'filename_ch',
                              'filename_5',
                              'width'
                             ])

    if site == 'sta':  # Sata (sta)
        # camera number:
        im = '001'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = '01'
        elif wavelength == 6300:
            ch = '02'
        elif wavelength == 4861:
            ch = '04'

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2021-08-11T00:00:00'):
            frest = '_20210802'

    elif site == 'zug':  # Zugspitze (zug)
        # camera number:
        im = '002'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = '01'
        elif wavelength == 6300:
            ch = '02'
        elif wavelength == 7774:
            ch = '04'

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2023-09-06T00:00:00'):
            frest = '_20230731'
 
    elif site == 'sto':  # Sto (sto)

        # 4x4 binning pixels:   
        wid0 = wid_cdf * 4

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = '01'
            # camera number:
            im = '011'
        elif wavelength == 6300:
            ch = '01'
            # camera number:
            im = '010'

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2017-10-29T00:00:00'):
            frest = '_20240611'

    elif site == 'alx':  # Alexiandria (alx)

        # 4x4 binning pixels:   
        wid0 = wid_cdf * 4

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = '01'
            # camera number:
            im = '004'
        elif wavelength == 6300:
            ch = '02'
            # camera number:
            im = '003'

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2025-10-12T00:00:00'):
            frest = '_20220107'
            
    filename_ch = f'Z{im}{ch}{frest}.OUT'
    filename_5 = f'Z{im}05{frest}.OUT'
    return Calibration(filename_ch, filename_5, wid0)
