import logging as log

import numpy as np
import rx.core as rx
import urllib3
from cv2 import cv2 as cv
from urllib3 import HTTPResponse

import camera
import reactives

camera_config = camera.Configuration()
camera_config.host = "192.168.137.22:9001/camera"
camera_config.timeout = urllib3.Timeout(connect=1, read=2)

# camera_config.retry = urllib3.Retry(total=5, backoff_factor=0.1)
# camera_config.retry.RETRY_AFTER_STATUS_CODES = list(urllib3.Retry.RETRY_AFTER_STATUS_CODES) + [422]

# camera_config.debug = True
camera_api = camera.DefaultApi(camera.ApiClient(camera_config))
# create an instance of the API class

# camera_api.settings_aecompensation_put(camera.AECompensationValue(-2.0))
# camera_api.settings_aelock_put(camera.AELockValue(True))
# camera_api.settings_aemode_put(camera.AEModeValue(camera.AEMode.OFF))
# camera_api.settings_iso_put(camera.ISOValue(50))
# camera_api.settings_shutterspeed_put(body=camera.ShutterSpeedValue(100000))


images = reactives.Subject()
images.last = np.ndarray(())


def image():
    response: HTTPResponse = camera_api.image_get(_preload_content=False)

    np_arr = np.frombuffer(response.data, np.uint8)
    img = cv.imdecode(np_arr, cv.IMREAD_COLOR)
    log.debug("Image size: %s", img.shape[:2])

    images.on_next(img)

    return img


class ParamOptimizer(rx.Observer):

    def __init__(self):
        super().__init__()

        camera_api.settings_aemode_put(camera.AEModeValue(camera.AEMode.OFF
                                                          ))

    def on_next(self, processing_result) -> None:
        (_, points) = processing_result
        (blue_points, red_points) = points
        points_cnt = len(blue_points) + len(red_points)
        if points_cnt == 3:
            return

        if points_cnt < 3:
            self.increase_exposure()
        elif points_cnt > 3:
            self.decrease_exposure()

    @staticmethod
    def increase_exposure():
        iso: camera.ISOInfo = camera_api.settings_iso_get()
        new_iso = int(iso.value) * 2
        if new_iso <= int(iso.values[-1]):
            camera_api.settings_iso_put(camera.ISOValue(str(new_iso)))

    @staticmethod
    def decrease_exposure():
        iso: camera.ISOInfo = camera_api.settings_iso_get()
        new_iso = int(int(iso.value) / 2)
        if int(iso.values[0]) <= new_iso:
            camera_api.settings_iso_put(camera.ISOValue(str(new_iso)))
