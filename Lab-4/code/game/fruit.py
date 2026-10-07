import math

class Fruit:
    def __init__(self, x, y, vx, vy, gravity, radius=28, kind="fruit",
                 color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.radius = radius
        self.kind = kind  # "fruit" or "bomb"
        self.color = color
        self.sliced = False

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def contains_point(self, x, y):
        return math.hypot(self.x - x, self.y - y) <= self.radius

    def intersects_segment(self, x1, y1, x2, y2):
        # A reported mouse position is only a sample of where the blade was at
        # one instant. Testing the whole segment the blade swept between two
        # samples is what makes a fast swipe register: the two endpoints can sit
        # either side of the fruit with neither one inside the circle, yet the
        # line between them still cuts through it.
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return self.contains_point(x1, y1)

        # Closest point on the segment to the centre: project the centre onto
        # the line, then clamp to the segment so a fruit beyond either end
        # isn't counted as hit.
        t = ((self.x - x1) * dx + (self.y - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        return math.hypot(self.x - (x1 + t * dx), self.y - (y1 + t * dy)) <= self.radius

    def off_screen(self, height):
        return self.y - self.radius > height
