import math
from typing import Optional, Tuple, Union

# Define small positive number
# epsilon = sys.float_info.epsilon # = 2.220446049250313e-16 in some machine
epsilon = 1e-16  # For more simple view


def str_to_float_or_none(x: str) -> Optional[float]:
    """
    >>> str_to_float_or_none("0.1")
    0.1
    >>> str_to_float_or_none("1")
    1.0
    >>> str_to_float_or_none("1e-1")
    0.1
    >>> str_to_float_or_none("1/10")
    """
    try:
        return float(x)
    except ValueError:
        return None


def str_to_int_or_none(x: str) -> Optional[int]:
    """
    >>> str_to_int_or_none("0.1")
    0
    >>> str_to_int_or_none("1")
    1
    >>> str_to_int_or_none("1e-1")
    0
    >>> str_to_int_or_none("1/10")
    >>>
    """
    maybe_float = str_to_float_or_none(x)
    if maybe_float is None:
        return None
    else:
        return int(maybe_float)


def round_down(x: float, ndigits: Optional[int] = None) -> float:
    """
    >>> round_down(1.2)
    1
    >>> round_down(-1.2)
    -2
    >>> round_down(1.25, 1)
    1.2
    >>> round_down(-1.25, 1)
    -1.3
    """
    if ndigits is None:
        return math.floor(x)
    factor = 10**ndigits
    return math.floor(x * factor) / factor


def round_up(x: float, ndigits: Optional[int] = None) -> float:
    """
    >>> round_up(1.2)
    2
    >>> round_up(-1.2)
    -1
    >>> round_up(1.25, 1)
    1.3
    >>> round_up(-1.25, 1)
    -1.2
    """
    if ndigits is None:
        return math.ceil(x)
    factor = 10**ndigits
    return math.ceil(x * factor) / factor


_white_char_list = "0123456789+-*/%.()eE"


def check_safe_string(string: str) -> bool:
    """
    >>> check_safe_string("0.1")
    True
    >>> check_safe_string("1e-1")
    True
    >>> check_safe_string("1/10")
    True
    >>> check_safe_string("e")
    True
    >>> check_safe_string("print()")
    False
    """
    if type(string) != str:
        return False
    for char in string:
        if char not in _white_char_list:
            return False
    return True


def safe_eval_formula(string: str) -> Optional[float]:
    """
    >>> safe_eval_formula("0.1")
    0.1
    >>> safe_eval_formula("1e-1")
    0.1
    >>> safe_eval_formula("1/10")
    0.1
    >>> safe_eval_formula("e")
    >>> safe_eval_formula("print()")
    """
    is_safe = check_safe_string(string)
    if not is_safe:
        return None
    try:
        res = eval(string)
    except:
        return None
    if not isinstance(res, int) and not isinstance(res, float):
        return None
    return float(res)


def line_style_idl_to_mpl(value: Union[int, str]) -> Tuple[int, Tuple[int, ...]]:
    """
    Return values are (offset, (x1 pt line, x2 pt space, ...))
    Values are based and modified from pytplot/options/options
    """
    if value == 0 or value == "solid_line" or value == "-":
        return (0, (1, 0))
    elif value == 1 or value == "dot" or value == ":":
        return (0, (2, 4))
    elif value == 2 or value == "dash" or value == "--":
        return (0, (6, 3))
    elif value == 3 or value == "dash_dot" or value == "-.":
        return (0, (6, 4, 2, 4))
    elif value == 4 or value == "dash_dot_dot_dot" or value == "-:":
        return (0, (6, 4, 2, 4, 2, 4, 2, 4))
    elif value == 5 or value == "long_dash" or value == "__":
        return (0, (10, 5))
    elif value == 6 or value == "none" or value == "":
        return (0, (0, 1))
    else:
        raise ValueError("Invalid line style value")


def choose_black_or_white_for_high_contrast(
    color: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    r, g, b = color

    def choose_each_color_value_for_high_contrast(x):
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4

    rr = choose_each_color_value_for_high_contrast(r)
    gg = choose_each_color_value_for_high_contrast(g)
    bb = choose_each_color_value_for_high_contrast(b)
    Lbg = 0.2126 * rr + 0.7152 * gg + 0.0722 * bb
    Lw = 1.0
    Lb = 0.0
    Cw = (Lw + 0.05) / (Lbg + 0.05)
    Cb = (Lbg + 0.05) / (Lb + 0.05)
    output_color = (0, 0, 0) if Cw < Cb else (1, 1, 1)
    return output_color


if __name__ == "__main__":
    import doctest

    doctest.testmod()
