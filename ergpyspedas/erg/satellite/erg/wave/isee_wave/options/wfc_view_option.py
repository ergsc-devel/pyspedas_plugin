from dataclasses import dataclass


@dataclass
class WFCViewOption:
    xsize: int = 800  # px
    ysize: int = 900  # px
    font_size: float = 9.0  # pt


@dataclass
class WFCViewOptionOther:
    """Hold WFC view option that is will not be saved as .json file."""

    mask_threshold_digit_linear: int = 2
    mask_threshold_digit_log: int = 0
