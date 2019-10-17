#!/usr/bin/env python3

import cv2

from util import *

GREEN_COLOR = (0, 255, 0)
RED_COLOR = (0, 0, 255)
BORDER_SIZE = 100
ERODE_KERNEL = kernel(3)
DILATE_KERNEL = kernel(9)

from window import show_debug_image

blob_detector_params = cv2.SimpleBlobDetector_Params()
blob_detector_params.filterByArea = False
blob_detector_params.filterByCircularity = False
blob_detector_params.filterByInertia = False
blob_detector_params.filterByConvexity = False
blob_detector_params.filterByColor = False
blob_detector_params.blobColor = 255
blob_detector = cv2.SimpleBlobDetector_create(blob_detector_params)


def process_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    show_debug_image(img, 0, 0, "image")

    (blue_img, green_img, red_img) = cv2.split(img)

    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    (hue_img, sat_img, value_img) = cv2.split(hsv_img)
    show_debug_image(sat_img, 0, 1, "saturation")

    blue_points = process_channel(blue_img, sat_img, 1, "blue")
    red_points = process_channel(red_img, sat_img, 2, "red")

    show_result(img, blue_points, red_points)
    return blue_points, red_points


def process_channel(ch_img, sat_img, row, channel_name):
    # channel_name = "channel " + str(row)
    show_debug_image(ch_img, row, 0, channel_name)

    ch_sat_img = cv2.bitwise_and(ch_img, sat_img)
    show_debug_image(ch_sat_img, row, 1, channel_name + " sat")

    (result, half_bin_image) = cv2.threshold(ch_sat_img, 255 / 2, 255, cv2.THRESH_TOZERO)
    (result, bin_img) = cv2.threshold(half_bin_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    show_debug_image(bin_img, row, 2, channel_name + " thresh")

    bin_img = cv2.erode(bin_img, ERODE_KERNEL)
    bin_img = cv2.dilate(bin_img, DILATE_KERNEL)
    # bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel(5))
    # bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel(21))
    show_debug_image(bin_img, row, 3, channel_name + " morph")

    # Detect blobs.
    blobs = blob_detector.detect(bin_img)
    blob_center_points = [blob.pt
                          for blob in blobs]
    return blob_center_points


def show_result(img, blue_points, red_points):
    if not config.debug:
        return

    result_img = img.copy()

    points = blue_points + red_points
    for point in points:
        position = (int(point[0]), int(point[1]))
        cv2.drawMarker(
            img=result_img,
            position=position,
            color=GREEN_COLOR,
            markerType=cv2.MARKER_TILTED_CROSS,
            markerSize=100,
            thickness=20,
            line_type=cv2.LINE_AA
        )

    success = len(blue_points) == 2 and len(red_points) == 1
    border_color = GREEN_COLOR if success else RED_COLOR
    result_img = cv2.copyMakeBorder(
        src=result_img,
        top=BORDER_SIZE,
        bottom=BORDER_SIZE,
        left=BORDER_SIZE,
        right=BORDER_SIZE,
        borderType=cv2.BORDER_CONSTANT,
        value=border_color
    )

    show_debug_image(result_img, 0, 2, "result")
