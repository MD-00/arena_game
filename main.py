import pygame as pg
import setup

screen = pg.display.set_mode((setup.width, setup.height))
pg.display.set_caption(setup.name)
icon = pg.image.load("IMG/icon.png")
pg.display.set_icon(icon)
# background = pg.image.load('IMG/background.jpg')


# game loop
gameOn = True
while gameOn:
    # screen.blit(background,(0,0))
    keys_pressed = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT or keys_pressed[pg.K_ESCAPE]:
            gameOn = False
    pg.display.update()