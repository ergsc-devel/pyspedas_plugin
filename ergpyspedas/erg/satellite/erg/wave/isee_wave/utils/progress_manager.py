from abc import ABC, ABCMeta, abstractmethod
from enum import Enum, auto
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets


class MessageKind(Enum):
    error = auto()
    information = auto()
    question = auto()
    warning = auto()


class ProgressManagerInterface(ABC):
    # You can implement this interface with or without GUI
    @abstractmethod
    def canceled(self):
        pass

    @abstractmethod
    def set_canceled(self, canceled: bool) -> None:
        pass

    @abstractmethod
    def set_answer(self, answer: bool) -> None:
        pass

    @abstractmethod
    def ask_message(self, message: str, message_kind: MessageKind) -> bool:
        pass

    @abstractmethod
    def set_label_text(self, text: str) -> None:
        pass

    @abstractmethod
    def set_value(self, value: int) -> None:
        pass


# ProgressManager
class QObjectABCMeta(type(QtCore.QObject), ABCMeta):
    # NOTE: Does not work if base class order is otherwise
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

    def ask_message(self, message: str, message_kind: MessageKind) -> bool:
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

    def canceled(self) -> bool:
        return self._canceled

    def set_value(self, value: int) -> None:
        if self._progress is None:
            raise ValueError("Progress dialog does not exist anymore.")
        self._progress.setValue(value)


# class ProgressManager(QtCore.QObject):
class ProgressManagerForThread(
    ProgressManagerInterface, QtCore.QObject, metaclass=QObjectABCMeta
):
    # Signals
    set_label_text_signal = QtCore.Signal(str)
    set_value_signal = QtCore.Signal(int)
    ask_message_signal = QtCore.Signal(str, int)

    # States
    _canceled = False
    _answer = False

    # Threading
    mutex = QtCore.QMutex()
    answer_wait_condition = QtCore.QWaitCondition()

    def __init__(self) -> None:
        super().__init__()

    def canceled(self) -> bool:
        return self._canceled

    def set_canceled(self, canceled: bool) -> None:
        self._canceled = canceled

    def set_answer(self, answer: bool) -> None:
        self._answer = answer

    # Implement ProgressManagerInterface
    def ask_message(self, message: str, message_kind: MessageKind) -> bool:
        try:
            self.mutex.lock()
            # Pass enum value because emit accepts Python or Qt built-in types only
            self.ask_message_signal.emit(message, message_kind.value)
            # Wait until condition is met.
            # Transition of self.mutex:
            # Before: is locked in this thread
            # After wait: become unlocked
            # After wakeOne or wakeAll (exists in other place): become locked at last
            self.answer_wait_condition.wait(self.mutex)
        finally:
            # However it does not have to be locked at last this case, so unlock here
            # Always unlock at last to avoid deadlock
            self.mutex.unlock()
        return self._answer

    def set_label_text(self, text: str) -> None:
        self.set_label_text_signal.emit(text)

    def set_value(self, value: int) -> None:
        self.set_value_signal.emit(value)


class WorkerInterface(QtCore.QObject):
    # Signals
    succeeded = QtCore.Signal()
    failed = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.progress_manager = None

    def set_progress_manager(self, progress_manager: ProgressManagerForThread) -> None:
        self.progress_manager = progress_manager

    def run(self):
        raise NotImplementedError()

    def success(self) -> None:
        self.succeeded.emit()

    def fail(self) -> None:
        self.failed.emit()


class ThreadController:
    def _setup_worker(self, worker: WorkerInterface) -> None:
        self.worker = worker

    def _setup_thread(self) -> None:
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)  # type: ignore
        self.worker.failed.connect(self.on_worker_failed)
        self.worker.succeeded.connect(self.on_worker_succeeded)
        self.worker.succeeded.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.worker.succeeded.connect(self.worker.deleteLater)
        self.worker.failed.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)  # type: ignore

    def _start_thread(self) -> None:
        # Start thread
        self.thread.start()

    def on_worker_succeeded(self) -> None:
        pass

    def on_worker_failed(self) -> None:
        pass


class ProgressDialogWithoutImmediateHiding(QtWidgets.QDialog):
    # Signal
    canceled = QtCore.Signal()

    def __init__(
        self,
        labelText: str,
        cancelButtonText: str,
        minimum: int,
        maximum: int,
        parent: Optional[QtWidgets.QWidget] = None,
        flags: Optional[QtCore.Qt.WindowType] = None,
    ) -> None:
        """Custom progress dialog like QProgressDialog.

        However, the dialog is not hidden immediately after the cancel button
        is clicked, because it is generally difficult to immediately stop
        the long running task that the dialog monitors.

        This just emits signal that the button is clicked and
        user should define other behaviours.
        """

        super().__init__(parent=parent)
        if flags is not None:
            self.setWindowFlags(flags)

        self.label = QtWidgets.QLabel(labelText)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMinimum(minimum)
        self.progress_bar.setMaximum(maximum)
        self.button = QtWidgets.QPushButton(cancelButtonText)
        self._was_canceled = False

        # Layout is as same as QProgressDialog
        layout = QtWidgets.QVBoxLayout(self)
        label_layout = QtWidgets.QHBoxLayout()
        label_layout.addStretch()
        label_layout.addWidget(self.label)
        label_layout.addStretch()
        layout.addLayout(label_layout)
        layout.addWidget(self.progress_bar)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.button)
        layout.addLayout(button_layout)

        self.button.clicked.connect(self._on_button_clicked)  # type: ignore

    def setValue(self, progress: int) -> None:
        # Do not auto close at 100% progress (Different from QProgressDialog)
        self.progress_bar.setValue(progress)

    def setLabelText(self, text: str) -> None:
        self.label.setText(text)

    def _on_button_clicked(self) -> None:
        self.canceled.emit()
        self._was_canceled = True

    def wasCanceled(self) -> bool:
        """Return whether cancel button was pressed. Used in single thread."""
        return self._was_canceled

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Pressing close hint button or typing closing keyboard shortcuts is
        now same as pressing cancel button.
        """
        event.ignore()
        self._on_button_clicked()


class ProgressManagerForThreadController(ThreadController):
    def _setup_progress_manager(
        self, parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        self._progress_dialog = ProgressDialogWithoutImmediateHiding(
            labelText="",
            minimum=0,
            maximum=100,
            cancelButtonText="Cancel",
            parent=parent,
        )
        self._progress_dialog.setWindowTitle("Operation in Progress...")
        self._progress_dialog.setWindowModality(
            QtCore.Qt.WindowModality.ApplicationModal
        )
        self._progress_dialog.canceled.connect(
            self.on_progress_dialog_canceled_with_thread
        )
        self._progress_dialog.show()

        self.progress_manager = ProgressManagerForThread()
        self.worker.set_progress_manager(self.progress_manager)
        self.worker.succeeded.connect(self.progress_manager.deleteLater)
        self.worker.failed.connect(self.progress_manager.deleteLater)
        self.progress_manager.moveToThread(self.thread)
        self.progress_manager.set_label_text_signal.connect(
            self.on_progress_manager_set_label_text
        )
        self.progress_manager.set_value_signal.connect(
            self.on_progress_manager_set_value
        )
        self.progress_manager.ask_message_signal.connect(
            self.on_progress_manager_ask_message
        )

    def _show_message_box(self, message: str, message_kind: MessageKind) -> bool:
        if message_kind == MessageKind.question:
            button = QtWidgets.QMessageBox.question(
                self._progress_dialog, "Question", message
            )
            if button == QtWidgets.QMessageBox.StandardButton.No:
                return False
        elif message_kind == MessageKind.information:
            QtWidgets.QMessageBox.information(
                self._progress_dialog, "Information", message
            )
        elif message_kind == MessageKind.warning:
            QtWidgets.QMessageBox.warning(self._progress_dialog, "Warning", message)
        elif message_kind == MessageKind.error:
            QtWidgets.QMessageBox.critical(self._progress_dialog, "Error", message)
        else:
            ValueError(f"message_kind: {message_kind} is invalid.")
        return True

    def on_progress_manager_ask_message(
        self, message: str, message_kind_value: int
    ) -> None:
        # Need this conversion because Qt signal and slot
        # allows Python or Qt build-ins only
        message_kind = MessageKind(message_kind_value)
        # Get answer from user while worker thread is stopped
        with QtCore.QMutexLocker(self.progress_manager.mutex):
            answer = self._show_message_box(message, message_kind)
            # Pass answer to worker thread
            self.progress_manager.set_answer(answer)
            # Resume worker thread
            self.progress_manager.answer_wait_condition.wakeAll()

    def on_progress_manager_set_value(self, value: int) -> None:
        self._progress_dialog.setValue(value)

    def on_progress_manager_set_label_text(self, value: str) -> None:
        self._progress_dialog.setLabelText(value)

    def on_progress_dialog_canceled_with_thread(self) -> None:
        # Show that cancel step is started
        self._progress_dialog.button.setEnabled(False)
        self._progress_dialog.setLabelText("Cancelling...")
        self._progress_dialog.progress_bar.hide()
        # If worker thread with progress manager exists, ask to stop
        if getattr(self, "progress_manager") and self.progress_manager is not None:
            self.progress_manager.set_canceled(True)

    def on_worker_failed(self):
        self._progress_dialog.hide()
