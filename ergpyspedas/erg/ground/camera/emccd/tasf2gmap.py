from datetime import datetime, timezone

import numpy as np
import pyspedas
from scipy.ndimage import distance_transform_edt


def fill_empty_cells(
    image,
    valid_mask,
    max_distance=None,
):
    """
    Fill empty cells using values from the nearest valid cell.

    Parameters
    ----------
    image : ndarray
        Two-dimensional gridded image.

    valid_mask : ndarray of bool
        True for cells containing observation data.

    max_distance : float or None
        Maximum filling distance in grid cells.
        None fills all empty cells.

    Returns
    -------
    ndarray
        Filled image.
    """

    image = np.asarray(image)
    valid_mask = np.asarray(valid_mask, dtype=bool)

    if image.shape != valid_mask.shape:
        raise ValueError(
            "image and valid_mask must have the same shape: "
            f"{image.shape} != {valid_mask.shape}"
        )

    if not np.any(valid_mask):
        return image.copy()

    distances, nearest_indices = distance_transform_edt(
        ~valid_mask,
        return_indices=True,
    )

    nearest_values = image[
        nearest_indices[0],
        nearest_indices[1],
    ]

    if max_distance is None:
        fill_mask = ~valid_mask
    else:
        fill_mask = (
            (~valid_mask)
            & (distances <= float(max_distance))
        )

    filled_image = image.copy()
    filled_image[fill_mask] = nearest_values[fill_mask]

    return filled_image


def tasf2gmap(
    vname1,
    vname2,
    grid_x=0.05,
    grid_y=0.05,
    altitude=120.0,
    fill_empty=True,
    max_fill_distance=3.0,
):
    """
    Convert all-sky image data to geographic coordinates.

    Parameters
    ----------
    vname1 : str
        Airglow image tplot variable.
        Expected shape is (time, image_x, image_y).

    vname2 : str
        Mapping-table tplot variable containing glat, glon,
        and altitude in its attributes.

    grid_x : float
        Longitude resolution in degrees.

    grid_y : float
        Latitude resolution in degrees.

    altitude : float
        Requested mapping altitude in kilometres.

    fill_empty : bool
        Fill empty grid cells using nearest-neighbour values.

    max_fill_distance : float or None
        Maximum filling distance in grid cells.
        None fills every empty cell.

    Returns
    -------
    str or None
        Created tplot variable name.
    """

    grid_x = float(grid_x)
    grid_y = float(grid_y)

    if grid_x <= 0.0 or grid_y <= 0.0:
        raise ValueError(
            "grid_x and grid_y must be greater than zero."
        )

    if (
        max_fill_distance is not None
        and float(max_fill_distance) < 0.0
    ):
        raise ValueError(
            "max_fill_distance must be zero or greater."
        )

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

    map_data = pyspedas.get_data(
        map_name,
        xarray=True,
    )

    if raw_data is None or map_data is None:
        print("Cannot retrieve the tplot data.")
        return None

    times = np.asarray(
        raw_data[0],
        dtype=np.float64,
    )

    images = np.asarray(
        raw_data[1],
        dtype=np.float32,
    )

    if images.ndim != 3:
        raise ValueError(
            "Image data must have shape "
            "(time, image_x, image_y): "
            f"{images.shape}"
        )

    if times.size != images.shaperaise ValueError(
            "Time and image dimensions do not match: "
            f"time={times.size}, images={images.shape[0]}"
        )

    # =========================================
    # Read mapping-table components
    # =========================================
    def get_map_component(data, name):
        if name in data.coords:
            return np.asarray(
                data.coords[name].values
            )

        if hasattr(data, name):
            value = getattr(data, name)

            if hasattr(value, "values"):
                value = value.values

            return np.asarray(value)

        attrs = getattr(data, "attrs", {})

        if name in attrs:
            return np.asarray(attrs[name])

        raise KeyError(
            f"'{name}' was not found in '{map_name}'. "
            f"Coordinates={list(data.coords)}, "
            f"attributes={list(attrs.keys())}"
        )

    altitudes = get_map_component(
        map_data,
        "altitude",
    )

    glat_all = get_map_component(
        map_data,
        "glat",
    )

    glon_all = get_map_component(
        map_data,
        "glon",
    )

    altitudes = np.asarray(
        altitudes,
        dtype=np.float64,
    ).reshape(-1)

    glat_all = np.asarray(
        glat_all,
        dtype=np.float64,
    )

    glon_all = np.asarray(
        glon_all,
        dtype=np.float64,
    )

    if altitudes.size == 0:
        raise ValueError("The altitude array is empty.")

    if not np.any(np.isfinite(altitudes)):
        raise ValueError(
            "The altitude array has no finite values."
        )

    if glat_all.ndim != 3 or glon_all.ndim != 3:
        raise ValueError(
            "glat and glon must be three-dimensional: "
            f"glat={glat_all.shape}, "
            f"glon={glon_all.shape}"
        )

    if glat_all.shape != glon_all.shape:
        raise ValueError(
            "glat and glon shapes do not match: "
            f"{glat_all.shape} != {glon_all.shape}"
        )

    if glat_all.shape[-1] != altitudes.size:
        raise ValueError(
            "Altitude dimension does not match: "
            f"mapping={glat_all.shape[-1]}, "
            f"altitude={altitudes.size}"
        )

    # =========================================
    # Select nearest mapping altitude
    # =========================================
    alt_index = int(
        np.nanargmin(
            np.abs(altitudes - float(altitude))
        )
    )

    selected_altitude = float(
        altitudes[alt_index]
    )

    glat = glat_all[:, :, alt_index].copy()
    glon = glon_all[:, :, alt_index].copy()

    glat[np.isclose(glat, -999.0)] = np.nan
    glon[np.isclose(glon, -999.0)] = np.nan

    if images.shape[1:] != glat.shape:
        raise ValueError(
            "Image and mapping-table dimensions "
            "do not match: "
            f"image={images.shape[1:]}, "
            f"mapping={glat.shape}"
        )

    # =========================================
    # Get site code
    # =========================================
    name_parts = raw_name.split("_")

    if len(name_parts) < 3:
        raise ValueError(
            f"Wrong tplot variable name: {raw_name}"
        )

    site = name_parts[2]

    # =========================================
    # Determine geographic range
    # =========================================
    center_x = min(127, glat.shape[0] - 1)
    center_y = min(127, glat.shape[1] - 1)

    center_glat = glat[center_x, :]
    center_glon = glon[:, center_y]

    if not np.any(np.isfinite(center_glat)):
        raise ValueError(
            "No finite latitude values were found "
            "on the center line."
        )

    if not np.any(np.isfinite(center_glon)):
        raise ValueError(
            "No finite longitude values were found "
            "on the center line."
        )

    min_glat = float(np.nanmin(center_glat))
    max_glat = float(np.nanmax(center_glat))
    min_glon = float(np.nanmin(center_glon))
    max_glon = float(np.nanmax(center_glon))

    nx = int(
        np.floor(
            (max_glon - min_glon) / grid_x
        )
    )

    ny = int(
        np.floor(
            (max_glat - min_glat) / grid_y
        )
    )

    if nx <= 0 or ny <= 0:
        raise ValueError(
            f"Invalid geographic grid: nx={nx}, ny={ny}"
        )

    x_glon = (
        min_glon
        + grid_x * np.arange(nx, dtype=np.float32)
    )

    y_glat = (
        min_glat
        + grid_y * np.arange(ny, dtype=np.float32)
    )

    n_times = times.size
    n_bins = nx * ny

    image_gmap = np.full(
        (n_times, nx, ny),
        np.nan,
        dtype=np.float32,
    )

    # =========================================
    # Create fixed pixel-grid correspondence
    # =========================================
    flat_glon = glon.ravel(order="F")
    flat_glat = glat.ravel(order="F")
    raw0 = images[0].ravel(order="F")

    coordinate_valid = (
        np.isfinite(flat_glon)
        & np.isfinite(flat_glat)
    )

    ix = np.full(
        flat_glon.shape,
        -1,
        dtype=np.int64,
    )

    iy = np.full(
        flat_glat.shape,
        -1,
        dtype=np.int64,
    )

    ix[coordinate_valid] = np.floor(
        (
            flat_glon[coordinate_valid]
            - min_glon
        )
        / grid_x
    ).astype(np.int64)

    iy[coordinate_valid] = np.floor(
        (
            flat_glat[coordinate_valid]
            - min_glat
        )
        / grid_y
    ).astype(np.int64)

    valid = (
        coordinate_valid
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

    # IDL-style flattened grid number
    bin_number = (
        ix[valid]
        + np.int64(nx) * iy[valid]
    )

    bin_count = np.bincount(
        bin_number,
        minlength=n_bins,
    )

    active_bins = bin_count > 0

    valid_grid = active_bins.reshape(
        (nx, ny),
        order="F",
    )

    # =========================================
    # Grid each time step
    # =========================================
    for i in range(n_times):
        raw = images[i].ravel(order="F")
        raw_valid = raw[valid_pixel_indices]

        bin_sum = np.bincount(
            bin_number,
            weights=raw_valid,
            minlength=n_bins,
        )

        output_flat = np.full(
            n_bins,
            np.nan,
            dtype=np.float32,
        )

        output_flat[active_bins] = (
            bin_sum[active_bins]
            / bin_count[active_bins]
        )

        map_image = output_flat.reshape(
            (nx, ny),
            order="F",
        )

        if fill_empty:
            map_image = fill_empty_cells(
                image=map_image,
                valid_mask=valid_grid,
                max_distance=max_fill_distance,
            )

        image_gmap[i] = map_image

        if i % 10 == 0:
            date = datetime.fromtimestamp(
                float(times[i]),
                tz=timezone.utc,
            )

            print(
                "now converting... : "
                + date.strftime(
                    "%Y-%m-%d/%H:%M:%S.%f"
                )[:-3]
            )

    # =========================================
    # Store output tplot variable
    # =========================================
    output_name = (
        f"{raw_name}_gmap_"
        f"{int(selected_altitude)}"
    )

    source_metadata = pyspedas.get_data(
        raw_name,
        metadata=True,
    )

    if source_metadata is None:
        source_metadata = {}

    output_metadata = dict(source_metadata)

    output_metadata.update(
        {
            "site": site.upper(),
            "mapping_altitude_km": selected_altitude,
            "grid_longitude_degree": grid_x,
            "grid_latitude_degree": grid_y,
            "empty_cells_filled": bool(fill_empty),
            "max_fill_distance_grid_cells": (
                max_fill_distance
            ),
        }
    )

    success = pyspedas.store_data(
        output_name,
        data={
            "x": times,
            "y": image_gmap,
            "v1": x_glon,
            "v2": y_glat,
        },
        attr_dict=output_metadata,
    )

    if not success:
        print(f"Failed to store: {output_name}")
        return None

    print(f"Created tplot variable: {output_name}")

    return output_name
