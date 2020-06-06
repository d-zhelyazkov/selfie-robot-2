#!/usr/bin/env python3


from multiprocessing import Pool
from multiprocessing import cpu_count
import signal

stop_loop = 0


def exit_child(_, __):
    global stop_loop
    stop_loop = 1


def f(x):
    global stop_loop
    while not stop_loop:
        x * x


signal.signal(signal.SIGINT, exit_child)
if __name__ == '__main__':
    processes = cpu_count()
    pool = Pool(processes)

    print('-' * 20)
    print('Running load on CPU(s)')
    print('Utilizing %d cores' % processes)
    print('-' * 20)
    pool.map(f, range(processes))
    pool.terminate()
