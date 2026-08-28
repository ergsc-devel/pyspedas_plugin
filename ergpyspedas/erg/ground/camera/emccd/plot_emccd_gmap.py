import numpy as np
import matplotlib.pyplot as plt
import pyspedas


def plot_emccd_gmap(
    vname,
    time=None,
    x_min=None,
    x_max=None,
    y_min=None,
    y_max=None,
    z_min=None,
    z_max=None,
    cmap="viridis",
    show=True,
):
    """
    Plot a geographic image at the time nearest to the requested time.

    Parameters
    ----------
    vname : str
        Geographic-map tplot variable.
        Expected shape: (time, longitude, latitude)

    time : str or float, optional
        Plot time. A string is converted with time_double().
        If omitted, the first data time is used.

    x_min, x_max : float, optional
        Longitude plot range [degree].

    y_min, y_max : float, optional
        Latitude plot range [degree].

    z_min, z_max : float, optional
        Color scale range.

    cmap : str, optional
        Matplotlib colormap.

    show : bool, optional
        Display the figure when True.

    Returns
    -------
    tuple or None
        (figure, axes, selected_time_index)
    """

    # ======================================
    # Check tplot variable
    # ======================================
    names = pyspedas.tnames(vname)

    if len(names) == 0:
        print(f"Cannot find the tplot variable: {vname}")
        return None

    resolved_name = names[0]
    name_parts = resolved_name.split("_")

    if len(name_parts) < 7:
        print(f"Wrong tplot variable name: {resolved_name}")
        return None

    site = name_parts[2]
    level = name_parts[4]
    altitude = name_parts[-1]

    # ======================================
    # Get tplot data
    # ======================================
    raw_data = pyspedas.get_data(resolved_name)

    if raw_data is None:
        print(f"Cannot retrieve data from: {resolved_name}")
        return None

    times = np.asarray(raw_data[0], dtype=np.float64)
    image_data = np.asarray(raw_data[1], dtype=np.float64)

    if image_data.ndim != 3:
        raise ValueError(
            "Input must have shape (time, longitude, latitude); "
            f"current shape={image_data.shape}"
        )

    if times.size == 0:
        raise ValueError("The tplot variable contains no time data.")

    # tasf2gmap() stores GLON and GLAT as v1 and v2
    if len(raw_data) < 4:
        raise ValueError(
            "GLON and GLAT coordinates were not found. "
            "Store them as v1 and v2."
        )

    glon = np.asarray(raw_data[2], dtype=np.float64).squeeze()
    glat = np.asarray(raw_data[3], dtype=np.float64).squeeze()

    if glon.ndim != 1 or glat.ndim != 1:
        raise ValueError("GLON and GLAT must be one-dimensional.")

    if image_data.shape[1:] != (glon.size, glat.size):
        raise ValueError(
            "Image and coordinate dimensions do not match: "
            f"image={image_data.shape[1:]}, "
            f"GLON={glon.size}, GLAT={glat.size}"
        )

    # ======================================
    # Find nearest time
    # ======================================
    if time is None:
        requested_time = times[0]
    elif isinstance(time, str):
        requested_time = float(pyspedas.time_double(time))
    else:
        requested_time = float(time)

    time_index = int(
        np.nanargmin(np.abs(times - requested_time))
    )

    selected_time = times[time_index]
    image = image_data[time_index]

    # ======================================
    # Plot ranges
    # ======================================
    if x_min is None:
        x_min = float(np.nanmin(glon))

    if x_max is None:
        x_max = float(np.nanmax(glon))

    if y_min is None:
        y_min = float(np.nanmin(glat))

    if y_max is None:
        y_max = float(np.nanmax(glat))

    if z_min is None:
        z_min = 0.0

    if z_max is None:
        z_max = float(np.nanmax(image))

    if not z_min < z_max:
        raise ValueError(
            f"z_min must be smaller than z_max: "
            f"z_min={z_min}, z_max={z_max}"
        )

    # ======================================
    # Colorbar title
    # ======================================
    if "dev" in name_parts:
        ztitle = "Normalized deviation"
    elif level == "abs":
        ztitle = "Intensity [R]"
    elif level == "raw":
        ztitle = "Count"
    else:
        ztitle = ""

    # ======================================
    # Plot geographic image
    # ======================================
    fig, ax = plt.subplots(figsize=(8, 7))

    # image shape is (longitude, latitude), while
    # pcolormesh expects (latitude, longitude).
    mesh = ax.pcolormesh(
        glon,
        glat,
        image.T,
        shading="auto",
        cmap=cmap,
        vmin=z_min,
        vmax=z_max,
    )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_xlabel("GLON [deg]")
    ax.set_ylabel("GLAT [deg]")

    colorbar = fig.colorbar(mesh, ax=ax)

    if ztitle:
        colorbar.set_label(ztitle)

    # PySPEDAS time_string supports formatting Unix times. 【2-076bef】
    selected_time_string = pyspedas.time_string(
        selected_time,
        fmt="%Y-%m-%d/%H:%M:%S.%f",
    )

    # Milliseconds
    selected_time_string = selected_time_string[:-3]

    fig.suptitle(
        f"Station: {site.upper()}\n"
        f"Mapping altitude: {altitude} [km]\n"
        f"{selected_time_string}",
        fontsize=12,
    )

    fig.tight_layout()

    if show:
        plt.show()

    return fig, ax, time_index