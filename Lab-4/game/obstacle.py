import pygame

class Obstacle:
    def __init__(self, x, ground_y, width=25, height=40):
        self.x = float(x)
        self.prev_x = self.x
        self.width = width
        self.height = height
        self.y = float(ground_y - height)
        self.scored = False

    def move(self, speed):
        self.prev_x = self.x
        self.x -= speed

    def off_screen(self):
        return self.x + self.width < 0

    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def swept_rect(self):
        """Rect covering every position this obstacle occupied during the last move()."""
        left = round(self.x)
        right = round(self.prev_x) + self.width
        return pygame.Rect(left, round(self.y), right - left, self.height)
