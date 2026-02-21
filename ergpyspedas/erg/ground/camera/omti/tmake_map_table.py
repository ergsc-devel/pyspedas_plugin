from pyspedas import tplot_names, get_data, store_data
import numpy as np

from ....ground.camera.omti.omti_attitude_params import omti_attitude_params

def tmake_map_table(
    v_name,
    mapping_alt='110',
    grid=None, 
    map_size=None,
    in_km=False
    ):
    """
    Create the mapping table in geographic coordinates, and store tplot variable.
    
    @v_name: tplot variable of airgrow data
    @mapping_alt: Mapping altitude. The default is 110 km
    @grid: grid size
    @map_size: map size. The default is an original image size
    @in_km: if True, unit is km
    """
    # ---Get data from tplot variable with image data:
    if v_name not in tplot_names():
        print('Cannot find the tplot var in argument!')
        return

    times, ag_data = get_data(v_name)  # ---for airglow image

    # ---Get the information of site, date, and wavelength from tplot name:
    str_tnames = v_name.split('_')

    # ---Time in UT
    date = str(times[0])

    # ---Observation site (ABB code)
    site = str_tnames[2]

    # ---Wavelength:
    wavelength = str_tnames[3]

    # ---Get the information of imgsize and map_size from ag_data:
    image_size = len(ag_data[0][:][0])
    if map_size is None:
        map_size = image_size

    # ---Set the map grid in cases of degree or km unit:
    if grid is None:
        if not in_km:
            # ---longitudinal and latitudinal grids of map [deg]:
            grid_lon = grid_lat = 0.01
        else:
            # ---longitudinal and latitudinal grids of map [km]:
            grid_lon = grid_lat = 1.0
    else:
        grid_lon = grid_lat = grid

    # ------Transform the mapping altitude:
    mapping_alt = float(mapping_alt)

    # ---Width of the latitude and longitude that depend on both map and grid sizes:
    width_lon = map_size * grid_lon
    width_lat = map_size * grid_lat

    # ----Get the OMTI Imager Attitude Parameters for Coordinate Transformation:
    result = omti_attitude_params(date=date, site=site)
    lon_obs, lat_obs, alt_obs, x_cent, y_cent, a_val, rot_d = result
    # lon_obs is longitude of observation site [deg];
    # lat_obs is latitude of observation site [deg];
    # alt_obs is altitude of observation site [km];
    # x_cent is x-location of the maximum elevation in an image map;
    # y_cent is y-location of the maximum elevation in an image map;
    # a_val is A value = image diameter(pixel)/3.14159;
    # rot_d is rotation angle [deg].

    # ---If in_km is set, unit is km.
    # ---Set the map grid in a case of degree unit.
    map_unit = 'km' if in_km else 'deg'

    # ---Conversion of rotation angle from degree to radian:
    rot_d = np.deg2rad(rot_d)

    # ---Calculation of radius on Earth ellipsoid as a function of latitude:
    a = 6378.140  # ---Earth radius (Equator) [km]
    b = 6356.755  # ---Earth radius (Pole) [km]

    # ---The Earth radius at a latitude of a site location:
    r = a * b / np.sqrt(np.square(a * np.sin(np.deg2rad(lat_obs))) +
                        np.square(b * np.cos(np.deg2rad(lat_obs))))

    # ---Definition of map and position array
    img_map = np.zeros((2, map_size, map_size), dtype=int)
    img_pos = np.zeros((2, map_size), dtype=float)

    # ---Identification of array number of image data corresponding to latitude (meridional)
    # ---and longitude (zonal) values, and put the position data into the position array

    # ---for loop of y direction:
    for j in range(map_size):
        # ---Calculate the latitude of j location of image:
        if in_km:
            # ---Distance from the map center
            y_img = (j - map_size / 2.0) * grid

            # ---Conversion from a distance to a degree:
            lat_img = lat_obs + np.rad2deg(y_img / (r + mapping_alt))

            # ---Input the position data (meridional direction):
            img_pos[1, j] = y_img
        else:
            # ---Latitude from the map center:
            lat_img = lat_obs - width_lat / 2.0 + j * grid_lat

            # ---Input the position data (latitude):
            img_pos[1, j] = lat_img

        # ---for loop of x direction:
        for i in range(map_size):
            # ---Calculate the longitude of i location of image:
            if in_km:
                # ---Distance from the map center
                x_img = (i - map_size / 2.0) * grid

                # ---Conversion from a distance to a degree:
                lon_img = lon_obs + np.rad2deg(x_img / ((r + mapping_alt)* np.cos(np.deg2rad(lat_img))))

                # ---Input the position data (zonal direction):
                img_pos[0, i] = x_img
            else:
                # ---Longitude from the map center:
                lon_img = lon_obs - width_lon / 2.0 + i * grid_lon

                # ---Input the position data (longitude):
                img_pos[0, i] = lon_img

            # ---Radian value of the longitudinal difference from the j point to the image center:
            aa_rad = np.deg2rad(lon_img - lon_obs)

            # ---Radian value of the latitudinal difference from the pole to the i point:
            b_rad = np.deg2rad(90.0 - lat_img)

            # ---Radian value of the latitudinal difference from the pole to the image center:
            c_rad = np.deg2rad(90.0 - lat_obs)

            cos_a = np.cos(b_rad) * np.cos(c_rad) + np.sin(b_rad) * np.sin(c_rad) * np.cos(aa_rad)
            sin_a = np.sqrt(1.0 - cos_a * cos_a)

            if sin_a != 0.0:
                sin_bb = np.sin(b_rad) * np.sin(aa_rad) / sin_a
                cos_bb = (np.cos(b_rad) * np.sin(c_rad) -
                          np.sin(b_rad) * np.cos(c_rad) * np.cos(aa_rad)) / sin_a
                th_rad = np.arctan(((r + mapping_alt) * sin_a) /
                                   ((r + mapping_alt) * cos_a - (r + alt_obs * 1.0)))

                # ---Correction for fish eye lens distortion ** OMTI version
                th = np.rad2deg(th_rad)
                fc = -2.3483712E-5 * (th ** 3) + 0.0016958048 * (th ** 2) + \
                    2.6996802 * th + 0.26921133
                r_fc = fc * a_val / 156.26124
                x_fc = x_cent + r_fc * sin_bb
                y_fc = y_cent + r_fc * cos_bb
            else:
                x_fc = x_cent
                y_fc = y_cent

            # ---Correction for Rotation:
            x_zo = 2.0 * x_cent - x_fc
            x = (x_zo - x_cent) * np.cos(rot_d) + (y_fc - y_cent) * np.sin(rot_d) + x_cent
            y = (y_fc - y_cent) * np.cos(rot_d) - (x_zo - x_cent) * np.sin(rot_d) + y_cent

            if (x >= 0) and (y >= 0) and (x < image_size) and (y < image_size):
                img_map[0, i, j] = round(x)
                img_map[1, i, j] = round(y)

    # ---Store tplot variable:
    gmap_table_name = f'omti_asi_{site}_{wavelength}_gmap_table_{int(mapping_alt)}'
    store_data(gmap_table_name,
               data={'y': {'map': img_map, 'pos': img_pos, 'z_title': map_unit}})
