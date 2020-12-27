#!/usr/bin/env python3
import sys
from pathlib import Path

import cv2.cv2 as cv

import image_processor
from image_processor import are_robot_points

images_path = Path(sys.argv[1])
images = list(images_path.rglob("*"))
print(f"Got {len(images)} images.")

image_points = list(map(
    lambda image: image_processor.process(cv.imread(str(image), cv.IMREAD_COLOR)),
    images,
))

robot_points = list(filter(
    lambda points: are_robot_points(*points),
    image_points,
))
print(f"Robot found in {len(robot_points)} out of {len(images)} images.")
print(f"{len(robot_points) / len(images):.2f} success rate.")
