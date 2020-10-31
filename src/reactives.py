import threading
from typing import Any

import rx.subject


class Subject(rx.subject.Subject):

    def __init__(self):
        super().__init__()

        self.last = None
        self._next_event = threading.Event()

    def on_next(self, value: Any) -> None:
        self.last = value
        super().on_next(value)
        self._next_event.set()

    def wait_next(self):
        self._next_event.clear()
        self._next_event.wait()
