#!/usr/bin/env python3

import imgproc._config as config
from tools import show_image


def show_debug_image(img, row, col, win_name):
    if not config.debug:
        return

    show_image(img, win_name, row, col, )
