import numpy as np
import pyspedas
from datetime import datetime, timezone


def tasf2gmap(
    vname1,
    vname2,
    grid_x=0.05,
    grid_y=0.05,
    altitude=120.0,
):
    """
    Convert all-sky image data to geographic coordinates.

    Parameters
    ----------
    vname1 : str
        Airglow image tplot variable.
        Expected data shape: (time, image_x, image_y)

    vname2 : str
        Mapping-table tplot variable containing:
        alt, glat and glon.

    grid_x : float, optional
        Longitude resolution [degree].

    grid_y : float, optional
        Latitude resolution [degree].

    altitude : float, optional
        Requested mapping altitude [km].

    Returns
    -------
    str or None
        Created tplot variable name.
    """

    # =========================================
    # Check tplot variables
    # =========================================
    names1 = pyspedas.tnames(vname1)
    names2 = pyspedas.tnames(vname2)

    if len(names1) == 0 or len(names2) == 0:
        print("Cannot find the tplot vars in argument!")
        return None

    raw_name = names1[0]
    map_name = names2[0]

    # =========================================
    # Get tplot data
    # =========================================
    raw_data = pyspedas.get_data(raw_name)
    map_data = pyspedas.get_data(map_name, xarray=True)

    if raw_data is None or map_data is None:
        print("Cannot retrieve the tplot data.")
        return None

    times = np.asarray(raw_data[0])
    images = np.asarray(raw_data[1], dtype=np.float32)

    if images.ndim != 3:
        raise ValueError(
            "The image data must have shape "
            "(time, image_x, image_y). "
            f"Current shape: {images.shape}"
        )

    # =========================================
    # Extract mapping-table coordinates
    # =========================================
    def get_map_component(data, name):
        """Extract a coordinate or variable from xarray data."""

        if name in data.coords:
            return np.asarray(data.coords[name].values)

        if hasattr(data, name):
            value = getattr(data, name)
            return np.asarray(
                value.values if hasattr(value, "values") else value
            )

        attrs = getattr(data, "attrs", {})

        if name in attrs:
            return np.asarray(attrs[name])

        raise KeyError(
            f"'{name}' was not found in mapping variable '{map_name}'. "
            f"Available coordinates: {list(data.coords)}"
        )

    altitudes = get_map_component(map_data, "alt")
    glat_all = get_map_component(map_data, "glat")
    glon_all = get_map_component(map_data, "glon")

    altitudes = np.ravel(altitudes)

    # Nearest altitude, equivalent to IDL nn()
    alt_index = int(
        np.nanargmin(np.abs(altitudes - float(altitude)))
    )

    selected_altitude = float(altitudes[alt_index])

    # Assumed shape: (image_x, image_y, altitude)
    glat = np.asarray(
        glat_all[:, :, alt_index],
        dtype=np.float64
    ).copy()

    glon = np.asarray(
        glon_all[:, :, alt_index],
        dtype=np.float64
    ).copy()

    # Replace fill values
    glat[glat == -999.0] = np.nan
    glon[glon == -999.0] = np.nan

    if images.shape[1:] != glat.shape:
        raise ValueError(
            "Image and mapping-table dimensions do not match: "
            f"image={images.shape[1:]}, map={glat.shape}"
        )

    # =========================================
    # Get site code from tplot variable name
    # =========================================
    name_parts = raw_name.split("_")

    if len(name_parts) < 3:
        raise ValueError(
            f"Wrong tplot variable name: {raw_name}"
        )

    site = name_parts[2]

    # =========================================
    # Geographic range
    # =========================================
    center_x = min(127, glat.shape[0] - 1)
    center_y = min(127, glat.shape[1] - 1)

    min_glat = np.nanmin(glat[center_x, :])
    max_glat = np.nanmax(glat[center_x, :])

    min_glon = np.nanmin(glon[:, center_y])
    max_glon = np.nanmax(glon[:, center_y])

    nx = int((max_glon - min_glon) / grid_x)
    ny = int((max_glat - min_glat) / grid_y)

    if nx <= 0 or ny <= 0:
        raise ValueError(
            f"Invalid geographic grid size: nx={nx}, ny={ny}"
        )

    x_glon = (
        min_glon
        + float(grid_x) * np.arange(nx, dtype=np.float32)
    )

    y_glat = (
        min_glat
        + float(grid_y) * np.arange(ny, dtype=np.float32)
    )

    n_times = len(times)
    n_bins = nx * ny

    image_gmap = np.zeros(
        (n_times, nx, ny),
        dtype=np.float32
    )

    # =========================================
    # Create fixed pixel-grid correspondence
    # =========================================
    #
    # order="F" reproduces IDL's column-major
    # one-dimensional indexing.
    #
    flat_glon = glon.ravel(order="F")
    flat_glat = glat.ravel(order="F")
    raw0 = images[0].ravel(order="F")

    ix = np.floor(
        (flat_glon - min_glon) / grid_x
    ).astype(np.int64)

    iy = np.floor(
        (flat_glat - min_glat) / grid_y
    ).astype(np.int64)

    valid = (
        np.isfinite(flat_glon)
        & np.isfinite(flat_glat)
        & np.isfinite(raw0)
        & (ix >= 0)
        & (ix < nx)
        & (iy >= 0)
        & (iy < ny)
    )

    if not np.any(valid):
        print("No valid pixels were found.")
        return None

    valid_pixel_indices = np.flatnonzero(valid)

    # IDL: bin = ix + nx * iy
    bin_number = (
        ix[valid] + np.int64(nx) * iy[valid]
    )

    # Number of pixels in each geographic cell
    bin_count = np.bincount(
        bin_number,
        minlength=n_bins
    )

    active_bins = bin_count > 0

    # =========================================
    # Grid each time step
    # =========================================
    for i in range(n_times):

        raw = images[i].ravel(order="F")
        raw_valid = raw[valid_pixel_indices]

        # Sum values belonging to each cell
        bin_sum = np.bincount(
            bin_number,
            weights=raw_valid,
            minlength=n_bins
        )

        output_flat = np.zeros(
            n_bins,
            dtype=np.float32
        )

        output_flat[active_bins] = (
            bin_sum[active_bins]
            / bin_count[active_bins]
        )

        # Convert IDL-style flattened grid back to (nx, ny)
        image_gmap[i] = output_flat.reshape(
            (nx, ny),
            order="F"
        )

        if i % 10 == 0:
            date = datetime.fromtimestamp(
                float(times[i]),
                tz=timezone.utc
            )

            print(
                "now converting... : "
                + date.strftime