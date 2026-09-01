import numpy as np
import pyspedas


def asf_keogram(vname, pixel_x=127, pixel_y=127, pixel=0):
    """
    Create vertical and horizontal keograms from an image tplot variable.

    Parameters
    ----------
    vname : str
        Name of an image-data tplot variable.
        The data shape must be:
            (time, pixel_x, pixel_y)

    pixel_x : int, optional
        Pixel position for the vertical slice. Default is 127.

    pixel_y : int, optional
        Pixel position for the horizontal slice. Default is 127.

    pixel : int, optional
        Half-width used for pixel smoothing.
        For example, pixel=2 averages over five pixels.
        Default is 0.

    Returns
    -------
    tuple[str, str] or None
        Names of the vertical and horizontal keogram variables.
    """

    # ----------------------------------------
    # Check arguments
    # ----------------------------------------
    matched_names = pyspedas.tnames(vname)

    if len(matched_names) == 0:
        print(f"Cannot find the tplot variable: {vname}")
        return None

    # Use the first exact/wildcard match
    resolved_vname = matched_names[0]

    name_parts = resolved_vname.split("_")

    # The IDL code references `strtnames[4]`, so a minimum of 5 elements is required.
    if len(name_parts) < 5:
        print(f"Wrong tplot variable name: {resolved_vname}")
        return None

    site = name_parts[2]
    level = name_parts[4]

    pixel_x = int(pixel_x)
    pixel_y = int(pixel_y)
    pixel = int(pixel)

    if pixel < 0:
        raise ValueError("pixel must be zero or greater.")

    # ----------------------------------------
    # Get data from the tplot variable
    # ----------------------------------------
    tplot_data = pyspedas.get_data(resolved_vname)

    if tplot_data is None:
        print(f"Cannot get data from: {resolved_vname}")
        return None

    times = np.asarray(tplot_data[0])
    image_data = np.asarray(tplot_data[1], dtype=float)

    if image_data.ndim != 3:
        raise ValueError(
            f"{resolved_vname} must be a 3-D array "
            f"(time, pixel_x, pixel_y); shape={image_data.shape}"
        )

    nt, nx, ny = image_data.shape

    if len(times) != nt:
        raise ValueError(
            f"Time length ({len(times)}) does not match "
            f"the first data dimension ({nt})."
        )

    if not 0 <= pixel_x < nx:
        raise IndexError(
            f"pixel_x={pixel_x} is outside the valid range 0-{nx - 1}."
        )

    if not 0 <= pixel_y < ny:
        raise IndexError(
            f"pixel_y={pixel_y} is outside the valid range 0-{ny - 1}."
        )

    # ----------------------------------------
    # Make keograms
    # ----------------------------------------
    if pixel == 0:
        # Fixed pixel_x, retain the pixel_y dimension
        keogram_vertical = image_data[:, pixel_x, :]

        # Fixed pixel_y, retain the pixel_x dimension
        keogram_horizontal = image_data[:, :, pixel_y]

    else:
        x_start = max(0, pixel_x - pixel)
        x_end = min(nx, pixel_x + pixel + 1)

        y_start = max(0, pixel_y - pixel)
        y_end = min(ny, pixel_y + pixel + 1)

        # Average around pixel_x
        with np.errstate(invalid="ignore"):
            keogram_vertical = np.nanmean(
                image_data[:, x_start:x_end, :],
                axis=1
            )

        # Average around pixel_y
        with np.errstate(invalid="ignore"):
            keogram_horizontal = np.nanmean(
                image_data[:, :, y_start:y_end],
                axis=2
            )

    vertical_pixels = np.arange(ny, dtype=float)
    horizontal_pixels = np.arange(nx, dtype=float)

    # ----------------------------------------
    # Titles
    # ----------------------------------------
    ytitle_vertical = (
        f"Station: {site.upper()}\n"
        f"Vertical slice pixel: {pixel_x}\n"
        "[pixel]"
    )

    ytitle_horizontal = (
        f"Station: {site.upper()}\n"
        f"Horizontal slice pixel: {pixel_y}\n"
        "[pixel]"
    )

    if level == "raw":
        ztitle = "Count"
    elif len(name_parts) >= 6:
        ztitle = "Normalized deviation"
    else:
        ztitle = ""

    vertical_name = (
        f"{resolved_vname}_keogram_vertical_{pixel_x}"
    )
    horizontal_name = (
        f"{resolved_vname}_keogram_horizontal_{pixel_y}"
    )

    # ----------------------------------------
    # Store vertical keogram
    # ----------------------------------------
    pyspedas.store_data(
        vertical_name,
        data={
            "x": times,
            "y": keogram_vertical,
            "v": vertical_pixels
        }
    )

    pyspedas.options(
        vertical_name,
        opt_dict={
            "ytitle": ytitle_vertical,
            "ztitle": ztitle,
            "spec": True
        }
    )

    pyspedas.ylim(vertical_name, 0, ny - 1)

    # ----------------------------------------
    # Store horizontal keogram
    # ----------------------------------------
    pyspedas.store_data(
        horizontal_name,
        data={
            "x": times,
            "y": keogram_horizontal,
            "v": horizontal_pixels
        }
    )

    pyspedas.options(
        horizontal_name,
        opt_dict={
            "ytitle": ytitle_horizontal,
            "ztitle": ztitle,
            "spec": True
        }
    )

    pyspedas.ylim(horizontal_name, 0, nx - 1)

    return vertical_name, horizontal_name
