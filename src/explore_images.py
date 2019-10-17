#!/usr/bin/env python3

import os
import sys
import os.path as path
import image_processor as improc
import cv2
import config

images_path = sys.argv[1]
image_files = [path.join(images_path, file)
               for file in os.listdir(images_path)
               if path.isfile(path.join(images_path, file))]
image_count = len(image_files)
print(image_files)

config.debug = True

i = 0
while True:
    i %= image_count
    image_file = image_files[i]
    improc.process_image(image_file)

    key = cv2.waitKey()
    print("Key pressed: {}".format(key))
    if key == 81 or key == 8:
        # left arrow or backspace
        i -= 1
    elif key == 27:
        # ESC
        cv2.destroyAllWindows()
        break
    else:
        i += 1
