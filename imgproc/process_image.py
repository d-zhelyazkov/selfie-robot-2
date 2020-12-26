#!/usr/bin/env python3

import sys

import cv2.cv2 as cv

import image_processor


def main():
    image_file = sys.argv[1]

    img = cv.imread(image_file, cv.IMREAD_COLOR)

    (blue_points, red_points) = image_processor.process(img)

    output_points(blue_points)
    output_points(red_points)


def output_points(points):
    for point in points:
        print("[{},{}]".format(point[0], point[1]), end=' ')
    print(end='\n')


main()
