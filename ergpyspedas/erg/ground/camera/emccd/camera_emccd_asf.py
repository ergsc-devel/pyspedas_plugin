import logging
from typing import Dict, List, Optional, Tuple, Union

import cdflib
import numpy as np
from pyspedas import clip, get_data, store_data

from ....ground.camera.load_emccd import load_emccd
from ....satellite.erg.get_gatt_ror import get_gatt_ror


VALID_SITES = [
    "gak",
    "kev",
    "mag",
    "pok",
    "sod",
    "tja",
    "tro",
]


def camera_emccd_asf(
    trange: Optional[List[str]] = None,
    suffix: str = "",
    site: Union[str, List[str]] = "all",
    get_support_data: bool = False,
    mapping_table: bool = False,
    varformat: Optional[str] = None,
    varnames: Optional[List[str]] = None,
    downloadonly: bool = False,
    notplot: bool = False,
    no_update: bool = False,
    uname: Optional[str] = None,
    passwd: Optional[str] = None,
    time_clip: bool = False,
    ror: bool = True,
    force_download: bool = False,
):
    """
    Load EMCCD ASF data from the ISEE ERG-SC data repository.

    Parameters
    ----------
    trange : list of str, optional
        Time range [start_time, end_time].

    suffix : str
        Suffix added to tplot variable names.

    site : str or list of str
        Observation site or list of sites.
        Available sites are:
        gak, kev, mag, pok, sod, tja and tro.
        Use "all" to load all sites.

    get_support_data : bool
        Load CDF support-data variables.

    mapping_table : bool
        If True, read glat, glon and altitude from the CDF and
        return them as a Python dictionary.

    varformat : str, optional
        Wildcard selecting CDF variables.

    varnames : list of str, optional
        CDF variable names to load.

    downloadonly : bool
        Download CDF files without creating tplot variables.

    notplot : bool
        Return data dictionaries instead of tplot variables.

    no_update : bool
        Use only locally cached files.

    uname, passwd : str, optional
        Authentication information.

    time_clip : bool
        Clip loaded data to the requested time range.

    ror : bool
        Print PI information and Rules of the Road.

    force_download : bool
        Force downloading files.

    Returns
    -------
    list or dict
        If mapping_table=False, returns loaded_data.

    tuple
        If mapping_table=True, returns:

            loaded_data, mapping_table_structure

        The mapping-table dictionary has the form:

            {
                site_code: {
                    "site_code": str,
                    "glat": ndarray,
                    "glon": ndarray,
                    "altitude": ndarray,
                }
            }
    """

    if trange is None:
        trange = [
            "2018-03-15/01:00:00",
            "2018-03-15/01:05:00",
        ]

    if varnames is None:
        varnames = []

    site_codes = _normalize_sites(site)

    if not site_codes:
        logging.error(
            "No valid sites were specified. Valid sites: %s",
            VALID_SITES,
        )

        if mapping_table:
            return [], {}

        return []

    if notplot:
        loaded_data = {}
    else:
        loaded_data = []

    mapping_table_structure = {}

    for site_input in site_codes:
        prefix = f"emccd_asf_{site_input}_"
        file_res = 60.0

        pathformat = (
            f"{site_input}/%Y/%m/%d/"
            f"*_asf_{site_input}_"
            "%Y%m%d%H%M_v??.cdf"
        )

        loaded_data_temp = load_emccd(
            pathformat=pathformat,
            file_res=file_res,
            trange=trange,
            prefix=prefix,
            suffix=suffix,
            get_support_data=get_support_data,
            varformat=varformat,
            varnames=varnames,
            downloadonly=downloadonly,
            notplot=notplot,
            time_clip=time_clip,
            no_update=no_update,
            uname=uname,
            passwd=passwd,
            force_download=force_download,
        )

        if loaded_data_temp is None:
            logging.warning(
                "No data were loaded for site %s.",
                site_input,
            )
            continue

        if notplot:
            if isinstance(loaded_data_temp, dict):
                loaded_data.update(loaded_data_temp)
        else:
            loaded_data.extend(loaded_data_temp)

        if len(loaded_data_temp) > 0 and ror:
            _print_ror(
                downloadonly=downloadonly,
                loaded_data_temp=loaded_data_temp,
                site_input=site_input,
            )

        # No tplot variables exist in these modes.
        if downloadonly or notplot:
            continue

        current_tplot_name = (
            f"{prefix}image_raw{suffix}"
        )

        if current_tplot_name not in loaded_data:
            logging.warning(
                "Image variable was not loaded: %s",
                current_tplot_name,
            )
            continue

        image_data = get_data(current_tplot_name)

        if image_data is None:
            store_data(
                current_tplot_name,
                delete=True,
            )
            continue

        # Replace values outside the valid range with NaN.
        clip(
            current_tplot_name,
            -1.0e6,
            1.0e6,
        )

        # Re-read data after clipping.
        image_data = get_data(current_tplot_name)
        metadata = get_data(
            current_tplot_name,
            metadata=True,
        )

        if image_data is None:
            continue

        # Store clipped image while preserving metadata.
        store_data(
            current_tplot_name,
            data={
                "x": image_data.times,
                "y": image_data.y,
            },
            attr_dict=metadata,
        )

        if mapping_table:
            site_mapping = _read_mapping_table(
                metadata=metadata,
                site_code=site_input,
            )

            if site_mapping is not None:
                mapping_table_structure[
                    site_input
                ] = site_mapping

    if mapping_table:
        return loaded_data, mapping_table_structure

    return loaded_data


def _normalize_sites(
    site: Union[str, List[str]],
) -> List"""
    Normalize and validate the requested site codes.
    """

    if isinstance(site, str):
        requested_sites = site.lower().split()

    elif isinstance(site, list):
        requested_sites = [
            str(item).lower()
            for item in site
        ]

    else:
        raise TypeError(
            "site must be a string or a list of strings."
        )

    if "all" in requested_sites:
        return VALID_SITES.copy()

    # Preserve input order while removing duplicates.
    normalized_sites = []

    for site_code in requested_sites:
        if (
            site_code in VALID_SITES
            and site_code not in normalized_sites
        ):
            normalized_sites.append(site_code)

    invalid_sites = [
        value
        for value in requested_sites
        if value not in VALID_SITES
    ]

    if invalid_sites:
        logging.warning(
            "Ignoring invalid site codes: %s",
            invalid_sites,
        )

    return normalized_sites


def _get_cdf_filename(
    metadata: Optional[dict],
) -> Optional"""
    Extract one CDF filename from tplot metadata.
    """

    if not metadata:
        return None

    cdf_metadata = metadata.get("CDF", {})

    filename = cdf_metadata.get("FILENAME")

    if filename is None:
        return None

    if isinstance(filename, (list, tuple, np.ndarray)):
        if len(filename) == 0:
            return None

        filename = filename[0]

    return str(filename)


def _read_mapping_table(
    metadata: Optional[dict],
    site_code: str,
) -> Optional[Dict[str, object]]:
    """
    Read glat, glon and altitude from the source CDF file.
    """

    filename = _get_cdf_filename(metadata)

    if filename is None:
        logging.warning(
            "CDF filename was not found for site %s.",
            site_code,
        )
        return None

    try:
        cdf_file = cdflib.CDF(filename)

    except Exception as error:
        logging.warning(
            "Could not open CDF file %s: %s",
            filename,
            error,
        )
        return None

    try:
        glat = np.asarray(
            cdf_file.varget("glat"),
            dtype=np.float32,
        ).copy()

        glon = np.asarray(
            cdf_file.varget("glon"),
            dtype=np.float32,
        ).copy()

        altitude = np.asarray(
            cdf_file.varget("altitude"),
            dtype=np.float32,
        ).copy()

    except Exception as error:
        logging.warning(
            "Could not read the mapping table "
            "from %s: %s",
            filename,
            error,
        )
        return None

    finally:
        cdf_file.close()

    # Convert mapped-coordinate fill values to NaN.
    glat[np.isclose(glat, -999.0)] = np.nan
    glon[np.isclose(glon, -999.0)] = np.nan

    mapping_data = {
        "site_code": site_code,
        "glat": glat,
        "glon": glon,
        "altitude": altitude,
    }

    logging.info(
        "Mapping table for %s: "
        "glat=%s, glon=%s, altitude=%s",
        site_code,
        glat.shape,
        glon.shape,
        altitude.shape,
    )

    return mapping_data


def _print_ror(
    downloadonly: bool,
    loaded_data_temp,
    site_input: str,
) -> None:
    """
    Print PI information and Rules of the Road.
    """

    try:
        gatt = get_gatt_ror(
            downloadonly,
            loaded_data_temp,
        )

        print("*" * 78)
        print(
            gatt.get(
                "Logical_source_description",
                "",
            )
        )
        print()
        print(
            "Information about "
            f"{gatt.get('Station_code', site_input)}"
        )
        print(
            f"PI: {gatt.get('PI_name', '')}"
        )
        print()
        print(
            "Affiliations: "
            f"{gatt.get('PI_affiliation', '')}"
        )
        print()
        print(
            "Rules of the Road for "
            "EMCCD ASF Data Use:"
        )

        rules = gatt.get("TEXT", [])

        if isinstance(rules, str):
            rules = [rules]

        for text in rules:
            print(text)

        print(gatt.get("LINK_TEXT", ""))
        print("*" * 78)

    except Exception as error:
        logging.warning(
            "Printing PI information and Rules "
            "of the Road failed for %s: %s",
            site_input,
            error,
        )
