import math
from typing import Optional


def str_to_float_or_none(x: str) -> Optional[float]:
    try:
        return float(x)
    except ValueError:
        return None


def str_to_int_or_none(x: str) -> Optional[int]:
    maybe_float = str_to_float_or_none(x)
    if maybe_float is None:
        return None
    else:
        return int(maybe_float)


def round_toward_inf(x: float) -> int:
    """
    >>> round_toward_inf(1.2)
    2
    >>> round_toward_inf(-1.2)
    -2
    """
    return int(math.copysign(math.ceil(abs(x)), x))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
