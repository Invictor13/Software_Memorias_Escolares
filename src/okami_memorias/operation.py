"""Progresso e cancelamento cooperativo, independentes da interface."""

from collections.abc import Callable
from threading import Event

from .errors import OperationCancelled


class Operation:
    def __init__(self, report: Callable[[str, int, int], None]):
        self._cancelled = Event()
        self._report = report

    def cancel(self) -> None:
        self._cancelled.set()

    def checkpoint(self) -> None:
        if self._cancelled.is_set():
            raise OperationCancelled

    def progress(self, phase: str, completed: int, total: int) -> None:
        self.checkpoint()
        self._report(phase, completed, total)
