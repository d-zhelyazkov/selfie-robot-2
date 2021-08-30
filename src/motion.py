import logging
import threading
import time
from collections import deque
from dataclasses import dataclass

import serial

import reactives
import threads

log = logging.getLogger(__name__)


@dataclass
class Command:
    cmd: str
    val: int
    units: str

    def __str__(self):
        return f"{self.cmd} {self.val} {self.units}"

    def revert(self) -> 'Command':
        return Command(
            self.cmd,
            -self.val,
            self.units,
        )


class Motion:

    def __init__(self) -> None:
        self.events = reactives.Subject()
        self.__comm = None
        self.__reading_thread = None
        self.__recent_moves = deque(maxlen=10)

    def __enter__(self):
        self.init()
        return self

    def init(self):
        log.info("Initializing serial comm...")

        self.__reading_thread = threads.RepeatingTimer(
            function=self.__read,
            interval=0.1,
        )
        self.__comm = serial.Serial("/dev/ttyACM0", timeout=1,
                                    baudrate=9600)
        self.__reading_thread.start()
        time.sleep(5)
        log.info("Initialized.")

    def __read(self):
        raw_reading = self.__comm.readline()
        if not raw_reading:
            return

        string = raw_reading.decode().strip()
        # string = string.replace("\n", "; ")
        log.info(string)
        self.events.on_next(string)

    def turn(self, deg):
        deg = int(deg)
        cmd = Command("TURN", deg, "DEG")

        log.info(f"Turning {deg} degrees...")
        self.__move(cmd)

    def movef(self, dist):
        """
        :param dist: cm
        """
        dist = int(dist)
        cmd = Command("MOVE FORWARD", dist, "UNITS")

        log.info(f"Moving {dist}cm forward...")
        self.__move(cmd)

        self.__recent_moves.append(cmd)

    def __move(self, cmd: Command):
        if not self.__comm:
            log.warning("Cannot move since not initialized...")
            return

        done = threading.Event()

        def check_done(event):
            if event in ("STOPPED", "INVALID"):
                done.set()

        with self.events.subscribe(check_done):
            self.__comm.write(str(cmd).encode())
            success = done.wait(10)
            if success:
                log.info("Move complete!")
            else:
                log.error("Moving didn't complete on time...")

    def back(self):
        if not len(self.__recent_moves):
            return

        last_cmd: Command = self.__recent_moves.pop()
        self.__move(last_cmd.revert())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def stop(self):
        self.__reading_thread.cancel()
        self.__comm.close()
        self.__comm = None


class NullMotion(Motion):
    def init(self):
        pass

    def stop(self):
        pass
