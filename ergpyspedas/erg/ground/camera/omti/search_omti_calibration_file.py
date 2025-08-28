import numpy as np
import datetime
from collections import namedtuple


def search_omti_calibration_file(
    date, 
    site, 
    wavelength, 
    wid_cdf 
    ):
    """
    Select the OMTI calibration file for site and wavelength at the specified date.
    
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

    if site == 'eur':  # Eureka (eur)
        # camera number:
        im = 'F'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2015-05-18T00:00:00'):
            frest = '0001'

    elif site == 'rsb':  # Resolute Bay (rsb)
        # camera number:
        im = '6'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4
        elif wavelength == 5893:
            ch = 6

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2005-01-01T00:00:00'):
            frest = '0002'
 
    elif site == 'ist':  # Istok (ist)
        # camera number:
        im = 'K'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 4861:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2017-10-29T00:00:00'):
            frest = '0001'

    elif site == 'trs':  # Tromsoe (trs)
        # camera number:
        im = 'C'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 5893:
            ch = 4
        elif wavelength == 7320:
            ch = 6

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2009-01-11T00:00:00') <= date <= datetime.datetime.fromisoformat('2023-05-01T00:00:00'):
            frest = '0001'

    elif site == 'hus':  # Husafell (hus)
        # camera number:
        im = 'L'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 4861:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2017-03-21T00:00:00'):
            frest = '0001'

    elif site == 'nai':  # Nain (nai)
        # camera number:
        im = 'H'

        # 4x4 binning pixels:   
        wid0 = wid_cdf * 4

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 4861:
            ch = 4

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2018-09-11T00:00:00') <= date <= datetime.datetime.fromisoformat('2020-01-30T00:00:00'):
            frest = '0001'

    elif site == 'ath':  # Athabasca (ath)
        # camera number:
        im = '7'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 4861:
            ch = 4
        elif wavelength == 8446:
            ch = 6
        elif wavelength == 5893:
            ch = 7

        # calibration file for each observation period:
        if date <= datetime.datetime.fromisoformat('2014-11-17T23:59:59'):
            frest = '2456'
        elif datetime.datetime.fromisoformat('2014-11-18T00:00:00') <= date <= datetime.datetime.fromisoformat('2024-06-10T23:59:59'):  
            frest = '0002'
        elif date >= datetime.datetime.fromisoformat('2024-06-11T00:00:00'):
            frest = '0003'

    elif site == 'zgn':  # Zhigansk (zgn)
        # camera number:
        im = 'E'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 4861:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2019-09-27T00:00:00'):
            frest = '0001'

    elif site == 'gak':  # Gakona (gak)
        # camera number:
        im = 'J'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 4861:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2017-03-03T00:00:00'):
            frest = '0001'

    elif site == 'nyr':  # Nyrola (nyr)
        # camera number:
        im = 'I'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 4861:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2017-01-24T00:00:00'):
            frest = '0001'

    elif site == 'kap':  # Kapuskasing (kap)
        # camera number:
        im = 'G'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 4861:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2017-02-25T00:00:00'):
            frest = '0001'

    elif site == 'ith':  # Ithaca (ith)
        # camera number:
        im = '9'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2006-01-28T00:00:00') <= date <= datetime.datetime.fromisoformat('2007-04-30T23:59:59'):
            frest = '0001'

    elif site == 'mgd':  # Magadan (mgd)
        # camera number:
        im = 'B'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4
        elif wavelength == 4861:
            ch = 6

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2008-11-04T00:00:00') <= date <= datetime.datetime.fromisoformat('2016-05-09T23:59:59'):
            frest = '0001'
        elif date >= datetime.datetime.fromisoformat('2016-05-10T00:00:00'):
            frest = '0002'

    elif site == 'ptk':  # Paratunka (ptk)
        # camera number:
        im = 'A'

        # 2x2 binning pixels:   
        wid0 = wid_cdf * 2

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4
        elif wavelength == 4861:
            ch = 6

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2007-08-17T00:00:00'):
            frest = '0001'

    elif site == 'rik':  # Rikubetsu (rik)
        # camera number:
        if datetime.datetime.fromisoformat('1998-10-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2008-05-19T23:59:59'):
            im = '3'
        elif date >= datetime.datetime.fromisoformat('2008-05-20T00:00:00'):
            im = '9'

        # 2x2 binning pixels for im = '9':
        if im == '9': 
            wid0 = wid_cdf * 2
        # no 2x2 binning pixels for im = '3' 
        elif im == '3':
            wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('1998-10-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2008-05-19T23:59:59'):
            frest = '2456'
        elif datetime.datetime.fromisoformat('2008-05-20T00:00:00') <= date <= datetime.datetime.fromisoformat('2012-06-29T23:59:59'):
            frest = '0001'
        elif date >= datetime.datetime.fromisoformat('2012-06-30T00:00:00'):
            frest = '0002'

    elif site == 'sgk':  # Shigaraki (sgk)
        # camera number:
        im = '1'

        # no 2x2 binning pixels:  
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 5893:
            ch = 4

        # calibration file for each observation period:
        if date <= datetime.datetime.fromisoformat('2000-06-16T23:59:59'):
            frest = '2456'
        elif datetime.datetime.fromisoformat('2000-06-17T00:00:00') <= date <= datetime.datetime.fromisoformat('2000-12-07T23:59:59'):
            frest = '0001'
        elif datetime.datetime.fromisoformat('2000-12-08T00:00:00') <= date <= datetime.datetime.fromisoformat('2006-08-30T23:59:59'):
            frest = '0002'
        elif datetime.datetime.fromisoformat('2006-08-31T00:00:00') <= date <= datetime.datetime.fromisoformat('2006-10-30T23:59:59'):
            frest = '0003'
        elif datetime.datetime.fromisoformat('2006-10-31T00:00:00') <= date <= datetime.datetime.fromisoformat('2007-02-26T23:59:59'):
            frest = '0004'
        elif datetime.datetime.fromisoformat('2007-02-27T00:00:00') <= date <= datetime.datetime.fromisoformat('2012-04-18T23:59:59'):
            frest = '0005'
        elif datetime.datetime.fromisoformat('2012-04-19T00:00:00') <= date <= datetime.datetime.fromisoformat('2023-07-30T23:59:59'):
            frest = '0006'
        elif date >= datetime.datetime.fromisoformat('2023-07-31T00:00:00'):
            frest = '0007'
            
    elif site == 'sta':  # Sata (sta)
        # camera number:
        if datetime.datetime.fromisoformat('2000-07-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2009-07-15T23:59:59'):
            im = '2'
        elif datetime.datetime.fromisoformat('2009-10-28T00:00:00') <= date <= datetime.datetime.fromisoformat('2021-04-08T23:59:59'):
            im = '3'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2

        # calibration file for each observation period:
        if im == '2':
            if date <= datetime.datetime.fromisoformat('2010-08-19T23:59:59'):
                frest = '2456'
        elif im == '3':
            if datetime.datetime.fromisoformat('2010-08-20T00:00:00') <= date <= datetime.datetime.fromisoformat('2012-04-18T23:59:59'):
                frest = '0002'
            elif datetime.datetime.fromisoformat('2012-04-19T00:00:00') <= date <= datetime.datetime.fromisoformat('2013-01-14T23:59:59'):
                frest = '0003'
            elif datetime.datetime.fromisoformat('2013-01-15T00:00:00') <= date <= datetime.datetime.fromisoformat('2016-05-09T23:59:59'):
                frest = '0004'
            elif date >= datetime.datetime.fromisoformat('2016-05-10T00:00:00'):
                frest = '0005'

    elif site == 'yng':  # Yonaguni (yng)
        # camera number:
        if datetime.datetime.fromisoformat('2006-03-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2013-05-07T23:59:59'):
            im = '8'

        # no 2x2 binning pixels:   
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4

        # calibration file for each observation period:
        if date <= datetime.datetime.fromisoformat('2013-08-19T23:59:59'):
            frest = '2456'
        elif datetime.datetime.fromisoformat('2013-08-20T00:00:00') <= date <= datetime.datetime.fromisoformat('2013-05-07T23:59:59'):
            frest = '0002'

    elif site == 'isg':  # Ishigaki (isg)
        # camera number:
        if date >= datetime.datetime.fromisoformat('2014-04-22T00:00:00'):
            im = '8'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2013-08-20T00:00:00'):
            frest = '0002'

    elif site == 'hlk':  # Haleakala (hlk)
        # camera number:
        if date >= datetime.datetime.fromisoformat('2013-03-13T00:00:00'):
            im = '2'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 5893:
            ch = 4

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2013-08-13T00:00:00') <= date <= datetime.datetime.fromisoformat('2016-05-09T23:59:59'):
            frest = '0004'
        if date >= datetime.datetime.fromisoformat('2016-05-10T00:00:00'):
            frest = '0005'

    elif site == 'cmu':  # Chiang Mai (cmu)
        # camera number:
        if date >= datetime.datetime.fromisoformat('2018-08-16T00:00:00'):
            im = '2'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 5893:
            ch = 4

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2018-08-16T00:00:00') <= date <= datetime.datetime.fromisoformat('2025-01-16T23:59:59'):
            frest = '0005'
        elif date >= datetime.datetime.fromisoformat('2025-01-17T00:00:00'):
            frest = '0006'
    elif site == 'cpn':  # Chumphon (cpn)
        # camera number:
        if date >= datetime.datetime.fromisoformat('2020-01-15T00:00:00'):
            im = 'N'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2020-01-15T00:00:00'):
            frest = '0002'

    elif site == 'abu':  # Abuja (abu)
        # camera number:
        if date >= datetime.datetime.fromisoformat('2020-01-15T00:00:00'):
            im = '5'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4

        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2015-06-09T00:00:00'):
            frest = '0002'

    elif site == 'drw':  # Darwin (drw)
        # camera number:
        if datetime.datetime.fromisoformat('2001-10-09T00:00:00') <= date <= datetime.datetime.fromisoformat('2007-03-19T23:59:59'):
            im = '4'
        elif date >= datetime.datetime.fromisoformat('2011-03-19T00:00:00'):
            im = '4'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2001-10-09T00:00:00') <= date <= datetime.datetime.fromisoformat('2006-04-30T23:59:59'):
            frest = '0001'
        elif datetime.datetime.fromisoformat('2006-05-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2007-03-19T23:59:59'):
            frest = '0003'
        elif date >= datetime.datetime.fromisoformat('2011-03-19T00:00:00'):
            frest = '0004'

    elif site == 'ktb':  # Kototabang (ktb)
        # camera number:
        if datetime.datetime.fromisoformat('2002-10-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2010-06-10T23:59:59'):
            im = '5'
        elif date >= datetime.datetime.fromisoformat('2010-06-11T00:00:00'):
            im = 'D'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
        elif wavelength == 6300:
            ch = 2
        elif wavelength == 7774:
            ch = 4

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2002-10-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2010-06-10T23:59:59'):
            frest = '0001'
        elif date >= datetime.datetime.fromisoformat('2010-06-11T00:00:00'):
            frest = '0001'

    elif site == 'syo':  # Syowa Station (syo)
        # camera number:
        if datetime.datetime.fromisoformat('2011-03-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2011-10-01T23:59:59'):
            im = '2'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
            wid0 = wid_cdf * 2  # 2x2 binning pixels
        elif wavelength == 6300:
            ch = 2
            wid0 = wid_cdf * 2  # 2x2 binning pixels
        elif wavelength == 5893:
            ch = 4
            wid0 = wid_cdf  # no 2x2 binning pixels

        # calibration file for each observation period:
        if datetime.datetime.fromisoformat('2011-03-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2011-10-01T23:59:59'):
            frest = '0002'

    elif site == 'syo':  # Skibotn Station (skb)
         # camera number:
        if date >= datetime.datetime.fromisoformat('2023-10-11T00:00:00'):
            im = 'C'

        # no 2x2 binning pixels:
        wid0 = wid_cdf

        # observed wavelength of airglow data:
        if wavelength == 5577:
            ch = 1
            wid0 = wid_cdf * 2  # 2x2 binning pixels
        elif wavelength == 6300:
            ch = 2
            wid0 = wid_cdf * 2  # 2x2 binning pixels
        elif wavelength == 5893:
            ch = 4
            wid0 = wid_cdf * 2  # 2x2 binning pixels
        elif wavelength == 7320:
            ch = 6
            wid0 = wid_cdf * 2  # 2x2 binning pixels
            
        # calibration file for each observation period:
        if date >= datetime.datetime.fromisoformat('2023-10-11T00:00:00'):
            frest = '0001'
            
    filename_ch = f'M{im}C{ch}{frest}.OUT'
    filename_5 = f'M{im}C5{frest}.OUT'
    return Calibration(filename_ch, filename_5, wid0)
