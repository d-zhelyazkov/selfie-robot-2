#!/usr/bin/env python3

import cv2.cv2 as cv
from imgproc import config

WIN_SIZE = (400, 300)

windowses = set()


def init(row, col, win_name):
    # win_name = str(x) + str(y)
    if win_name in windowses:
        return

    cv.namedWindow(win_name, cv.WINDOW_NORMAL)
    cv.resizeWindow(win_name, WIN_SIZE[0], WIN_SIZE[1])
    cv.moveWindow(win_name, col * WIN_SIZE[0], row * WIN_SIZE[1])
    windowses.add(win_name)


def show_image(img, row, col, win_name):
    init(row, col, win_name)
    cv.imshow(win_name, img)
    cv.waitKey(1)


def show_debug_image(img, row, col, win_name):
    if not config.debug:
        return

    show_image(img, row, col, win_name)
