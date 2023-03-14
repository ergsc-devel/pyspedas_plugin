from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets

from ..utils.utils import check_safe_string, safe_eval_formula


class LineEditWithValidator(QtWidgets.QLineEdit):
    def __init__(
        self,
        validator: QtGui.QValidator,
        text: str = "",
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(text, parent)
        self.setValidator(validator)

    def focusOutEvent(self, text: QtGui.QFocusEvent) -> None:
        # args are input, cursor position
        ret = self.validator().validate(self.text(), 0)
        # ret is tuple of state, input, cursor position
        # States are Acceptable, Intermediate, Invalid
        # Since user cannot even input invalid text,
        # considering intermediate is enough
        if ret[0] == QtGui.QValidator.State.Intermediate:  # type: ignore
            self.setFocus()
        else:
            super().focusOutEvent(text)


class DoubleValidator(QtGui.QValidator):
    def __init__(
        self,
        bottom: Optional[float] = None,
        top: Optional[float] = None,
        parent: Optional[QtCore.QObject] = None,
    ) -> None:
        super().__init__(parent)
        if bottom is None:
            bottom = -float("inf")
        self._bottom = bottom
        if top is None:
            top = float("inf")
        self._top = top

    def validate(self, text: str, cursor_pos: int) -> object:
        is_safe = check_safe_string(text)
        if not is_safe:
            return (QtGui.QValidator.State.Invalid, text, cursor_pos)
        number = safe_eval_formula(text)
        if number is None:
            return (QtGui.QValidator.State.Intermediate, text, cursor_pos)
        if number < self._bottom:
            return (QtGui.QValidator.State.Intermediate, text, cursor_pos)
        if number > self._top:
            return (QtGui.QValidator.State.Intermediate, text, cursor_pos)
        return (QtGui.QValidator.State.Acceptable, text, cursor_pos)

    def setBottom(self, value: float) -> None:
        self._bottom = value

    def setTop(self, value: float) -> None:
        self._top = value


class IntValidator(QtGui.QValidator):
    def __init__(
        self,
        bottom: Optional[int] = None,
        top: Optional[int] = None,
        parent: Optional[QtCore.QObject] = None,
    ) -> None:
        super().__init__(parent)
        if bottom is None:
            bottom = -float("inf")  # type: ignore
        self._bottom = bottom
        if top is None:
            top = float("inf")  # type: ignore
        self._top = top

    def validate(self, text: str, cursor_pos: int) -> object:
        is_safe = check_safe_string(text)
        if not is_safe:
            return (QtGui.QValidator.State.Invalid, text, cursor_pos)
        number = safe_eval_formula(text)
        if number is None:
            return (QtGui.QValidator.State.Intermediate, text, cursor_pos)
        if not number.is_integer():
            return (QtGui.QValidator.State.Intermediate, text, cursor_pos)
        if number < self._bottom:  # type: ignore
            return (QtGui.QValidator.State.Intermediate, text, cursor_pos)
        if number > self._top:  # type: ignore
            return (QtGui.QValidator.State.Intermediate, text, cursor_pos)
        return (QtGui.QValidator.State.Acceptable, text, cursor_pos)

    def setBottom(self, value: int) -> None:
        self._bottom = value

    def setTop(self, value: int) -> None:
        self._top = value
