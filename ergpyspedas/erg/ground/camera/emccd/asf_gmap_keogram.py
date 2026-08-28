import numpy as np
import pyspedas


def asf_gmap_keogram(
    vname,
    lat=60.0,
    lon=20.0,
    pixel=0,
):
    """
    Create longitude-time and latitude-time keograms.

    Parameters
    ----------
    vname : str
        Geographic-map image tplot variable.
        Expected shape: (time, longitude, latitude)

    lat : float, optional
        Latitude used for the longitude-time keogram.

    lon : float, optional
        Longitude used for the latitude-time keogram.

    pixel : int, optional
        Half-width used for spatial smoothing.

    Returns
    -------
    tuple[str, str] or None
        Latitude-slice and longitude-slice tplot variable names.
    """

    # =========================================
    # Check arguments
    # =========================================
    matched_names = pyspedas.tnames(vname)

    if len(matched_names) == 0:
        print(f"Cannot find the tplot variable: {vname}")
        return None

    resolved_name = matched_names[0]
    name_parts = resolved_name.split("_")

    if len(name_parts) < 7:
        print(f"Wrong tplot variable name: {resolved_name}")
        return None

    pixel = int(pixel)

    if pixel < 0:
        raise ValueError("pixel must be zero or greater.")

    site = name_parts[2]
    level = name_parts[4]
    altitude = name_parts[-1]

    # =========================================
    # Get tplot data
    # =========================================
    raw_data = pyspedas.get_data(resolved_name)

    if raw_data is None:
        print(f"Cannot retrieve data from: {resolved_name}")
        return None

    times = np.asarray(raw_data[0])
    image_data = np.asarray(raw_data[1], dtype=float)

    if image_data.ndim != 3:
        raise ValueError(
            "Input data must have shape "
            "(time, longitude, latitude); "
            f"current shape={image_data.shape}"
        )

    # get_data() returns v1 and v2 after time and data
    if len(raw_data) < 4:
        raise ValueError(
            "Longitude and latitude coordinates were not found. "
            "Store the source variable using v1 and v2."
        )

    glon = np.asarray(raw_data[2], dtype=float).squeeze()
    glat = np.asarray(raw_data[3], dtype=float).squeeze()

    if glon.ndim != 1 or glat.ndim != 1:
        raise ValueError(
            "glon and glat must be one-dimensional arrays."
        )

    if image_data.shape[1:] != (glon.size, glat.size):
        raise ValueError(
            "Coordinate dimensions do not match image data: "
            f"image={image_data.shape[1:]}, "
            f"glon={glon.size}, glat={glat.size}"
        )

    # =========================================
    # Find nearest coordinates
    # =========================================
    if not np.any(np.isfinite(glon)):
        raise ValueError("glon contains no finite coordinates.")

    if not np.any(np.isfinite(glat)):
        raise ValueError("glat contains no finite coordinates.")

    idx_lon = int(np.nanargmin(np.abs(glon - float(lon))))
    idx_lat = int(np.nanargmin(np.abs(glat - float(lat))))

    selected_lon = float(glon[idx_lon])
    selected_lat = float(glat[idx_lat])

    # =========================================
    # Create keograms
    # =========================================
    if pixel == 0:
        # Fixed latitude: longitude-time plot
        keogram_lon_time = image_data[:, :, idx_lat]

        # Fixed longitude: latitude-time plot
        keogram_lat_time = image_data[:, idx_lon, :]

    else:
        lat_start = max(0, idx_lat - pixel)
        lat_end = min(glat.size, idx_lat + pixel + 1)

        lon_start = max(0, idx_lon - pixel)
        lon_end = min(glon.size, idx_lon + pixel + 1)

        # Average around the selected latitude
        with np.errstate(invalid="ignore"):
            keogram_lon_time = np.nanmean(
                image_data[:, :, lat_start:lat_end],
                axis=2,
            )

        # Average around the selected longitude
        with np.errstate(invalid="ignore"):
            keogram_lat_time = np.nanmean(
                image_data[:, lon_start:lon_end, :],
                axis=1,
            )

    # =========================================
    # Titles
    # =========================================
    ytitle_lat = (
        f"Station: {site.upper()}\n"
        f"Slice GLON: {selected_lon:.1f} [deg]\n"
        "GLAT [deg]"
    )

    ytitle_lon = (
        f"Station: {site.upper()}\n"
        f"Slice GLAT: {selected_lat:.1f} [deg]\n"
        "GLON [deg]"
    )

    if "dev" in name_parts:
        ztitle = "Normalized deviation"
    elif level == "abs":
        ztitle = "Intensity [R]"
    elif level == "raw":
        ztitle = "Count"
    else:
        ztitle = ""

    lon_text = f"{int(lon)}"
    lat_text = f"{int(lat)}"

    lon_output_name = (
        f"{resolved_name}_keogram_lon_{lon_text}"
    )

    lat_output_name = (
        f"{resolved_name}_keogram_lat_{lat_text}"
    )

    # =========================================
    # Fixed longitude: latitude-time keogram
    # =========================================
    pyspedas.store_data(
        lon_output_name,
        data={
            "x": times,
            "y": keogram_lat_time,
            "v": glat,
        },
        attr_dict={
            "site": site.upper(),
            "mapping_altitude_km": altitude,
            "requested_longitude": float(lon),
            "selected_longitude": selected_lon,
        },
    )

    pyspedas.options(
        lon_output_name,
        opt_dict={
            "ytitle": ytitle_lat,
            "ztitle": ztitle,
            "spec": True,
        },
    )

    # =========================================
    # Fixed latitude: longitude-time keogram
    # =========================================
    pyspedas.store_data(
        lat_output_name,
        data={
            "x": times,
            "y": keogram_lon_time,
            "v": glon,
        },
        attr_dict={
            "site": site.upper(),
            "mapping_altitude_km": altitude,
            "requested_latitude": float(lat),
            "selected_latitude": selected_lat,
        },
    )

    pyspedas.options(
        lat_output_name,
        opt_dict={
            "ytitle": ytitle_lon,
            "ztitle": ztitle,
            "spec": True,
        },
    )

    print(
        f"Selected coordinate: "
        f"GLON={selected_lon:.3f}, GLAT={selected_lat:.3f}"
    )

    return lon_output_name, lat_output_name