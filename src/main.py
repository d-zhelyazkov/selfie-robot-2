#!/usr/bin/env python3
import logging as log

import cv2.cv2 as cv
import numpy as np
from urllib3 import HTTPResponse

import camera
import reactives
import threads
from imgproc import image_processor as imgproc
from tools import show_image, draw_points, init_window

log.basicConfig(
    level=log.DEBUG,
    format='%(asctime)s %(message)s',
)

init_window("result")

camera_config = camera.Configuration()
camera_config.host = "192.168.137.20:9001/camera"
# camera_config.debug = True
camera_api = camera.DefaultApi(camera.ApiClient(camera_config))
# create an instance of the API class

# camera_api.settings_aecompensation_put(camera.AECompensationValue(-2.0))
# camera_api.settings_aelock_put(camera.AELockValue(True))
camera_api.settings_aemode_put(camera.AEModeValue(camera.AEMode.OFF))
camera_api.settings_iso_put(camera.ISOValue(50))
camera_api.settings_shutterspeed_put(body=camera.ShutterSpeedValue(100000))

images = reactives.Subject()
images.last = np.ndarray(())

processed_imgs = reactives.Subject()
processed_imgs.last = (images.last, ([], []))


def show_result(img, points):
    (blue_points, red_points) = points
    show_image(draw_points(img, blue_points + red_points), "result")


def image():
    response: HTTPResponse = camera_api.image_get(_preload_content=False)

    np_arr = np.frombuffer(response.data, np.uint8)
    img = cv.imdecode(np_arr, cv.IMREAD_COLOR)
    log.debug("Image size: %s", img.shape[:2])

    images.on_next(img)


def process():
    if np.array_equal(images.last, processed_imgs.last[0]):
        images.wait_next()

    result = imgproc.process(images.last)
    (blue_dots, red_dots) = result
    log.info("Img processed. Found %d blue and %d red points", len(blue_dots), len(red_dots))
    processed_imgs.on_next((images.last, (blue_dots, red_dots)))


def main():
    with \
            threads.RepeatingTimer(
                function=image,
                interval=0,
                name="ImgThread",
            ) as img_thread, \
            threads.RepeatingTimer(
                function=process,
                interval=0,
                name="ProcessThread",
            ) as process_thread:
        img_thread.start()
        process_thread.start()

        while True:
            processed_imgs.wait_next()
            show_result(*processed_imgs.last)

        # process_thread.join()
        # img_thread.join()


if __name__ == "__main__":
    main()
