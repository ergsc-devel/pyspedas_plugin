from collections import UserList
from typing import Dict, List, Optional

from ..utils.utils import safe_eval_formula

# Default options
_support_line_option_list = [
    {
        "species": "fc",
        "m": "1/1837",
        "q": "1",
        "lsty": "0",
        "lcol": "5",
        "enable": "OFF",
    },
    {
        "species": "0.5fc",
        "m": "2/1837",
        "q": "1",
        "lsty": "0",
        "lcol": "1",
        "enable": "OFF",
    },
    {
        "species": "0.1fc",
        "m": "10/1837",
        "q": "1",
        "lsty": "0",
        "lcol": "3",
        "enable": "OFF",
    },
    {
        "species": "fcH",
        "m": "1",
        "q": "1",
        "lsty": "0",
        "lcol": "255",
        "enable": "OFF",
    },
    {
        "species": "fcHe",
        "m": "4",
        "q": "1",
        "lsty": "0",
        "lcol": "255",
        "enable": "OFF",
    },
    {
        "species": "fcO",
        "m": "16",
        "q": "1",
        "lsty": "0",
        "lcol": "255",
        "enable": "OFF",
    },
]


class SupportLineOption:
    props = ("species", "m", "q", "lsty", "lcol", "enable")

    def __init__(
        self, species: str, m: str, q: str, lsty: str, lcol: str, enable: str
    ) -> None:
        """Support line option.

        Each option is saved as string to hold input string as it is.
        Getter SupportLineOption.<option> will return string,
        and getter SupportLineOption.<option>_typed will return
        option with desired type.
        """
        self.species = species
        self.m = m
        self.q = q
        self.lsty = lsty
        self.lcol = lcol
        self.enable = enable

    @property
    def species(self) -> str:
        return self._species

    @species.setter
    def species(self, value: str) -> None:
        self._species = value

    @property
    def species_typed(self) -> str:
        return str(self._species)

    @property
    def m(self) -> str:
        return self._m

    @m.setter
    def m(self, value: str) -> None:
        ret = safe_eval_formula(value)
        if ret is None:
            raise ValueError(f"Cannot evaluate m as formula: {value}")
        self._m = value

    @property
    def m_typed(self) -> float:
        ret = safe_eval_formula(self.m)
        assert ret is not None
        return ret

    @property
    def q(self) -> str:
        return self._q

    @q.setter
    def q(self, value: str) -> None:
        ret = safe_eval_formula(value)
        if ret is None:
            raise ValueError(f"Cannot evaluate q as formula: {value}")
        self._q = value

    @property
    def q_typed(self) -> float:
        ret = safe_eval_formula(self.q)
        assert ret is not None
        return ret

    @property
    def lsty(self) -> str:
        return self._lsty

    @lsty.setter
    def lsty(self, value: str) -> None:
        _ = int(value)
        self._lsty = value

    @property
    def lsty_typed(self) -> float:
        ret = int(self.lsty)
        return ret

    @property
    def lcol(self) -> str:
        return self._lcol

    @lcol.setter
    def lcol(self, value: str) -> None:
        _ = int(value)
        self._lcol = value

    @property
    def lcol_typed(self) -> float:
        ret = int(self.lcol)
        return ret

    @property
    def enable(self) -> str:
        return self._enable

    @enable.setter
    def enable(self, value: str) -> None:
        if value not in ["ON", "OFF"]:
            raise ValueError(f'enable must be "ON" or "OFF" but is {self.enable}')
        self._enable = value

    @property
    def enable_typed(self) -> bool:
        if self.enable == "ON":
            return True
        else:
            return False

    def to_dict(self) -> Dict[str, str]:
        return {key: getattr(self, key) for key in self.props}


# Used to get type hint during development
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Need to be place after definition of SupportLineOption
    _SupportLineOptionsBase = UserList[SupportLineOption]
else:
    _SupportLineOptionsBase = UserList


class SupportLineOptions(_SupportLineOptionsBase):
    """Group SupportLineOption for different species."""

    @classmethod
    def from_list_of_dict(
        cls, list_of_dict: Optional[List[Dict[str, str]]] = None
    ) -> "SupportLineOptions":
        if list_of_dict is None:
            list_of_dict = _support_line_option_list
        return cls([SupportLineOption(**d) for d in list_of_dict])

    def to_list_of_dict(self) -> List[Dict[str, str]]:
        return [opt.to_dict() for opt in self]


if __name__ == "__main__":
    support_line_options = SupportLineOptions.from_list_of_dict(
        _support_line_option_list
    )
    assert all(
        [
            d1 == d2
            for d1, d2 in zip(
                _support_line_option_list, support_line_options.to_list_of_dict()
            )
        ]
    )
