#!/usr/bin/env python3

import logging as log
import time

from motion import Motion

log.basicConfig(
    level=log.DEBUG,
    format="[%(asctime)s] [%(name)s] %(message)s",
)


def main():
    with Motion() as motion:
        while True:
            motion.turn(90)
            time.sleep(1)


if __name__ == '__main__':
    main()
