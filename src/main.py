#!/usr/bin/env python3
import logging as log

import booleans
import cam_srv
import imgproc.config
import reactives
import robot_finder
import threads
from imgproc import image_processor as imgproc
from motion import Motion
from tools import show_image, draw_points, init_window

log.basicConfig(
    level=log.DEBUG,
    format="[%(asctime)s] [%(name)s] %(message)s",
)

GUI = booleans.env("GUI", False)

if GUI:
    init_window("result")

imgproc.config.debug = False


processed_imgs = reactives.Subject()
processed_imgs.last = (cam_srv.images.last, ([], []))


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


motion = Motion()


def position(robot):
    robot_position, angle, distance = robot
    if distance < 5:
        log.info("I AM AT THE CENTER!!!")
        return

    # ToDo: rotate max 90 deg
    if not (-20 < angle < 20):
        motion.turn(angle)
    else:
        motion.movef(min(distance, 30))


def main():
    with \
            threads.RepeatingTimer(
                function=process,
                interval=0,
                name="ProcessThread",
            ) as process_thread, \
            motion, \
            cam_srv.ParamOptimizer() as param_optimizer:
        processed_imgs.subscribe(robot_finder.find)
        robot_finder.found.subscribe(position)
        robot_finder.not_found.subscribe(param_optimizer)

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
