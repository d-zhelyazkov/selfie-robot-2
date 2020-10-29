#!/usr/bin/env python3
import logging as log

import cv2.cv2 as cv
import numpy as np
import rx.operators as rx_ops
import rx.subject as rx_subj
from urllib3 import HTTPResponse

import camera
from camera import AEModeValue, AEMode, ISOValue, ShutterSpeedValue
from camera import AELockValue
from imgproc import image_processor as imgproc
from tools import show_image, draw_points, init_window

log.basicConfig(
    level=log.DEBUG,
    format='%(asctime)s %(message)s',
)

init_window("result")

camera_config = camera.Configuration()
camera_config.host = "192.168.137.21:9001/camera"
# camera_config.debug = True
camera_api = camera.DefaultApi(camera.ApiClient(camera_config))
# create an instance of the API class

# camera_api.settings_aecompensation_put(AECompensationValue(-2.0))
camera_api.settings_aelock_put(AELockValue(True))
# camera_api.settings_aemode_put(AEModeValue(AEMode.OFF))
# camera_api.settings_iso_put(ISOValue(50))
# camera_api.settings_shutterspeed_put(body=ShutterSpeedValue(100000))

images = rx_subj.Subject()
processed_imgs = rx_subj.Subject()


def show_result(img, points):
    (blue_points, red_points) = points
    show_image(draw_points(img, blue_points + red_points), "result")


images.subscribe(on_next=lambda img: log.info(
    f"Image size: {img.shape[:2]}"))
images.pipe(
    rx_ops.map(lambda img: (img, imgproc.process(img)))
).subscribe(processed_imgs)
processed_imgs.subscribe(
    on_next=lambda result: show_result(*result))
processed_imgs.subscribe(
    on_next=lambda result: log.info(
        f"Img processed. Found {len(result[1][0])} blue and {len(result[1][1])} red points")
)


def main():
    while True:
        # Get image.
        response: HTTPResponse = camera_api.image_get(_preload_content=False)

        np_arr = np.frombuffer(response.data, np.uint8)
        img = cv.imdecode(np_arr, cv.IMREAD_COLOR)

        images.on_next(img)


if __name__ == "__main__":
    main()
