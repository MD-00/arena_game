import pygame as pg
import setup
import os
import neat
import fps
from bird import Bird
from pipe import Pipe

#odkomentowac, zeby dzialalo na serwerze
# os.environ["SDL_VIDEODRIVER"] = "dummy"


highest = 0

BASE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "base.png")))
BG_IMG = pg.transform.scale2x(pg.image.load(os.path.join("IMG", "background.png")))

pg.font.init()
font = pg.font.SysFont("Arial", 50)

screen = pg.display.set_mode((setup.width, setup.height))
pg.display.set_caption(setup.name)
icon = pg.image.load(os.path.join("IMG", "bird1.png"))
pg.display.set_icon(icon)

#draw_window - funkcja odpowiadająca za wyświetlanie grafiki
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
            plik = open("log.txt", "at")
            plik.write(f"{score} ")

            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
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
            global highest
            score += 1
            if score > highest:
                highest = score
            for g in ge:
                g.fitness += 5

            if len(ge):
                varx = int(max(x.fitness for x in ge))
                print(f"Score: {score} fitness: {varx} highest score: {highest} ")
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= setup.height or bird.y < 0:
                ge[x].fitness -= 1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(screen, birds, pipes, score)

#run - główna pętla programu
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(fitness_fun, 5000)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    xd = open("log.txt", "wt")
    xd.write("")
    xd.close()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neatconfig.txt")
    run(config_path)



