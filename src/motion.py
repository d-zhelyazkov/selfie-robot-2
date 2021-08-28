import logging
import threading
import time

import serial

import reactives
import threads

log = logging.getLogger(__name__)


class Motion:

    def __init__(self) -> None:
        self.events = reactives.Subject()
        self.__comm = None
        self.__reading_thread = None

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
        log.info(f"Turning {deg} degrees...")
        self.__move(f"TURN {deg} DEG")

    def movef(self, dist):
        """
        :param dist: cm
        """
        log.info(f"Moving forward...")
        self.__move(f"MOVE FORWARD {int(dist)} UNITS")

    def __move(self, cmd):
        if not self.__comm:
            log.warning("Cannot move since not initialized...")
            return

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
                log.error("Moving didn't complete on time...")

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
