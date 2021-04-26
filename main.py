import pygame as pg
import setup
import os

BIRD_IMGS = [pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird1.png"))),
             pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird2.png"))),
             pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird3.png")))]
PIPE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "pipe.png")))
BASE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "base.png")))
BG_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "background.png")))

screen = pg.display.set_mode((setup.width, setup.height))
pg.display.set_caption(setup.name)
icon = pg.image.load(os.path.join("IMG", "bird1.png"))
pg.display.set_icon(icon)


# defining Bird

class Bird:
    IMGS = BIRD_IMGS
    max_rotation = 25
    rot_vel = 20
    animation_time = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.tick_count = 0

    def jump(self):
        self.vel = -13
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count + 3 * self.tick_count ** 2

        if d >= 11:
            d = (d/abs(d)) * 11

        if d < 0:
            d -= 4

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
        else:
            if self.tilt > -60:
                self.tilt -= self.rot_vel

    def draw(self, window):
        self.img_count += 1

        if self.img_count <= self.animation_time:
            self.img = self.IMGS[0]
        elif self.img_count <= self.animation_time * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.animation_time * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.animation_time * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.animation_time * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -60:
            self.img = self.IMGS[1]
            self.img_count = self.animation_time * 2

        blitRotateCenter(window, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pg.mask.from_surface(self.img)

def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

def draw_window(window, bird):
    window.blit(BG_IMG, (0, 0))
    bird.draw(window)
    pg.display.update()


def main():
    bird = Bird(100, 100)
    clock = pg.time.Clock()
    gameOn = True
    while gameOn:
        clock.tick(30)
        keys_pressed = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys_pressed[pg.K_ESCAPE]:
                gameOn = False

        draw_window(screen, bird)

        bird.move()
        if keys_pressed[pg.K_w]:
            bird.jump()
    pg.quit()
    quit()


main()
