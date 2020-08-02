#!/usr/bin/env python3

import cv2.cv2 as cv
import numpy as np
import requests
import imgproc.image_processor as imgproc
import logging as log

log.basicConfig(
    level=log.DEBUG,
    format='%(asctime)s %(message)s',
)

while True:
    response = requests.get(url="http://192.168.137.20:9001/camera/image")
    log.info(f"Response {response}")

    np_arr = np.frombuffer(response.content, np.uint8)
    img = cv.imdecode(np_arr, cv.IMREAD_COLOR)
    log.info(f"Img size {img.shape[:2]}")
    # cv.imwrite("camera_image.png", img)

    result = imgproc.process(img)
    log.info(f"Proc result {result}")
