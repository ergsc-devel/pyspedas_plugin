import datetime
import numpy as np
from collections import namedtuple


def zwo_attitude_params(
    date='2025-09-08T00:00:00', 
    site='sto',
    wavelength,
    ):
    """
    Output the ZWO camera for Coordinate Transformation.
    
    @date: time (datetime, string, int, float, np.integer, np.float64)
    @site: site name (ABB code)
    @return: namedtuple('Attitude',
                          [
                           'lon_obs',  # longitude of observation site [deg] 
                           'lat_obs',  # latitude of observation site [deg]
                           'alt_obs',  # altitude of observation site [km]
                           'xm',  # x-location of the maximum elevation in an image map
                           'ym',  # y-location of the maximum elevation in an image map
                           'a_val', # A value = image diameter(pixel)/3.14159
                           'rotation' # rotation angle [deg]
                           ]
                          )
    """

    if not isinstance(date, datetime.datetime):
        if isinstance(date, str):
            try:
                date = datetime.datetime.fromisoformat(date)
            except ValueError:
                date = datetime.datetime.utcfromtimestamp(float(date))
        elif isinstance(date, (int, float, np.integer, np.float64)):
            date = datetime.datetime.utcfromtimestamp(date)

    Attitude = namedtuple('Attitude',
                          [
                           'lon_obs',  # longitude of observation site [deg] 
                           'lat_obs',  # latitude of observation site [deg]
                           'alt_obs',  # altitude of observation site [km]
                           'xm',  # x-location of the maximum elevation in an image map
                           'ym',  # y-location of the maximum elevation in an image map
                           'a_val',  # A value = image diameter(pixel)/3.14159
                           'rotation'  # rotation angle [deg]
                           ]
                          )

    site = site.lower()

    if site == 'sto':  # Sto (STO) : (80.0N, 274.1E)
        lon_obs = 15.14
        lat_obs = 69.01
        alt_obs = 0.811
        if date >= datetime.datetime.fromisoformat('2025-09-08T00:00:00'):
            if wavelength == 6300:
                xm = 399.18444
                ym = 380.011444
                a_val = 194.24311
                rotation = -15.000
            if wavelength == 6300:
                xm = 385.779
                ym = 404.343
                a_val = 194.246
                rotation = -18.0000
    elif site == 'alx':   # Alexiandria (ALX) : (30.86N  29.56E)
        lon_obs = 30.86
        lat_obs = 29.56
        alt_obs = 0.008
        if date >= datetime.datetime.fromisoformat('2025-10-16T00:00:00'):
            if wavelength == 6300:
                xm = 414.1230809
                ym = 379.1550643
                a_val = 193.5310252
                rotation = -5.572019987
            if wavelength == 5577:
                xm = 413.9080667
                ym = 399.4596561
                a_val = 191.3120104
                rotation = 3.57414936
            if wavelength == 7200:
                xm = 400.2199309
                ym = 403.1977052
                a_val = 192.9758405
                rotation = 3.288370199
            
    return Attitude(lon_obs, lat_obs, alt_obs, xm, ym, a_val, rotation)
