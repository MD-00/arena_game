import pygame as pg
import setup
import os
import random
import neat
import fps
import sys
from bird import Bird
from pipe import Pipe

# sys.stdout = open("log.txt", "w")



BASE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "base.png")))
BG_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "background.png")))

pg.font.init()
font = pg.font.SysFont("Arial", 50)

screen = pg.display.set_mode((setup.width, setup.height))
pg.display.set_caption(setup.name)
icon = pg.image.load(os.path.join("IMG", "bird1.png"))
pg.display.set_icon(icon)


# defining Bird




def draw_window(window, birds, pipes, score):
    window.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    text = font.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (setup.width - 20 - text.get_width(), 10))

    for bird in birds:
        bird.draw(window)
    window.blit(fps.update_fps(), (10, 0))
    pg.display.update()

    fps.clock.tick(60)





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
    game_on = True
    while game_on:
        clock.tick(60)
        keys_pressed = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys_pressed[pg.K_ESCAPE]:
                game_on = False
                pg.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipe_top.get_width():
                pipe_ind = 1
        else:
            run = False
            # czy ta zmienna run w ogóle coś robi?
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            # ^^ tą wartość trzeba zmienić

            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
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

            if len(ge):
                print(int(max(x.fitness for x in ge)))
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
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(fitness_fun, 200)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neatconfig.txt")
    run(config_path)
    # sys.stdout.close()
