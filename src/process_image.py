#!/usr/bin/env python3

import sys
import image_processor as improc


def main():
    image_path = sys.argv[1]

    (blue_points, red_points) = improc.process_image(image_path)

    print_points(blue_points)
    print_points(red_points)


def print_points(points):
    for point in points:
        print("[{},{}]".format(point[0], point[1]), end=' ')
    print(end='\n')


main()
