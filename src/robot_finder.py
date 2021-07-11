import logging
import math
from enum import Enum

from sympy import Point2D, Line2D

import reactives
from geometry import two_points_90, pts_same_side, three_pts_angle, normalize_angle, point, midpoint, intersection

ROBOT_UNIT = 5  # cm
# distance from robot's center (the two wheels' middle point) to it's tail (the red light)

found = reactives.Subject()
not_found = reactives.Subject()


class NotFoundCase(Enum):
    UNDEF = 0
    MANY_POINTS = 1
    FEW_POINTS = 2


def find(processed_img):
    img, points = processed_img
    blue_points, red_points = points
    if (
            len(blue_points) != 2
            or
            len(red_points) != 1
    ):
        return _handle_not_found(blue_points, red_points)

    (height, width, _) = img.shape
    robot = transform(
        wheel1=point(*blue_points[0]),
        wheel2=point(*blue_points[1]),
        tail=point(*red_points[0]),
        scene_center=point(width / 2, height / 2),
    )
    logging.info("Robot FOUND!!!")
    logging.debug("Robot: %s", robot)
    found.on_next(robot)


def transform(
        wheel1: Point2D,
        wheel2: Point2D,
        tail: Point2D,
        scene_center: Point2D,
):
    """
    :return: (
        robot_position, # position against scene center;
        angle, # angle against scene center;
        distance, # distance to scene center;
        )
    """
    robot_center = midpoint(wheel1, wheel2)

    # finds the tail point's prime and its projection line - the main one
    tail_prime = two_points_90(wheel1, robot_center)
    intersection_line = Line2D(wheel1, wheel2)
    if not pts_same_side(tail, tail_prime, intersection_line):
        tail_prime = two_points_90(wheel2, robot_center)
    main_projection_line = Line2D(tail, tail_prime)

    # finds center line's prime
    center_line = Line2D(scene_center, robot_center)
    side_line = Line2D(tail, wheel1)
    side_intersection = intersection(center_line, side_line)
    if side_intersection:
        side_line_prime = Line2D(tail_prime, wheel1)
    else:
        side_line = Line2D(tail, wheel2)
        side_intersection = intersection(center_line, side_line)
        side_line_prime = Line2D(tail_prime, wheel2)

    # noinspection PyTypeChecker
    side_intersection_projection_line: Line2D = main_projection_line.parallel_line(side_intersection)
    side_intersection_prime = intersection(side_line_prime, side_intersection_projection_line)
    center_line_prime = Line2D(robot_center, side_intersection_prime)

    # computes position, angle and distance
    # noinspection PyTypeChecker
    center_line_projection: Line2D = main_projection_line.parallel_line(scene_center)
    center_prime = intersection(center_line_projection, center_line_prime)
    distance = center_prime.distance(robot_center) / robot_center.distance(tail_prime)
    robot_position = robot_center - center_prime
    angle = math.degrees(normalize_angle(
        three_pts_angle(tail_prime, robot_center, center_prime) - math.pi))
    return robot_position, angle, (distance * ROBOT_UNIT)


def _handle_not_found(blue_points, red_points):
    blue_cnt = len(blue_points)
    red_cnt = len(red_points)
    if blue_cnt >= 2 and red_cnt >= 1:
        case = NotFoundCase.MANY_POINTS
    elif blue_cnt <= 2 and red_cnt <= 1:
        case = NotFoundCase.FEW_POINTS
    else:
        case = NotFoundCase.UNDEF
    logging.warning("Robot NOT FOUND... - %s", case)
    not_found.on_next(case)
