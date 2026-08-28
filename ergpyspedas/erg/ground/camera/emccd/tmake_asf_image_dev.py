import numpy as np
import pyspedas


def tmake_asf_image_dev(vname, width=30.0):
    """
    Calculate normalized deviations from a moving-average image.

    Parameters
    ----------
    vname : str
        Input image tplot variable.
        Expected shape is (time, image_x, image_y).

    width : float, optional
        Full width of the moving time window [s].
        Default is 30 seconds.

    Returns
    -------
    str or None
        Created tplot variable name.
    """

    # ======================================
    # Check input variable
    # ======================================
    matched_names = pyspedas.tnames(vname)

    if len(matched_names) == 0:
        print(f"Cannot find the tplot variable: {vname}")
        return None

    resolved_name = matched_names[0]

    # ======================================
    # Get tplot data
    # ======================================
    raw_data = pyspedas.get_data(resolved_name)

    if raw_data is None:
        print(f"Cannot retrieve data from: {resolved_name}")
        return None

    times = np.asarray(raw_data[0], dtype=np.float64)
    images = np.asarray(raw_data[1], dtype=np.float32)

    if images.ndim != 3:
        raise ValueError(
            "Input data must have shape "
            "(time, image_x, image_y); "
            f"current shape={images.shape}"
        )

    if images.shape[0] != times.size:
        raise ValueError(
            "Time and image dimensions do not match: "
            f"time={times.size}, images={images.shape[0]}"
        )

    if width <= 0:
        raise ValueError("width must be greater than zero.")

    # Check chronological order
    if times.size > 1 and np.any(np.diff(times) < 0):
        raise ValueError(
            "Input times must be sorted in ascending order."
        )

    n_times, nx, ny = images.shape
    half_width = float(width) / 2.0

    dev = np.zeros_like(images, dtype=np.float32)

    # Sliding-window state
    left = 0
    right = 0

    # float64 reduces accumulated rounding errors
    sum_image = np.zeros((nx, ny), dtype=np.float64)

    # ======================================
    # Sliding-window calculation
    # ======================================
    for i in range(n_times):

        t_min = times[i] - half_width
        t_max = times[i] + half_width

        # Add frames satisfying time <= t_max
        while right < n_times and times[right] <= t_max:
            sum_image += images[right]
            right += 1

        # Remove frames satisfying time < t_min
        while left < right and times[left] < t_min:
            sum_image -= images[left]
            left += 1

        n_window = right - left

        if n_window == 0:
            continue

        average_image = sum_image / float(n_window)

        # IDLコードと同様、平均が0の画素では分母を1にする
        denominator = average_image.copy()
        denominator[denominator == 0.0] = 1.0

        normalized_deviation = (
            images[i].astype(np.float64) - average_image
        ) / denominator

        # Remove spatial mean, equivalent to mean(..., /NAN)
        spatial_mean = np.nanmean(normalized_deviation)
        normalized_deviation -= spatial_mean

        dev[i] = normalized_deviation.astype(np.float32)

    # ======================================
    # Store output tplot variable
    # ======================================
    output_name = f"{resolved_name}_dev"

    success = pyspedas.store_data(
        output_name,
        data={
            "x": times,
            "y": dev,
        },
        attr_dict={
            "source_variable": resolved_name,
            "average_window_seconds": float(width),
            "description": (
                "Normalized deviation from moving-average image "
                "with spatial mean removed"
            ),
        },
    )

    if not success:
        print(f"Failed to store: {output_name}")
        return None

    print(f"Created tplot variable: {output_name}")

    return output_name