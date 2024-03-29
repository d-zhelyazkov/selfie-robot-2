#!/usr/bin/env python3
import concurrent.futures
import logging
import math

import cv2.cv2 as cv

from imgproc._utils import *
from imgproc._windows import show_debug_image
from tools import draw_points

log = logging.getLogger(__name__)

GREEN_COLOR = (0, 255, 0)
RED_COLOR = (0, 0, 255)
BORDER_SIZE = 10
PROCESS_PIC_SIZE = m_to_num(1)

blob_detector_params = cv.SimpleBlobDetector_Params()
blob_detector_params.filterByArea = False
blob_detector_params.filterByCircularity = True
blob_detector_params.filterByInertia = False
blob_detector_params.filterByConvexity = False
blob_detector_params.filterByColor = False
blob_detector_params.blobColor = 255
blob_detector = cv.SimpleBlobDetector_create(blob_detector_params)

multithreading = not config.debug
if multithreading:
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def process(img):
    show_debug_image(img, 0, 0, "image")

    (resized_img, resize_k) = resize_image(img)

    (blue_img, green_img, red_img) = cv.split(resized_img)

    hsv_img = cv.cvtColor(resized_img, cv.COLOR_BGR2HSV)
    (hue_img, sat_img, value_img) = cv.split(hsv_img)
    show_debug_image(sat_img, 0, 1, "saturation")

    def process_blue_channel():
        return process_channel(blue_img, sat_img, 1, "blue")

    def process_red_channel():
        return process_channel(red_img, sat_img, 2, "red")

    tasks = (process_blue_channel, process_red_channel)

    if multithreading:
        futures = list(map(
            lambda task: executor.submit(task),
            tasks,
        ))

        points_sets = list(map(
            lambda future: future.result(),
            futures,
        ))
    else:
        points_sets = list(map(
            lambda task: task(),
            tasks,
        ))

    points_sets = list(map(
        lambda point_set: convert_points(point_set, resize_k),
        points_sets,
    ))

    show_result(img, *points_sets)
    return points_sets


def process_channel(ch_img, sat_img, row, channel_name):
    # channel_name = "channel " + str(row)
    show_debug_image(ch_img, row, 0, channel_name)

    ch_sat_img = cv.bitwise_and(ch_img, sat_img)
    show_debug_image(ch_sat_img, row, 1, channel_name + " sat")

    (result, half_bin_image) = cv.threshold(ch_sat_img, 255 / 2, 255, cv.THRESH_TOZERO)
    (result, bin_img) = cv.threshold(half_bin_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    show_debug_image(bin_img, row, 2, channel_name + " thresh")

    bin_img = cv.erode(bin_img, kernel(3))
    bin_img = cv.dilate(bin_img, kernel(9))
    # bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel(5))
    # bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel(21))
    show_debug_image(bin_img, row, 3, channel_name + " morph")

    # Detect blobs.
    blobs = blob_detector.detect(bin_img)
    log.info("Found %d %s blobs.", len(blobs), channel_name)

    blob_center_points = [blob.pt
                          for blob in blobs]
    return blob_center_points


def convert_points(points, k):
    return [tuple(d * k for d in point)
            for point in points]


def resize_image(img):
    (height, width, _) = img.shape
    img_size = width * height
    debug("Image size: {}MP".format(num_to_m(img_size)))

    k = math.sqrt(img_size / min(img_size, PROCESS_PIC_SIZE))
    debug("Resize ratio: " + str(k))

    resized_width = int(width / k)
    resized_height = int(height / k)
    resized_image = cv.resize(img, (resized_width, resized_height))
    (resized_height, resized_width, _) = resized_image.shape
    debug("Resized image size: {}MP".format(num_to_m(resized_width * resized_height)))

    return resized_image, k


def are_robot_points(blue_points, red_points):
    return len(blue_points) == 2 and len(red_points) == 1


def show_result(img, blue_points, red_points):
    if not config.debug:
        return

    result_img = img.copy()

    result_img = draw_points(result_img, blue_points + red_points)

    success = are_robot_points(blue_points, red_points)
    border_color = GREEN_COLOR if success else RED_COLOR
    result_img = cv.copyMakeBorder(
        src=result_img,
        top=BORDER_SIZE,
        bottom=BORDER_SIZE,
        left=BORDER_SIZE,
        right=BORDER_SIZE,
        borderType=cv.BORDER_CONSTANT,
        value=border_color
    )

    show_debug_image(result_img, 0, 2, "result")
