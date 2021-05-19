import pygame as pg
import os

BIRD_IMGS = [pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird1.png"))),
             pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird2.png"))),
             pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird3.png")))]

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
        d = self.vel * self.tick_count + 2 * self.tick_count ** 2

        if d >= 11:
            d = (d / abs(d)) * 11

        if d < 0:
            d -= 5

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
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
    surf.blit(rotated_image, new_rect.topleft)