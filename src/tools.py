import random

import numpy as np
from cv2 import cv2 as cv

WIN_SIZE = (400, 225)
IMG_SIZE = (1280, 720)

GREEN_COLOR = (0, 255, 0)


def init_window(name, row=0, col=0):
    cv.namedWindow(name, cv.WINDOW_NORMAL)
    cv.resizeWindow(name, WIN_SIZE[0], WIN_SIZE[1])
    cv.moveWindow(name, col * WIN_SIZE[0], row * WIN_SIZE[1])
    warmup_img = np.zeros(
        shape=(IMG_SIZE[1], IMG_SIZE[0], 3),
        dtype=np.uint8
    )
    show_image(warmup_img, name)


def show_image(img, win_name):
    # win_name = str(x) + str(y)

    cv.imshow(win_name, img)
    cv.waitKey(1)


def draw_points(img, points):
    result_img = img.copy()

    for point in points:
        position = (int(point[0]), int(point[1]))
        cv.drawMarker(
            img=result_img,
            position=position,
            color=GREEN_COLOR,
            markerType=cv.MARKER_TILTED_CROSS,
            markerSize=50,
            thickness=10,
            line_type=cv.LINE_AA
        )

    return result_img


def do_random_task(tasks: list):
    if len(tasks) == 0:
        return False

    task = random.choice(tasks)
    result = task()

    return result


def s2ns(s):
    return s * 1_000_000_000
