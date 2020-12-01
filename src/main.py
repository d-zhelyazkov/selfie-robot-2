#!/usr/bin/env python3
import logging as log


import booleans
import reactives
import threads
import cam_srv
from imgproc import image_processor as imgproc
from tools import show_image, draw_points, init_window

log.basicConfig(
    level=log.DEBUG,
    format="[%(asctime)s] [%(name)s] %(message)s",
)

GUI = booleans.env("GUI", False)

if GUI:
    init_window("result")


processed_imgs = reactives.Subject()
processed_imgs.last = (cam_srv.images.last, ([], []))
processed_imgs.subscribe(cam_srv.ParamOptimizer())


def show_result(img, points):
    (blue_points, red_points) = points
    show_image(draw_points(img, blue_points + red_points), "result")


def process():
    img = cam_srv.image()

    result = imgproc.process(img)
    (blue_dots, red_dots) = result
    log.info("Img processed. Found %d blue and %d red points", len(blue_dots), len(red_dots))
    processed_imgs.on_next((img, (blue_dots, red_dots)))


def display():
    processed_imgs.wait_next()
    show_result(*processed_imgs.last)


def main():
    with \
            threads.RepeatingTimer(
                function=process,
                interval=0,
                name="ProcessThread",
            ) as process_thread, \
            threads.RepeatingTimer(
                function=display,
                interval=0,
            ) as display_timer:
        process_thread.start()

        if GUI:
            display_timer.run()

        process_thread.join()


if __name__ == "__main__":
    main()
