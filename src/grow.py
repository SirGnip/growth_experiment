from dataclasses import dataclass
import arcade
import ease
from gnp.arcadelib import actor
import bezier

SEGMENTS = 20
CURVE_COLOR = arcade.color.FOREST_GREEN
BG_COLOR = arcade.color.BLACK
CTRL_POINT_COLOR = (20, 20, 20)

@dataclass
class Bezier:
    s: arcade.Point
    cp1: arcade.Point
    cp2: arcade.Point
    e: arcade.Point

    def get_point(self, u: float) -> arcade.Point:
        return bezier.bezier2cp(self.s, self.cp1, self.cp2, self.e, u)

    def get_points(self, u_start: float, u_end: float) -> arcade.PointList:
        points = []
        for i in range(0, SEGMENTS + 1):
            u = arcade.lerp(u_start, u_end, i / SEGMENTS)
            points.append(bezier.bezier2cp(self.s, self.cp1, self.cp2, self.e, u))
        return points


class LifetimeActor(actor.Actor):
    def __init__(self, lifetime):
        self.lifetime_remaining = lifetime

    def update(self, delta_time: float):
        self.lifetime_remaining -= delta_time

    def draw(self):
        pass

    def can_reap(self) -> bool:
        return self.lifetime_remaining <= 0.0

    def kill(self):
        self.lifetime_remaining = 0.0


class BezierActor(LifetimeActor):
    def __init__(self, lifetime, points):
        assert len(points) == 4
        super().__init__(lifetime)
        self.curve = Bezier(*points)
        self.u = 0.0

    def draw(self):
        arcade.draw_polygon_outline((self.curve.s, self.curve.cp1, self.curve.cp2, self.curve.e), CTRL_POINT_COLOR, 1)

        points = self.curve.get_points(0.0, ease.ease_out_exp(self.u, 4))
        arcade.draw_line_strip(points, CURVE_COLOR, 3)

        self.u = min(1.0, self.u + 0.005)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(BG_COLOR)
        self.actors = actor.ActorList()
        self.pending_points = [
            (100, 100),
            (200, 500),
            (400, 0),
            (500, 100)
        ]
        self._create_actor()

    def on_draw(self):
        self.clear()
        self.actors.draw()

    def on_update(self, delta_time):
        self.actors.update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.close()

    def on_mouse_press(self, x, y, button, key_modifiers):
        self.pending_points.append((x, y))
        self._create_actor()

    def _create_actor(self):
        if len(self.pending_points) == 4:
            a = BezierActor(6.0, self.pending_points)
            self.actors.append(a)
            self.pending_points = []


if __name__ == '__main__':
    game = MyGame(800, 600, 'Bezier growth')
    print('click mouse 4 times to create bezier curve')
    arcade.run()



