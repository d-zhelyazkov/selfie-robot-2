#!/usr/bin/env python3
import logging as log
from pprint import pprint

import cv2.cv2 as cv
import numpy as np
from urllib3 import HTTPResponse

import camera
import imgproc.image_processor as imgproc
from camera.rest import ApiException

log.basicConfig(
    level=log.DEBUG,
    format='%(asctime)s %(message)s',
)

configuration = camera.Configuration()
configuration.host = "192.168.137.20:9001/camera"
# configuration.debug = True

# create an instance of the API class
camera_api = camera.DefaultApi(camera.ApiClient(configuration))

while True:

    try:
        # Get image.
        response: HTTPResponse = camera_api.image_get(_preload_content=False)
        pprint(response)

        np_arr = np.frombuffer(response.data, np.uint8)
        img = cv.imdecode(np_arr, cv.IMREAD_COLOR)
        log.info(f"Img size {img.shape[:2]}")
        cv.imwrite("camera_image.png", img)

        result = imgproc.process(img)
        log.info(f"Proc result {result}")

    except ApiException as e:
        print("Exception when calling DefaultApi->image_get: %s\n" % e)
