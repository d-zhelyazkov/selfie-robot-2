#!/usr/bin/env python3
import json
import logging
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Tuple

import rx.operators
from rx.scheduler import ThreadPoolScheduler

import cam_srv
import main as main_proc
import reactives
import robot_finder
import threads
from tools import write_img, JSONEncoder, do_random_task, now_time

DATA_DIR = Path(os.getenv("DATA_DIR", "/mnt/data/robot_imgs/"))
DAY_DIR = DATA_DIR / datetime.now().strftime("%y_%m_%d")
DAY_DIR.mkdir(parents=True, exist_ok=True)

ready_data = reactives.Subject()


def prepare_data(finding):
    (robot, processed_img) = finding
    img = cam_srv.snapshot()
    time = now_time()
    ready_data.on_next((img, time, (processed_img, robot)))

    main_proc.selfies.on_next(img)


def save_data(data):
    try:
        (img, time, data) = data
        file_name = time.strftime("%H_%M_%S")

        write_img(img, DAY_DIR / (file_name + ".jpg"))

        (processed_img, robot) = data
        processed_img: robot_finder.ProcessedImg = processed_img
        write_img(processed_img.img, DAY_DIR / (file_name + "_proc.jpg"))

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


def move(finding: Tuple[robot_finder.Object, robot_finder.ProcessedImg]):
    (robot, processed_img) = finding
    if robot.dist < 100:
        do_random_task([
            movef_random,
            turn_random,
        ])
    else:
        main_proc.motion.turn(robot.angle)
        main_proc.motion.movef(robot.dist)


def back_up():
    main_proc.motion.back()


def on_not_found(case):
    do_random_task([
        lambda: cam_srv.ParamOptimizer.on_not_found(case),
        back_up,
    ])


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
        robot_finder.found.subscribe(prepare_data)
        ready_data.pipe(
            rx.operators.observe_on(data_scheduler)
        ).subscribe(save_data)

        robot_finder.found.subscribe(cam_srv.ParamOptimizer.on_found)
        robot_finder.not_found.subscribe(on_not_found)

        robot_finder.found.subscribe(move)

        process_thread.start()
        main_proc.run_gui()

        process_thread.join()


if __name__ == "__main__":
    main()
