#!/usr/bin/env python3
import cam_srv
from imgproc import image_processor as imgproc

imgproc.config.debug = True


def main():
    while True:
        img = cam_srv.image()
        imgproc.process(img)


if __name__ == "__main__":
    main()
