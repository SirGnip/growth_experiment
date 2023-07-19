import random
from dataclasses import dataclass
from typing import Sequence

import arcade
import ease
from gnp.arcadelib import actor
import bezier


WIDTH, HEIGHT = 800, 600
CURVE_LIFETIME = 6.0
SEGMENTS = 20
CURVE_COLOR = arcade.color.FOREST_GREEN
BG_COLOR = arcade.color.BLACK
CTRL_POINT_COLOR = (15, 15, 15)

CURVES = """
1.0 7.0 50  50  400 200 200 400 600 550
1.5 2.0 220 163 250 193 312 149 416 183
2.0 2.0 290 265 308 305 176 335 184 435
3.2 2.5 410 445 438 473 468 445 494 467
4.4 2.5 520 514 545 520 520 569 550 577
""".strip()


def text_2_curves(txt):
    entries = []
    for line in txt.strip().split('\n'):
        start, end, *vals = [float(v) for v in line.split()]
        points = []
        for i in range(0, len(vals), 2):
            points.append((vals[i], vals[i+1]))
        entries.append(BezierEntry(start, end, Bezier(*points)))
    return entries


def random_pt():
    return random.randint(0, WIDTH), random.randint(0, HEIGHT)


def invlerp(a, b, v):
    return (v - a) / (b - a)


@dataclass
class Bezier:
    s: arcade.Point
    cp1: arcade.Point
    cp2: arcade.Point
    e: arcade.Point

    @staticmethod
    def random():
        return Bezier(
            random_pt(),
            random_pt(),
            random_pt(),
            random_pt()
        )

    def get_point(self, u: float) -> arcade.Point:
        return bezier.bezier2cp(self.s, self.cp1, self.cp2, self.e, u)

    def get_points(self, u_start: float, u_end: float) -> arcade.PointList:
        points = []
        for i in range(0, SEGMENTS + 1):
            u = arcade.lerp(u_start, u_end, i / SEGMENTS)
            points.append(bezier.bezier2cp(self.s, self.cp1, self.cp2, self.e, u))
        return points


@dataclass
class BezierEntry:
    start: float
    duration: float
    curve: Bezier


class LifetimeActor(actor.Actor):
    def __init__(self, lifetime):
        self.lifetime = lifetime
        self.lifetime_remaining = lifetime

    def get_u(self):
        return (self.lifetime - self.lifetime_remaining) / self.lifetime

    def update(self, delta_time: float):
        self.lifetime_remaining -= delta_time

    def draw(self):
        pass

    def can_reap(self) -> bool:
        return self.lifetime_remaining <= 0.0

    def kill(self):
        self.lifetime_remaining = 0.0


class BezierActor(LifetimeActor):
    def __init__(self, lifetime, curve):
        super().__init__(lifetime)
        self.curve = curve

    def draw(self):
        # debug: control points
        arcade.draw_polygon_outline((self.curve.s, self.curve.cp1, self.curve.cp2, self.curve.e), CTRL_POINT_COLOR, 1)

        # curve
        points = self.curve.get_points(0.0, ease.ease_out_exp(self.get_u(), 2))
        arcade.draw_line_strip(points, CURVE_COLOR, 3)


class MultiBezierActor(LifetimeActor):
    def __init__(self, lifetime, curves: Sequence[BezierEntry]):
        super().__init__(lifetime)
        self.curves = curves
        for c in self.curves:
            print(c)
        self.width = 10

    def draw(self):
        for c in self.curves:
            elapsed = self.lifetime - self.lifetime_remaining
            u = min(1.0, max(0.0, invlerp(c.start, c.start + c.duration, elapsed)))  # clamp
            u = ease.ease_out_exp(u, 4)
            if u > 0.0:
                points = c.curve.get_points(0, u)
                arcade.draw_line_strip(points, CURVE_COLOR, self.width)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(BG_COLOR)
        self.actors = actor.ActorList()
        self.pending_points = []

        curves = text_2_curves(CURVES)
        self.actors.append(MultiBezierActor(15, curves))

    def on_draw(self):
        self.clear()
        self.actors.draw()

    def on_update(self, delta_time):
        self.actors.update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.R:
            self.actors.append(BezierActor(CURVE_LIFETIME, Bezier.random()))
        elif symbol == arcade.key.ESCAPE:
            self.close()

    def on_mouse_press(self, x, y, button, key_modifiers):
        self.pending_points.append((x, y))
        self._create_actor()

    def _create_actor(self):
        if len(self.pending_points) == 4:
            print(' '.join([f'{p[0]} {p[1]}' for p in self.pending_points]))
            a = BezierActor(CURVE_LIFETIME, Bezier(*self.pending_points))
            self.actors.append(a)
            self.pending_points = []


if __name__ == '__main__':
    game = MyGame(WIDTH, HEIGHT, 'Bezier growth')
    print('Click mouse 4 times to create bezier curve. Tap "R" to generate a random curve.')
    arcade.run()
