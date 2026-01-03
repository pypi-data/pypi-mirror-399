from src.GameBox import *
import pygame

width, height = 1400, 800
game = Game(width, height, (124, 204, 201))

cam = Cammera()

player = Player((width / 2, 500), (50, 50), (0, 255, 0), True)

player.add_physics(1.0, 3.0, 16, 7.0, 0.5)

rect = Rect((0, 700), (width*20, 100), (255, 0, 0), True)
      
cam.set_follow_target(player)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.platforming_movement()

    game.update()
    


pygame.quit()
quit()