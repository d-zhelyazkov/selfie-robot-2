#!/usr/bin/env python3

from multiprocessing import Pool
from multiprocessing import cpu_count

import time

import arduino_loop as arduino


# noinspection Pylint
def f(x):
    while True:
        x * x


def do_processing():
    processes = cpu_count()
    pool = Pool(processes)

    print('Utilizing %d cores' % processes)
    pool.map_async(f, range(processes))
    print("CPU utilized.")

    time.sleep(5)

    print("Finishing processing...")
    pool.terminate()
    print("Done processing.")


def main():
    arduino_comm = arduino.init()

    while True:
        do_processing()
        arduino.do_motion(arduino_comm)


if __name__ == '__main__':
    main()
