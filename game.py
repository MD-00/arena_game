import pygame as pg
import setup
import os
import random


BIRD_IMGS = [pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird1.png"))),
             pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird2.png"))),
             pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird3.png")))]

PIPE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "pipe.png")))
BASE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "base.png")))
BG_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "background.png")))

pg.font.init()
font = pg.font.SysFont("Arial", 50)




screen = pg.display.set_mode((setup.width, setup.height))
pg.display.set_caption(setup.name)
icon = pg.image.load(os.path.join("IMG", "bird1.png"))
pg.display.set_icon(icon)


# defining Bird
class Bird:

    max_rotation = 25
    rot_vel = 20
    animation_time = 5

    def __init__(self, x, y, color = 'y'):
        self.IMGS = self.change_bird_color(color)
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.tick_count = 0

    def change_bird_color(self, color='y'):
        if color == 'y':
            return [pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird1.png"))),
                    pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird2.png"))),
                    pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bird3.png")))]
        elif color == 'b':
            return [pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bluebird1.png"))),
                    pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bluebird2.png"))),
                    pg.transform.scale2x(pg.image.load(os.path.join("IMG", "bluebird3.png")))]
        elif color == 'r':
            return [pg.transform.scale2x(pg.image.load(os.path.join("IMG", "redbird1.png"))),
                    pg.transform.scale2x(pg.image.load(os.path.join("IMG", "redbird2.png"))),
                    pg.transform.scale2x(pg.image.load(os.path.join("IMG", "redbird3.png")))]

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


def draw_window(window, bird, pipes, score):
    window.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    text = font.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (setup.width - 20 - text.get_width(), 10))
    if pipe.collide(bird):
        text2 = font.render("Przegrałeś z: " + str(score) + "pkt", 1, (255, 255, 255))
        window.blit(text2, (setup.width/2 - text2.get_width()/2, setup.height/2))
        bird.draw(window)
        pg.display.update()
        pg.time.delay(2000)
    else:
        bird.draw(window)
        pg.display.update()

class Pipe:
    gap = 225

    vel = 5

    def __init__(self, x, color='y'):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.pipe_top = pg.transform.flip(PIPE_IMG, False, True)
        self.pipe_bottom = PIPE_IMG
        self.passed = False
        self.set_height()
        self.color = color

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.pipe_top.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.vel

    def draw(self, window):
        window.blit(self.pipe_top, (self.x, self.top))
        window.blit(self.pipe_bottom, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pg.mask.from_surface(self.pipe_top)
        bottom_mask = pg.mask.from_surface(self.pipe_bottom)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False

def game(color):
    bird = Bird(230, 350,color)
    pipes = [Pipe(700,color)]

    score = 0

    clock = pg.time.Clock()
    gameOn = True
    while gameOn:
        if color == 'r':
            clock.tick(35)
        else:
            clock.tick(30)
        keys_pressed = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys_pressed[pg.K_ESCAPE]:
                gameOn = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    bird.jump()
            if event.type == pg.MOUSEBUTTONDOWN:
                bird.jump()
        draw_window(screen, bird, pipes, score)

        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird):
                # pass
                gameOn = False

            if pipe.x + pipe.pipe_top.get_width() < 0:
                rem.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()
        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= setup.height:
            pass
            # gameOn=False
        bird.move()

