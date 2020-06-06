#!/usr/bin/env python3

from threading import Thread

import time
import serial


def do_motion(comm):
    print("Sending TURN command...")
    comm.write("TURN 180 DEG".encode())
    time.sleep(3)


def init():
    print("Initializing ARDUINO serial...")
    comm = serial.Serial("/dev/ttyACM0", timeout=1,
                         baudrate=9600)

    def reading():
        while True:
            time.sleep(0.1)
            raw_reading = comm.readline()
            if len(raw_reading) == 0:
                continue

            string = raw_reading.decode()
            # string = string.replace("\n", "; ")
            print("ARDUINO: " + string)

    reading_thread = Thread(target=reading)
    reading_thread.start()

    time.sleep(5)
    print("Initialized.")

    return comm


def main():
    comm = init()

    while True:
        do_motion(comm)


if __name__ == '__main__':
    main()
