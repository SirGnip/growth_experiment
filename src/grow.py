import arcade
from gnp.arcadelib import actor


def bezier2cp(start, p1, p2, end, t):
    x = (1 - t)**3 * start[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * end[0]
    y = (1 - t)**3 * start[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * end[1]
    return x, y


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
    def __init__(self, lifetime):
        super().__init__(lifetime)
        self.start = (100, 100)
        self.cp1 = (200, 500)
        self.cp2 = (400, 0)
        self.end = (500, 100)
        self.point_count = 10
        self.points = []

    def gen_points(self):
        self.points = [bezier2cp(self.start, self.cp1, self.cp2, self.end, t / self.point_count) for t in range(self.point_count + 1)]

    def draw(self):
        self.gen_points()
        arcade.draw_polygon_outline((self.start, self.cp1, self.cp2, self.end), arcade.color.DARK_SLATE_GRAY, 1)
        arcade.draw_line_strip(self.points, arcade.color.GREEN, 3)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        self.actors = actor.ActorList()
        self.actors.append(BezierActor(4.0))

    def on_draw(self):
        self.clear()
        self.actors.draw()

    def on_update(self, delta_time):
        self.actors.update(delta_time)


if __name__ == '__main__':
    game = MyGame(600, 600, 'Bezier growth')
    arcade.run()



