import logging as log

import numpy as np
from cv2 import cv2 as cv
from urllib3 import HTTPResponse

import camera
import reactives

camera_config = camera.Configuration()
camera_config.host = "192.168.137.20:9001/camera"
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
