#!/usr/bin/env python3

import os
import sys
import os.path as path
import image_processor as improc
import cv2.cv2 as cv
import _config

images_path = sys.argv[1]
image_files = [path.join(images_path, file)
               for file in os.listdir(images_path)
               if path.isfile(path.join(images_path, file))]
image_count = len(image_files)
print(image_files)

_config.debug = True

i = 0
while True:
    i %= image_count
    image_file = image_files[i]
    print(image_file)

    img = cv.imread(image_file, cv.IMREAD_COLOR)
    (blue_points, red_points) = improc.process(img)
    print("BLUE points: " + str(blue_points))
    print("RED points: " + str(red_points))

    key = cv.waitKey()
    print("Key pressed: {}".format(key))
    if key == 81 or key == 8:
        # left arrow or backspace
        i -= 1
    elif key == 27:
        # ESC
        cv.destroyAllWindows()
        break
    else:
        i += 1
