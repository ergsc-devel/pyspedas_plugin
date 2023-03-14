from collections import UserDict
from typing import List, Tuple

import numpy as np
import pytplot
from pytplot import get_data

from ..options.data_option import DataName, DataOption, DataOptions
from ..utils.utils import epsilon, round_down, round_up


def _get_min_max(z: np.ndarray, zlog: bool) -> Tuple[float, float]:
    """Get min and max of array.

    If zlog is True, only value > 0 in the array will be target.
    Returned min and max can be same, and they can be NaNs.

    Parameters
    ----------
    z : np.ndarray
        Input array
    zlog : bool
        Whether to consider in log space

    Returns
    -------
    Tuple[float, float]
        Min and max of array

    Examples
    --------
    >>> _get_min_max(np.array([1, 2]), False)
    (1.0, 2.0)
    >>> _get_min_max(np.array([1, -2]), False)
    (-2.0, 1.0)
    >>> _get_min_max(np.array([1, -2]), True)
    (1.0, 1.0)
    >>> _get_min_max(np.array([-1, -2]), True)
    (nan, nan)
    """
    z_real = z.real.astype(float)
    if zlog:
        z_pos = z_real[z_real > 0]
        if len(z_pos) == 0:
            return float("nan"), float("nan")
        else:
            return z_pos.min(), z_pos.max()
    else:
        return z_real.min(), z_real.max()


def _get_mask(z: np.ndarray, threshold: float, zlog: bool) -> np.ndarray:
    """Get mask of array.

    Trues in the mask are generally value equal to or below threshold.

    Parameters
    ----------
    z : np.ndarray
        Input array.
    threshold : float
        Threshold
    zlog : bool
        Whether to consider in log space

    Returns
    -------
    np.ndarray
        Mask

    Examples
    --------
    >>> _get_mask(np.array([1, 2]), 1, False)
    array([ True, False])
    >>> _get_mask(np.array([1, 2]), 1, True)
    array([ True, False])
    >>> _get_mask(np.array([1, -2]), 1, True)
    array([ True, False])
    >>> _get_mask(np.array([1, -2]), -2, True)
    array([False, False])
    """
    # Convert to float so that you can insert NaNs
    z_real = z.real.astype(float)
    if zlog:
        z_pos = z_real.copy()
        # Non-positives are always False in mask even if threshold <= 0
        # if np.count_nonzero(z_real <= 0) > 0:
        z_pos[z_real <= 0] = float("nan")
        # NaNs are evaluated as False and thus not in mask
        # Threshold value is in mask
        return z_pos <= threshold
    else:
        # NaNs are evaluated as False and thus not in mask
        # Threshold value is in mask
        return z_real <= threshold


def _apply_mask(
    tplot_names: List[str],
    thresholds: List[float],
    zlogs: List[bool],
    masks: List[bool],
) -> None:
    assert len(tplot_names) == len(thresholds) == len(zlogs) == len(masks)
    # Total mask is logical sum of mask of each variable
    # Make mask
    mask = None
    for tplot_name, threshold, zlog in zip(tplot_names, thresholds, zlogs):
        data = get_data(tplot_name)
        assert data is not None
        if mask is None:
            mask = _get_mask(data.y, threshold, zlog)
        else:
            mask = mask | _get_mask(data.y, threshold, zlog)
    assert mask is not None
    # Apply mask
    for tplot_name, apply_mask in zip(tplot_names, masks):
        tplot_name_for_mask = tplot_name + "_mask"
        data = get_data(tplot_name)
        assert data is not None
        # Some complex data will be converted to real
        # Convert to float so that you can insert NaNs
        y = data.y.real.astype(float).copy()
        if apply_mask:
            y[mask] = float("nan")
        # Replace masked data
        pytplot.data_quants[tplot_name_for_mask].values = y


class MaskManager:
    def __init__(
        self,
        data: np.ndarray,
        data_option: DataOption,
        linear_ndigits: int = 2,
        log_ndigits: int = 0,
    ) -> None:
        """Manage mask get / set within valid values if scale is either linear or log.

        Parameters
        ----------
        data : np.ndarray
            Data to mask.
        data_option : DataOption
            Option containing scale information (linear or log).
        linear_ndigits : int, optional
            Mask value is rounded to this digit in linear case
            ex. if 2, 12.345 -> 12.35, by default 2
        log_ndigits : int, optional
            Mask value is rounded to this digit,
            ex. if 0, 12.345 -> 12, by default 0
        """
        # Since linear and log have different min / max, save both
        self._linear_min_real, self._linear_max_real = _get_min_max(data, zlog=False)
        self._log_min_real, self._log_max_real = _get_min_max(data, zlog=True)
        self.set_data_option(data_option)
        self._linear_ndigits = linear_ndigits
        self._log_ndigits = log_ndigits
        self._init_mask()

    def set_data_option(self, data_option: DataOption) -> None:
        """Need to call this to update if reference to data_option is changed."""
        self._data_option = data_option

    @property
    def log(self) -> bool:
        return self._data_option.zlog

    def _min_real(self, log: bool) -> float:
        if log:
            return self._log_min_real
        else:
            return self._linear_min_real

    def _max_real(self, log: bool) -> float:
        if log:
            return self._log_max_real
        else:
            return self._linear_max_real

    def _select_ndigits(self, log: bool) -> int:
        if log:
            return self._log_ndigits
        else:
            return self._linear_ndigits

    def _select_limit(self, value: float, log: bool) -> float:
        if not (log and value <= 0):
            return value
        else:
            return epsilon

    def _unscale(self, value: float, from_log: bool) -> float:
        if from_log:
            return 10**value
        else:
            return value

    def _scale(self, value: float, to_log: bool) -> float:
        if to_log:
            return np.log10(value)
        else:
            return value

    def _init_mask(self) -> None:
        masks = []
        for log in [True, False]:
            min = self._min_real(log)
            mask = self._select_limit(min, log)
            mask = self._scale(mask, log)
            mask = round_down(mask, self._select_ndigits(log))
            masks.append(mask)
        self._log_mask, self._linear_mask = masks

    @property
    def ndigits(self) -> int:
        return self._select_ndigits(self.log)

    @property
    def min_scaled(self) -> float:
        log = self.log
        min = self._min_real(log)
        min = self._select_limit(min, log)
        min = self._scale(min, log)
        min = round_down(min, self._select_ndigits(log))
        return min

    @property
    def max_scaled(self) -> float:
        log = self.log
        max = self._max_real(log)
        max = self._select_limit(max, log)
        max = self._scale(max, log)
        max = round_up(max, self._select_ndigits(log))
        return max

    @property
    def mask_scaled(self) -> float:
        if self.log:
            return self._log_mask
        else:
            return self._linear_mask

    def set_mask_scaled(self, mask: float) -> None:
        log = self.log
        if log:
            self._log_mask = round_down(mask, self._select_ndigits(log=True))
            linear_mask = self._unscale(self._log_mask, from_log=True)
            self._linear_mask = round_down(linear_mask, self._select_ndigits(log=False))
        else:
            self._linear_mask = round_down(mask, self._select_ndigits(log=False))
            log_mask = self._select_limit(self._linear_mask, log=True)
            log_mask = self._scale(log_mask, to_log=True)
            self._log_mask = round_down(log_mask, self._select_ndigits(log=True))

    @property
    def mask(self) -> float:
        mask = self.mask_scaled
        if self.log:
            mask = self._unscale(mask, from_log=True)
        return mask


# Used to get type hint during development
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Need to be place after definition of MaskManager
    _MaskManagersBase = UserDict[DataName, MaskManager]
else:
    _MaskManagersBase = UserDict


class MaskManagers(_MaskManagersBase):
    """Group MaskManager for different WFC analyzed data."""

    def __init__(self, data_options: DataOptions) -> None:
        super().__init__()
        for name, opt in data_options.items():
            # Data should be taken from original tplot data
            tplot_name = name.value
            data = get_data(tplot_name)
            mask_manager = MaskManager(data.y, opt)  # type: ignore
            self[name] = mask_manager

    def apply_mask(self) -> None:
        tplot_names, thresholds, zlogs, masks = [], [], [], []
        for name in DataName:
            mask_manager = self[name]
            opt = mask_manager._data_option
            tplot_names.append(name.value)
            thresholds.append(mask_manager.mask)
            zlogs.append(opt.zlog)
            masks.append(opt.mask)
        _apply_mask(tplot_names, thresholds, zlogs, masks)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
