import pygame as pg
import setup
import os
import random
import neat

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


def draw_window(window, birds, pipes, score):
    window.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    text = font.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (setup.width - 20 - text.get_width(), 10))

    for bird in birds:
        bird.draw(window)
    pg.display.update()


class Pipe:
    gap = 180
    vel = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.pipe_top = pg.transform.flip(PIPE_IMG, False, True)
        self.pipe_bottom = PIPE_IMG

        self.passed = False
        self.set_height()

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


def fitness_fun(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)


    pipes = [Pipe(700)]

    score = 0

    clock = pg.time.Clock()
    gameOn = True
    while gameOn:
        clock.tick(30)
        keys_pressed = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys_pressed[pg.K_ESCAPE]:
                gameOn = False
                pg.quit()
                quit()
            # if event.type == pg.KEYDOWN:
            #     if event.key == pg.K_w:
            #         bird.jump()
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipe_top.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            # ^^ tą wartość trzeba zmienić

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()
            # mozna zmienic na 0.5


        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    # birds.remove(bird)
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)


                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.pipe_top.get_width() < 0:
                rem.append(pipe)


            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                # można dać 10 fitnessu
                g.fitness += 5

            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= setup.height or bird.y < 0:

                # w razie czego wywalić ten fitness
                ge[x].fitness -= 1
                # birds.remove(bird)
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)



        draw_window(screen, birds, pipes, score)



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(fitness_fun, 200)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neatconfig.txt")
    run(config_path)