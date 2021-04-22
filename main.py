import pygame as pg
import setup
import pymunk





screen = pg.display.set_mode((setup.width, setup.height))
pg.display.set_caption(setup.name)
icon = pg.image.load("IMG/icon.png")
pg.display.set_icon(icon)
background = pg.image.load('IMG/background.png')

#defining space using pymunk

space = pymunk.Space()
space.gravity = 0, -1000

body = pymunk.Body(1, 1666)
body.position = 50, 100

poly = pymunk.Poly.create_box(body)
space.add(body, poly)



# game loop
gameOn = True
while gameOn:
    screen.blit(background,(0,0))
    keys_pressed = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT or keys_pressed[pg.K_ESCAPE]:
            gameOn = False

    space.step(0.02)

    pg.display.update()