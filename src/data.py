#!/usr/bin/env python3
import json
import logging
import os
import random
from datetime import datetime
from pathlib import Path

import rx.operators
from rx.scheduler import ThreadPoolScheduler

import cam_srv
import main as main_proc
import reactives
import robot_finder
import threads
from tools import write_img, JSONEncoder, do_random_task

DIR = Path(os.getenv("DATA_DIR", "/mnt/data/robot_imgs/"))
DAY_DIR = DIR / datetime.now().strftime("%y_%m_%d")
DAY_DIR.mkdir(parents=True, exist_ok=True)

ready = reactives.Subject()


def prepare(finding):
    (robot, processed_img) = finding
    img = cam_srv.snapshot()
    time = datetime.now()
    ready.on_next((img, time, (processed_img, robot)))


def save(data):
    try:
        (img, time, data) = data
        file_name = time.strftime("%H_%M_%S")

        write_img(img, DAY_DIR / (file_name + ".jpg"))

        (processed_img, robot) = data
        with (DAY_DIR / (file_name + ".json")).open('w') as fp:
            json.dump(
                {
                    "blue_pts": processed_img.blue_pts,
                    "red_pts": processed_img.red_pts,
                    "robot": robot,
                },
                fp,
                indent=4,
                cls=JSONEncoder,
            )

    except Exception as e:
        logging.fatal("Error while saving data...", exc_info=e)


def movef_random():
    dist = random.randint(-30, 30)
    main_proc.motion.movef(dist)


def turn_random():
    angle = random.randint(-180, 180)
    main_proc.motion.turn(angle)


def move_random(robot: robot_finder.Object):
    if robot.dist < 100:
        do_random_task([
            movef_random,
            turn_random,
        ])
    else:
        main_proc.motion.turn(robot.angle)
        main_proc.motion.movef(robot.dist)


def main():
    data_scheduler = ThreadPoolScheduler(1)

    with \
            cam_srv.exposure, cam_srv.focus, \
            main_proc.motion, \
            threads.RepeatingTimer(
                function=main_proc.process,
                interval=0,
                name="ProcessThread",
            ) as process_thread:
        main_proc.processed_imgs.subscribe(robot_finder.find)
        robot_finder.found.subscribe(prepare)
        ready.pipe(
            rx.operators.observe_on(data_scheduler)
        ).subscribe(save)

        robot_finder.found.subscribe(cam_srv.ParamOptimizer.on_found)
        robot_finder.not_found.subscribe(
            cam_srv.ParamOptimizer.on_not_found)

        robot_finder.found.subscribe(
            on_next=lambda f: move_random(f[0]),
        )

        process_thread.run()


if __name__ == "__main__":
    main()
