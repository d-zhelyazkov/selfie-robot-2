from math import atan2, sin, cos, isinf
from numbers import Number
from typing import Optional, Callable

from sympy import Point2D, Line2D


def point(x, y) -> Point2D:
    return Point2D(
        x, y,
        evaluate=False,
    )


def midpoint(point1: Point2D, point2: Point2D) -> Point2D:
    return point(
        x=(point1.x + point2.x) / 2,
        y=(point1.y + point2.y) / 2,
    )


def intersection(line1: Line2D, line2: Line2D) -> Optional[Point2D]:
    # intersection_ = line1.intersection(line2)
    # return intersection_[0] if intersection_ \
    #     else None

    if line1.slope == line2.slope:
        return None

    if isinf(line1.slope):
        x = line_intercept(line1)
        return point(x, line_func(line2)(x))
    elif isinf(line2.slope):
        x = line_intercept(line2)
        return point(x, line_func(line1)(x))
    else:
        x = ((line_intercept(line2) - line_intercept(line1))
             / (line1.slope - line2.slope))
        return point(x, line_func(line1)(x))


def two_points_90(a: Point2D, o: Point2D):
    """
    Determines the pt that is 90 degree away from pt A based on pt O
    """
    return point(
        (o.x - a.y + o.y),
        (a.x - o.x + o.y),
    )


def dist_pt_line_intercept(pt: Point2D, line: Line2D):
    """
    Determines the distance from point to line on the X axis
    """

    # noinspection PyTypeChecker
    parallel_line: Line2D = line.parallel_line(pt)
    return line_intercept(parallel_line) - line_intercept(line)


def pts_same_side(p1, p2, line) -> bool:
    """
    Determines whether two points are on the same side against a line
    """
    return (dist_pt_line_intercept(p1, line) * dist_pt_line_intercept(p2, line)) > 0


def line_intercept(line: Line2D) -> float:
    a, b, c = line.coefficients
    # ax + by + c = 0
    # y = K.x + C, where K is the slope, C is the intercept

    return -c / b


def line_func(line: Line2D) -> Callable[[Number], Number]:
    a, b, c = line.coefficients
    # ax + by + c = 0
    # y = -(a/b)x - (c/b)
    return lambda x: -(a / b) * x - (c / b)


def three_pts_angle(
        a: Point2D,
        o: Point2D,
        b: Point2D,
):
    """
    :return: in radians
    """
    return atan2(a.y - o.y, a.x - o.x) - atan2(b.y - o.y, b.x - o.x)


def normalize_angle(angle):
    """
    :param angle: in radians
    """
    return atan2(sin(angle), cos(angle))
