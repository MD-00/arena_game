import pygame as pg

pg.font.init()
font = pg.font.SysFont("Arial", 22)
clock = pg.time.Clock()


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render("FPS: " + fps, 1, pg.Color("Black"))
    return fps_text
