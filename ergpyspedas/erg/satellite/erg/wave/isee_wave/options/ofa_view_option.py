from dataclasses import dataclass


@dataclass
class OFAViewOption:
    xsize: int = 1280  # px
    ysize: int = 600  # px
    font_size: float = 9.0  # pt
