from dataclasses import dataclass
from math import atan2, sin, cos, isinf, sqrt
from typing import Optional


@dataclass
class Point:
    x: float
    y: float

    def __sub__(self, other: 'Point'):
        return Point(
            self.x - other.x,
            self.y - other.y,
        )


@dataclass
class Line:
    # y = K.x + C, where K is the slope, C is the intercept

    slope: float
    intercept: float

    def f(self, x) -> float:
        return self.slope * x + self.intercept


def distance(pt1: Point, pt2: Point) -> float:
    return sqrt(pow((pt1.x - pt2.x), 2) + pow((pt1.y - pt2.y), 2))


def line(pt1: Point, pt2: Point) -> Line:
    slope = (pt2.y - pt1.y) / (pt2.x - pt1.x)
    return Line(slope, line_intersect(slope, pt1))


def midpoint(point1: Point, point2: Point) -> Point:
    return Point(
        x=(point1.x + point2.x) / 2,
        y=(point1.y + point2.y) / 2,
    )


def intersection(line1: Line, line2: Line) -> Optional[Point]:
    if line1.slope == line2.slope:
        return None

    if isinf(line1.slope):
        x = line1.intercept
        return Point(x, line2.f(x))
    elif isinf(line2.slope):
        x = line2.intercept
        return Point(x, line1.f(x))
    else:
        x = ((line2.intercept - line1.intercept)
             / (line1.slope - line2.slope))
        return Point(x, line1.f(x))


def two_points_90(a: Point, o: Point):
    """
    Determines the pt that is 90 degree away from pt A based on pt O
    """
    return Point(
        (o.x - a.y + o.y),
        (a.x - o.x + o.y),
    )


def line_intersect(slope, pt):
    return pt.y - pt.x * slope if not isinf(slope) else pt.x


def parallel_line(line_: Line, pt: Point):
    return Line(
        line_.slope,
        line_intersect(line_.slope, pt),
    )


def dist_pt_line_intercept(pt: Point, line_: Line):
    """
    Determines the distance from point to line on the X axis
    """

    parallel_line_: Line = parallel_line(line_, pt)
    return parallel_line_.intercept - line_.intercept


def pts_same_side(p1, p2, line_) -> bool:
    """
    Determines whether two points are on the same side against a line
    """
    return (dist_pt_line_intercept(p1, line_) * dist_pt_line_intercept(p2, line_)) > 0


def three_pts_angle(
        a: Point,
        o: Point,
        b: Point,
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
