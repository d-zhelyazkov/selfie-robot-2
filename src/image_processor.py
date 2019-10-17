#!/usr/bin/env python3

import cv2
import numpy as np
import window


def process_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    window.show_image(img, 0, 0, "image")

    (blue_img, green_img, red_img) = cv2.split(img)

    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    (hue_img, sat_img, value_img) = cv2.split(hsv_img)
    window.show_image(sat_img, 0, 1, "saturation")

    process_channel(blue_img, sat_img, 1, "blue")
    process_channel(red_img, sat_img, 2, "red")


def process_channel(ch_img, sat_img, row, channel_name):
    # channel_name = "channel " + str(row)
    window.show_image(ch_img, row, 0, channel_name)

    ch_sat_img = cv2.bitwise_and(ch_img, sat_img)
    window.show_image(ch_sat_img, row, 1, channel_name + " sat")

    (result, half_bin_image) = cv2.threshold(ch_sat_img, 255 / 2, 255, cv2.THRESH_TOZERO)
    (result, bin_img) = cv2.threshold(half_bin_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    window.show_image(bin_img, row, 2, channel_name + " thresh")

    bin_img = cv2.erode(bin_img, kernel(5))
    bin_img = cv2.dilate(bin_img, kernel(25))
    # bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel(5))
    # bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel(21))
    window.show_image(bin_img, row, 3, channel_name + " morph")


def kernel(size):
    return np.ones((size, size), np.uint8)
