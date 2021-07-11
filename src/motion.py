import logging
import threading
import time
from threading import Thread

import serial

import reactives

log = logging.getLogger(__name__)


class Motion:

    def __init__(self) -> None:
        self.events = reactives.Subject()

    def __enter__(self):

        log.info("Initializing serial comm...")

        self.__reading_thread = Thread(target=self.__reading)
        self.__comm = serial.Serial("/dev/ttyACM0", timeout=1,
                                    baudrate=9600)
        self.__reading_thread.start()
        time.sleep(5)
        log.info("Initialized.")

        return self

    def __reading(self):
        while True:
            time.sleep(0.1)
            raw_reading = self.__comm.readline()
            if not raw_reading:
                continue

            string = raw_reading.decode().strip()
            # string = string.replace("\n", "; ")
            log.info(string)
            self.events.on_next(string)

    def turn(self, deg):
        deg = int(deg)
        log.info(f"Turning {deg} degrees...")
        self.__move(f"TURN {deg} DEG")

    def movef(self, dist):
        """
        :param dist: cm
        """
        log.info(f"Moving forward...")
        self.__move(f"MOVE FORWARD {int(dist)} UNITS")

    def __move(self, cmd):
        done = threading.Event()

        def check_done(event):
            if event in ("STOPPED", "INVALID"):
                done.set()

        with self.events.subscribe(check_done):
            self.__comm.write(cmd.encode())
            success = done.wait(10)
            if success:
                log.info("Move complete!")
            else:
                log.error("Turning didn't complete...")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__comm.close()
