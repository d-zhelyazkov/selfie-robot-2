#!/usr/bin/env python3
import logging as log

import numpy as np

import booleans
import cam_srv
import imgproc.config
import reactives
import robot_finder
import threads
from imgproc import image_processor as imgproc
from motion import Motion, NullMotion
from tools import show_image, draw_points, init_window

log.basicConfig(
    level=log.DEBUG,
    format="[%(asctime)s] [%(name)s] %(message)s",
)

GUI = booleans.env("GUI", False)

if GUI:
    init_window("result")
    init_window("selfie")

imgproc.config.debug = False

processed_imgs = reactives.Subject((np.ndarray(()), ([], [])))
selfies = reactives.Subject(np.ndarray(()))


def show_result(img, points):
    (blue_points, red_points) = points
    show_image(draw_points(img, blue_points + red_points), "result")


def process():
    img = cam_srv.image()

    result = imgproc.process(img)
    processed_imgs.on_next((img, result))


def display():
    processed_imgs.wait_next()
    show_result(*processed_imgs.last)
    show_image(selfies.last, "selfie")


motion = Motion() if booleans.env("MOTION", True) else NullMotion()


def position(robot):
    robot_position, angle, distance = robot
    if distance < 5:
        log.info("I AM AT THE CENTER!!!")

        log.info(f"Taking a selfie...")
        selfie = cam_srv.snapshot()
        log.info(f"Selfie taken!")
        selfies.on_next(selfie)

    # ToDo: rotate max 90 deg
    if not (-20 < angle < 20):
        motion.turn(angle)
    else:
        motion.movef(min(distance, 30))


def main():
    with \
            cam_srv.exposure, cam_srv.focus, \
            motion, \
            threads.RepeatingTimer(
                function=process,
                interval=0,
                name="ProcessThread",
            ) as process_thread:
        processed_imgs.subscribe(robot_finder.find)
        robot_finder.found.subscribe(position)
        robot_finder.found.subscribe(cam_srv.ParamOptimizer.on_found)
        robot_finder.not_found.subscribe(
            cam_srv.ParamOptimizer.on_not_found)

        process_thread.start()

        if GUI:
            display_timer = threads.RepeatingTimer(
                function=display,
                interval=0,
            )
            display_timer.run()
        # process_thread.run()

        process_thread.join()


if __name__ == "__main__":
    main()
