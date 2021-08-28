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

PROC_WIN = "processing"
SNAP_WIN = "selfie"

GUI = booleans.env("GUI", False)

if GUI:
    init_window(PROC_WIN)
    init_window(SNAP_WIN)

imgproc.config.debug = False

processed_imgs = reactives.Subject((np.ndarray(()), ([], [])))
selfies = reactives.Subject(np.ndarray(()))


def show_result(processed_img: robot_finder.ProcessedImg):
    show_image(
        img=draw_points(
            processed_img.img,
            processed_img.blue_pts + processed_img.red_pts
        ),
        win_name=PROC_WIN,
    )


def process():
    img = cam_srv.image()

    result = imgproc.process(img)
    processed_imgs.on_next(robot_finder.ProcessedImg(img, *result))


def display():
    processed_imgs.wait_next()
    show_result(processed_imgs.last)
    show_image(selfies.last, SNAP_WIN)


motion = Motion() if booleans.env("MOTION", True) else NullMotion()


def position(robot: robot_finder.Object):
    if robot.dist < 5:
        log.info("I AM AT THE CENTER!!!")

        log.info(f"Taking a selfie...")
        selfie = cam_srv.snapshot()
        log.info(f"Selfie taken!")
        selfies.on_next(selfie)

    # ToDo: rotate max 90 deg
    if not (-20 < robot.angle < 20):
        motion.turn(robot.angle)
    else:
        motion.movef(min(robot.dist, 30))


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
        robot_finder.found.subscribe(on_next=lambda f: position(f[0]))
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
