import math

class Fruit:
    def __init__(self, x, y, vx, vy, gravity, radius=28, kind="fruit"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.radius = radius
        self.kind = kind  # "fruit" or "bomb"
        self.sliced = False

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def contains_point(self, x, y):
        # NOTE: only checks a single point against the fruit's circle.
        # A fast mouse swipe generates MOUSEMOTION events that can jump
        # from well outside the fruit to well past it between two
        # consecutive frames, so the fruit is never actually "touched"
        # by any single reported point even though the swipe visually
        # passed right through it. See Task 1 in the README.
        return math.hypot(self.x - x, self.y - y) <= self.radius

    def off_screen(self, height):
        return self.y - self.radius > height
