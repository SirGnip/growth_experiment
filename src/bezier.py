"""Foundational Bezier code"""


def bezier2cp(start, p1, p2, end, t) -> tuple:
    x = (1 - t)**3 * start[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * end[0]
    y = (1 - t)**3 * start[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * end[1]
    return x, y
