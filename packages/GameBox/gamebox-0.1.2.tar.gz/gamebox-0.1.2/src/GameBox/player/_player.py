import pygame
import numpy as np

from ..basics._net import Global

from ..player._playerPhysics import _playerPhysics

class Player:
    def __init__(self, pos: tuple, size: tuple, color: tuple = (0, 0, 0), gravity: bool = False):
        self.x, self.y = pos
        self.screenPos = pos
        self.dim = size
        self.color = color

        self.gravity = gravity
        
        Global.game.objs.append(self)
        Global.player.pos = pos


    def add_physics(self, speed: float = 1.0, gravity: float = 0.0, jump: float = 10.0, maxV: float = 10.0, airRes: float = 0.2):
        self.physics = _playerPhysics(self, speed, gravity, jump, maxV, airRes)

    def update(self):
        self.physics.update()
        #debug rect
        rect = pygame.Rect(self.x, self.y, self.dim[0], self.dim[1])
        pygame.draw.rect(Global.screen, self.color, rect)

    #movement
    def top_down_movement(self):
        self.physics.top_down_movement()

    def platforming_movement(self):
        self.physics.platforming_movement()
