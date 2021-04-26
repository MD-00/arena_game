import pygame as pg
import setup
import pymunk





screen = pg.display.set_mode((setup.width, setup.height))
pg.display.set_caption(setup.name)
icon = pg.image.load("IMG/icon.png")
pg.display.set_icon(icon)
background = pg.image.load('IMG/background.png')

#defining Bird

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 0
        self.height = self.y

    def jump(self):
        self.vel = -10.5
        self.height = self.y

    # def move(self):


class Pipe:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# game loop
gameOn = True
while gameOn:
    screen.blit(background,(0,0))
    keys_pressed = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT or keys_pressed[pg.K_ESCAPE]:
            gameOn = False


    pg.display.update()