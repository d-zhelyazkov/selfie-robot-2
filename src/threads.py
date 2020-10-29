"""
Module with timer utilities.
"""

import threading
from typing import Callable, Any, Optional, Iterable, Mapping


class Timer(threading.Timer):
    def __init__(self,
                 interval: float,
                 function: Callable[..., Any],
                 args: Optional[Iterable[Any]] = None,
                 kwargs: Optional[Mapping[str, Any]] = None,
                 name: str = None,
                 ) -> None:
        super().__init__(interval, function, args, kwargs)

        self.name = name

    def __enter__(self) -> "Timer":
        return self

    def __exit__(self, _, __, ___) -> None:
        self.cancel()


class RepeatingTimer(Timer):

    # noinspection PyUnresolvedReferences
    def run(self) -> None:

        while True:

            self.__wait(self.interval)

            if self.finished.is_set():
                break

            self.function(*self.args, **self.kwargs)

    def __wait(self, interval: float) -> None:
        # noinspection PyUnresolvedReferences
        self.finished.wait(interval)
