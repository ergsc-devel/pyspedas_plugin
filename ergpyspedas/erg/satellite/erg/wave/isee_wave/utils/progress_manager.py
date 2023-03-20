from abc import ABC, abstractmethod
from typing import Optional

from PySide6 import QtCore, QtWidgets

from ..wfc.erg_calc_pwe_wna import MessageKind


class ProgressManagerInterface(ABC):
    # You can implement this interface with or without GUI
    @abstractmethod
    def set_label_text(self, text: str) -> None:
        pass

    @abstractmethod
    def was_cancel_triggered(self) -> bool:
        pass

    @abstractmethod
    def complete(self) -> None:
        pass

    @abstractmethod
    def confirm_cancel(self, message: str, message_kind: MessageKind) -> None:
        pass

    @abstractmethod
    def was_canceled(self) -> bool:
        pass

    @abstractmethod
    def set_value(self, value: int) -> None:
        pass


class ProgressManager(ProgressManagerInterface):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Progress dialog with additional function."""
        self._minimum = 0
        self._maximum = 100
        self._progress = QtWidgets.QProgressDialog(
            labelText="",
            minimum=self._minimum,
            maximum=self._maximum,
            cancelButtonText="Cancel",
            flags=QtCore.Qt.WindowType.WindowTitleHint,  # Disable close button
            parent=parent,
        )
        self._progress.setWindowTitle("Operation in Progress...")
        self._progress.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        # If not specified the dialog will not show until a several tens of percent reached
        self._progress.setMinimumDuration(0)
        self._progress.forceShow()
        self._progress.setValue(0)
        # State
        self._canceled = False

    def set_label_text(self, text: str) -> None:
        if self._progress is None:
            raise ValueError("Progress dialog does not exist anymore.")

        self._progress.setLabelText(text)

    def was_cancel_triggered(self) -> bool:
        if self._progress is None:
            raise ValueError("Progress dialog does not exist anymore.")

        # HACK: Process event must be done at least twice to get real wasCanceled
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

        # Note that this is different from self.was_canceled
        return self._progress.wasCanceled()

    def complete(self) -> None:
        if self._progress is None:
            raise ValueError("Progress dialog does not exist anymore.")

        # When set, the dialog immediately closes
        self._progress.setValue(self._maximum)

    def close(self) -> None:
        # Close gracefully
        if self._progress is None:
            return

        self._progress.deleteLater()
        self._progress = None

    def confirm_cancel(self, message: str, message_kind: MessageKind) -> bool:
        if self._progress is None:
            raise ValueError("Progress dialog does not exist anymore.")

        if message_kind == MessageKind.question:
            button = QtWidgets.QMessageBox.question(self._progress, "Question", message)
            if button == QtWidgets.QMessageBox.StandardButton.No:
                return False
        elif message_kind == MessageKind.information:
            QtWidgets.QMessageBox.information(self._progress, "Information", message)
        elif message_kind == MessageKind.warning:
            QtWidgets.QMessageBox.warning(self._progress, "Warning", message)
        elif message_kind == MessageKind.error:
            QtWidgets.QMessageBox.critical(self._progress, "Error", message)
        else:
            ValueError(f"message_kind: {message_kind} is invalid.")

        self.close()

        # Admit cancel
        self._canceled = True
        return True

    def was_canceled(self) -> bool:
        return self._canceled

    def set_value(self, value: int) -> None:
        if self._progress is None:
            raise ValueError("Progress dialog does not exist anymore.")
        self._progress.setValue(value)
