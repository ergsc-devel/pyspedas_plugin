
import datetime
import numpy as np
from collections import namedtuple


def omti_attitude_params(
    date='2015-05-18T00:00:00', 
    site='sgk'
    ):
    """
    Output the OMTI Imager Attitude Parameters for Coordinate Transformation.
    
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
            date = datetime.datetime.fromisoformat(date)
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

    if site == 'eur':  # Eureka (EUR) : (80.0N, 274.1E)
        lon_obs = 274.10
        lat_obs = 80.0
        alt_obs = 0.127
        if date >= datetime.datetime.fromisoformat('2015-05-18T00:00:00'):
            xm = 255.700
            ym = 269.768
            a_val = 144.598
            rotation = 23.1193
    elif site == 'rsb':   # Resolute Bay (RSB) : (74.7N, 265.1E)
        lon_obs = 265.07
        lat_obs = 74.73
        alt_obs = 0.160
        if date >= datetime.datetime.fromisoformat('2005-01-01T00:00:00'):
            xm = 138.977
            ym = 111.149
            a_val = 75.3824
            rotation = 11.66
    elif site == 'ist':  # Istok (IST) : (70.03N, 88.01E)
        lon_obs = 88.01
        lat_obs = 70.03
        alt_obs = 0.038
        if date >= datetime.datetime.fromisoformat('2017-10-29T00:00:00'):
            xm = 0
            ym = 0
            a_val = 0
            rotation = 0
    elif site == 'trs':  # Tromsoe (TRS) : (69.59N, 19.227E)
        lon_obs = 19.22
        lat_obs = 69.5667
        alt_obs = 0.222
        if date >= datetime.datetime.fromisoformat('2009-01-11T00:00:00'):
            xm = 119.9
            ym = 137.1
            a_val = 75.1
            rotation = -182.2
    elif site == 'hus':  # Husafell (HUS) : (64.67N, 338.97E)
        lon_obs = 338.97
        lat_obs = 64.67
        alt_obs = 0.160
        if date >= datetime.datetime.fromisoformat('2017-03-21T00:00:00'):
            xm = 251.837
            ym = 260.692
            a_val = 164.276
            rotation= -26.239
    elif site == 'nai':  # Nain (NAI) : (56.54N, 298.269E)
        lon_obs = 298.269
        lat_obs = 56.54
        alt_obs = 0.169
        if datetime.datetime.fromisoformat('2018-09-11T00:00:00') <= date <= datetime.datetime.fromisoformat('2018-09-15T23:59:59'):
            xm = 123.6665778
            ym = 125.3363562
            a_val = 80.96082512
            rotation = -29.12566205
        elif date >= datetime.datetime.fromisoformat('2018-09-16T00:00:00'):
            xm = 123.904463
            ym = 126.0769982
            a_val = 81.73187528
            rotation = -29.08460874
    elif site == 'ath':  # Athabasca (ATH) : (54.7N, 246.7E)
        lon_obs = 246.686
        lat_obs = 54.714
        alt_obs = 0.568
        if datetime.datetime.fromisoformat('2005-09-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2006-12-09T23:59:59'):
            xm = 127.225
            ym = 124.343
            a_val = 74.8504
            rotation= 28.02
        elif datetime.datetime.fromisoformat('2006-12-10T00:00:00') <= date <= datetime.datetime.fromisoformat('2012-09-25T23:59:59'):
            xm = 127.419
            ym = 123.502
            a_val = 74.7895
            rotation = 28.10
        elif date >= datetime.datetime.fromisoformat('2012-09-27T00:00:00'):
            xm = 125.544
            ym = 130.819
            a_val = 75.449
            rotation= 9.74
    elif site == 'zgn':  # Zhigansk (ZGN) : (66.78N, 123.37E)
        lon_obs = 123.37
        lat_obs = 66.78
        alt_obs = 0.063
        if date >= datetime.datetime.fromisoformat('2019-09-27T00:00:00'):
            xm = 126.220987
            ym = 128.7920648
            a_val = 81.60706651
            rotation= 28.70376834            
    elif site == 'gak':  # Gakona (GAK) : (62.39N, 214.78E)
        lon_obs = 214.84245
        lat_obs = 62.407119
        alt_obs = 0.586
        if date >= datetime.datetime.fromisoformat('2017-03-03T00:00:00'):
            xm = 257.907
            ym = 256.131
            a_val = 162.620
            rotation= 181.874
    elif site == 'nyr':  # Nyrola (NYR) : (62.34N, 25.51E)
        lon_obs = 25.51
        lat_obs = 62.34
        alt_obs = 0.190
        if date >= datetime.datetime.fromisoformat('2017-01-24T00:00:00'):
            xm = 252.370
            ym = 257.190
            a_val = 163.104
            rotation= -216.268
    elif site == 'kap':  # Kapuskasing (KAP) : (49.39N, 277.81E)
        lon_obs = 277.81
        lat_obs = 49.39
        alt_obs = 0.238
        if date >= datetime.datetime.fromisoformat('2017-02-25T00:00:00'):
            xm = 255.4477
            ym = 259.8555
            a_val = 164.1066
            rotation= -16.066
    elif site == 'ith':  # Ithaca (ITH) : (42.5N, 283.6E)
        lon_obs = 283.56889
        lat_obs = 42.49548
        alt_obs = 0.118
        if datetime.datetime.fromisoformat('2006-06-28T00:00:00') <= date <= datetime.datetime.fromisoformat('2007-04-17T23:59:59'):
            xm = 136.759
            ym = 127.696
            a_val = 74.398
            rotation= -3.51
    elif site == 'mgd':  # Magadan (MGD) : (60.0513467N, 150.7292683E)
        lon_obs = 150.7292683
        lat_obs = 60.0513467
        alt_obs = 0.224
        if datetime.datetime.fromisoformat('2008-11-04T00:00:00') <= date <= datetime.datetime.fromisoformat('2016-05-09T23:59:59'):
            xm = 129.6611349
            ym = 132.7939871
            a_val = 74.74801171
            rotation= -11.68421779
        elif date >= datetime.datetime.fromisoformat('2016-05-10T00:00:00'):
            xm = 121.2306201
            ym = 136.284137
            a_val = 74.70055575
            rotation= -9.571134334
    elif site == 'ptk':  # Paratunka (PTK) : (52.9720466, 158.24762E)
        lon_obs = 158.24762
        lat_obs = 52.9720466
        alt_obs = 0.058
        if date >= datetime.datetime.fromisoformat('2007-08-19T00:00:00'):
            xm = 127.969
            ym = 130.7456
            a_val = 74.63278
            rotation= -7.633543
    elif site == 'rik':  # Rikubetsu (RIK) : (43.5N, 143.8E) 
        lon_obs = 143.7600
        lat_obs = 43.4542
        alt_obs = 0.272
        if datetime.datetime.fromisoformat('1998-10-20T00:00:00') <= date <= datetime.datetime.fromisoformat('1998-10-21T23:59:59'):
            xm = 245.4600
            ym = 253.3814
            a_val = 152.2790
            rotation = 189.6028
        elif datetime.datetime.fromisoformat('1998-10-22T00:00:00') <= date <= datetime.datetime.fromisoformat('1999-03-27T23:59:59'):
            xm = 245.6783
            ym = 255.0890
            a_val = 152.9733
            rotation = 178.1944
        elif datetime.datetime.fromisoformat('1998-04-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2008-05-19T23:59:59'):
            xm = 250.5931
            ym = 253.8743
            a_val = 152.8562
            rotation = -3.5557
        elif date >= datetime.datetime.fromisoformat('2008-05-20T00:00:00'):
            xm = 133.9425
            ym = 128.2934
            a_val = 73.9317
            rotation= 10.333
    elif site == 'sgk':  # Shigaraki (SGK) : (34.8N, 136.1E)
        lon_obs = 136.1089
        lat_obs = 34.8522
        alt_obs = 0.388
        if date <= datetime.datetime.fromisoformat('2000-10-09T23:59:59'):
            xm = 256.0258
            ym = 241.2775
            a_val = 155.4491
            rotation= 0.3817
        elif date >= datetime.datetime.fromisoformat('2000-10-10T00:00:00'):
            xm = 254.2615
            ym = 242.6770
            a_val = 155.9573
            rotation = 0.3982
    elif site == 'sta':  # Sata (STA) : (31.0N, 130.7E)
        lon_obs = 130.6837
        lat_obs = 31.0194
        alt_obs = 0.018
        if date <= datetime.datetime.fromisoformat('2003-08-31T23:59:59'):
            xm = 258.2739
            ym = 258.0548
            a_val = 153.9014
            rotation = -13.2571
        elif datetime.datetime.fromisoformat('2003-09-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2009-07-15T23:59:59'):
            xm = 256.594
            ym = 258.213
            a_val = 153.926
            rotation = -11.6431
        elif datetime.datetime.fromisoformat('2009-10-28T00:00:00') <= date <= datetime.datetime.fromisoformat('2021-04-08T23:59:59'):
            xm = 261.3298
            ym = 258.5835
            a_val = 153.338
            rotation= -10.8249
    elif site == 'yng':  # Yonaguni (YNG): (24.5N, 123.0E)
        lon_obs = 123.020
        lat_obs = 24.4693
        alt_obs = 0.039
        if datetime.datetime.fromisoformat('2006-03-24T00:00:00') <= date <= datetime.datetime.fromisoformat('2009-07-29T23:59:59'):
            xm = 254.017
            ym = 278.050
            a_val = 148.519
            rotation= 18.5446
        elif datetime.datetime.fromisoformat('2010-09-14T00:00:00') <= date <= datetime.datetime.fromisoformat('2013-05-07T23:59:59'):
            xm = 261.121
            ym = 262.952
            a_val = 146.416
            rotation= 18.2932
    elif site == 'isg':  # Ishigaki (ISG): (24.4N, 124.1E)
        lon_obs = 124.1447
        lat_obs = 24.4043
        alt_obs = 0.023
        if date >= datetime.datetime.fromisoformat('2014-04-22T00:00:00'):
            xm = 242.706
            ym = 267.292
            a_val = 148.641
            rotation= 1.71301
    elif site == 'hlk':  # Haleakala (HLK): (20.71N, 203.74E, altitude: 3040m) 
        lon_obs = 203.7422
        lat_obs = 20.7085
        alt_obs = 3.027
        if datetime.datetime.fromisoformat('2013-03-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2016-02-29T23:59:59'):
            xm = 235.6541918
            ym = 262.8874138
            a_val = 154.7773753
            rotation = 106.8006359
    elif site == 'cmu':  # Chiang Mai (CMU): (18.79N, 98.92E)
        lon_obs = 98.9211
        lat_obs = 18.7895
        alt_obs = 0.867
        if date >= datetime.datetime.fromisoformat('2017-03-14T00:00:00'):
            xm = 256.2966
            ym = 254.7530
            a_val = 176.2168
            rotation = -0.4742
    elif site == 'cpn':  # Chumphon (CPN): (10.73N, 99.37E)
        lon_obs = 99.37
        lat_obs = 10.73
        alt_obs = 0.044
        if date >= datetime.datetime.fromisoformat('2020-01-16T00:00:00'):
            xm = 230.59
            ym = 242.19
            a_val = 173.09
            rotation = -0.98
    elif site == 'abu':  # Abuja (ABU): (8.99063N, 7.38359E)
        lon_obs = 7.38
        lat_obs = 8.99
        alt_obs = 0.426
        if date >= datetime.datetime.fromisoformat('2015-06-09T00:00:00'):
            xm = 240.8365
            ym = 268.2431
            a_val = 154.8868
            rotation = 9.3110
    elif site == 'drw':  # Darwin (DRW) : (12.4S, 131.0E)
        lon_obs = 130.955918
        lat_obs = -12.443388
        alt_obs = 0.0444
        if datetime.datetime.fromisoformat('2001-10-09T00:00:00') <= date <= datetime.datetime.fromisoformat('2011-03-18T23:59:59'):
            xm = 237.6321
            ym = 255.7900
            a_val = 153.2353
            rotation = 4.4853
        elif date >= datetime.datetime.fromisoformat('2011-03-19T00:00:00'):
            xm = 248.7333
            ym = 257.2224
            a_val = 151.6393
            rotation=-0.6261
    elif site == 'ktb':  # Kototabang (KTB) : (0.2S, 100.3E)
        lon_obs = 100.32
        lat_obs = -0.2
        alt_obs = 0.865
        if datetime.datetime.fromisoformat('2002-10-26T00:00:00') <= date <= datetime.datetime.fromisoformat('2010-04-06T23:59:59'):
            xm = 246.783
            ym = 255.468
            a_val = 155.572
            rotation = 0.625049
        elif date >= datetime.datetime.fromisoformat('2010-06-11T00:00:00'):
            xm = 243.6771
            ym = 278.7887
            a_val = 153.1178
            rotation= -1.145864
    elif site == 'syo':  # Syowa Station (SYO) : (69.00S, 39.59E)
        lon_obs = 39.582
        lat_obs = -69.0045
        alt_obs = -0.013
        if datetime.datetime.fromisoformat('2011-03-01T00:00:00') <= date <= datetime.datetime.fromisoformat('2011-10-01T23:59:59'):
            xm = 245
            ym = 241
            a_val = 148.6508424
            rotation = 44.2998

    return Attitude(lon_obs, lat_obs, alt_obs, xm, ym, a_val, rotation)
