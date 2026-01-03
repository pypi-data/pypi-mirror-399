from src.GameBox import *
import pygame

width, height = 800, 600
win = Game(width, height, "blue", "First Game!")

cam = Cammera()

player = Player((width / 2, 375), (50, 50), "green", True)
player.add_physics(1.0, 3.0, 16, 7.0, 0.5)

floor = Rect((0, height-50), (width, 50), "yellow", True)

rect = Rect((0, 0), (50, 50), "red", True)

cam.set_follow_target(floor)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.platforming_movement()
    floor.move(-0.5, -0.5)

    win.update(60)

pygame.quit()