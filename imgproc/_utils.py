#!/usr/bin/env python3

import imgproc.config as config
import numpy as np

ONE_M = 10 ** 6


def kernel(size):
    return np.ones((size, size), np.uint8)


def debug(message):
    if not config.debug:
        return

    print(message)


def num_to_m(num):
    return num / ONE_M


def m_to_num(m):
    return m * ONE_M
