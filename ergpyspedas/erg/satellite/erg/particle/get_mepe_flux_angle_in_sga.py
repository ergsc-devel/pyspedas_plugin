import numpy as np

from astropy.coordinates import cartesian_to_spherical

from .get_mepe_az_dir_in_sga import get_mepe_az_dir_in_sga


def get_mepe_flux_angle_in_sga(looking_dir=False):

    fluxdir = looking_dir

    sgajdir = get_mepe_az_dir_in_sga(fluxdir=fluxdir)

    spherical_data = cartesian_to_spherical(
        x=sgajdir[0],
        y=sgajdir[1],
        z=sgajdir[2]
    )

    rtod = 180. / np.pi
    elev_array = spherical_data[1].value * rtod
    phi_array = spherical_data[2].value * rtod

    anglarr = np.zeros(shape=(2, 3, 16))  # ;[ elev/phi, min/cnt/max, apd_no ]

    for ch in range(15):
        anglarr[0, :, ch] = elev_array[ch]
        anglarr[1, :, ch] = phi_array[ch]

    return anglarr
