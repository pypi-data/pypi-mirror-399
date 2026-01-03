import pygame
import numpy as np

from ..basics._net import Global

class Rect:
    def __init__(self, pos: tuple, size: tuple, color: tuple = (0, 0, 0), collision: bool = True):
        self.x, self.y = pos
        self.width, self.height = size
        self.color = color
        Global.game.objs.append(self)
        self.collision = collision

    def update(self):
        rect = pygame.Rect(self.x - Global.cam.x
                           , self.y - Global.cam.y
                           , self.width, self.height)
        if self.collision: Global.collisions.append(rect)
        pygame.draw.rect(Global.screen, self.color, rect)

    def move(self, x, y):
        self.x += x
        self.y += y
