#!/usr/bin/env python3

import cv2
import config

WIN_SIZE = (400, 300)


def show_image(img, row, col, win_name):

    # win_name = str(x) + str(y)
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, WIN_SIZE[0], WIN_SIZE[1])
    cv2.moveWindow(win_name, col * WIN_SIZE[0], row * WIN_SIZE[1])
    cv2.imshow(win_name, img)


def show_debug_image(img, row, col, win_name):
    if not config.debug:
        return

    show_image(img, row, col, win_name)
