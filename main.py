import pygame as pg
import setup
import os
import neat
import fps
import random
from bird import Bird
from pipe import Pipe
from numba import jit, cuda
import copy

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

birds = []


#draw_window - funkcja odpowiadająca za wyświetlanie grafiki
# @jit(target_backend='cuda')
def draw_window(window, birds, pipes, score):
    window.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    text = font.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (setup.width - 20 - text.get_width(), 10))

    for bird in birds:
        if bird.is_alive:
            bird.draw(window)
    window.blit(fps.update_fps(), (10, 0))
    pg.display.update()

    fps.clock.tick(140)

# @jit(target_backend='cuda')
def get_score(e):
    return e.score

# @jit(target_backend='cuda')
def crossover(birds: tuple):
    bird_1 = copy.copy(birds[0])
    bird_2 = copy.copy(birds[1])

    # bird_2 = birds[1].deepcopy()

    if random.random() < 0.5:
        bird_1.net.weights1, bird_2.net.weights1 = bird_2.net.weights1, bird_1.net.weights1
    # else:
    #     bird_1.net.weights2, bird_2.net.weights2 = bird_2.net.weights2, bird_1.net.weights2

    return bird_1, bird_2

# @jit(target_backend='cuda')
def mutation(bird_1):
    pass

# @jit(target_backend='cuda')
def pop_random(lst):
    idx = random.randrange(0, len(lst))
    return lst.pop(idx)

# @jit(target_backend='cuda')
def breed(reproduction_rate, crossover_rate, mutation_rate):
    global birds
    parent_birds = sorted(birds, key=get_score, reverse=True)
    children_birds = parent_birds[0:int(reproduction_rate * len(parent_birds))]


    print(len(parent_birds))
    print(len(children_birds))
    fulfillment = random.sample(children_birds, len(parent_birds)-len(children_birds))
    children_birds = children_birds + fulfillment
    pairs = []

    while children_birds:
        rand_1 = pop_random(children_birds)
        rand_2 = pop_random(children_birds)
        pairs.append((rand_1, rand_2))

    print(len(pairs))
    print(len(set(pairs)))

    birds = []
    for pair in pairs:
        pair = crossover(pair)
        birds.append(pair[0])
        birds.append(pair[1])

    # print(f'XD!: {len(birds)}')

    # for x, bird in enumerate(children_birds):
    #     if random.random() < crossover_rate:
    #         crossover(random.sample(children_birds, 2))
    #
    #     if random.random() < mutation_rate:
    #         pass

def breed_2():
    global birds
    children_birds = []
    parent_birds = sorted(birds, key=get_score, reverse=True)
    for x in range(4):
        children_birds.append(parent_birds[0])

    best = crossover([parent_birds[0], parent_birds[1]])
    children_birds.append(best[0])
    children_birds.append(best[1])

    for x in range(3):
        new = crossover(random.sample(parent_birds, 2))
        children_birds.append(new[0])
        children_birds.append(new[1])

    children_birds.append(random.sample(parent_birds, 1))
    children_birds.append(random.sample(parent_birds, 1))

    # children_birds.append(Bird)
    # children_birds.append(Bird)
    print(f'lenght children birds: {len(children_birds)}')
    birds = children_birds





# @jit(target_backend='cuda')
def GA_fun(bird_population):
    global birds
    # birds = []


    pipes = [Pipe(700)]
    score = 0
    clock = pg.time.Clock()
    game_on = True
    # alive_birds = bird_population
    while game_on:

        alive_birds = any([bird.is_alive for bird in birds])
        clock.tick(60)
        keys_pressed = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys_pressed[pg.K_ESCAPE]:
                game_on = False
                pg.quit()
                quit()

        pipe_ind = 0
        if alive_birds:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipe_top.get_width():
                pipe_ind = 1
        else:
            # plik = open("log.txt", "at")
            # plik.write(f"{score} ")

            break

        for x, bird in enumerate(birds):
            if bird.is_alive:
                bird.move()
                birds[x].score += 0.1
                output = bird.net.eval(abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))

                if output > 0.5:
                    bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird) and bird.is_alive:
                    birds[x].score -= 1
                    bird.is_alive = False
                    alive_birds -= 1
                    # birds.pop(x)
                    # nets.pop(x)
                    # ge.pop(x)

                if not pipe.passed and pipe.x < bird.x and bird.is_alive:
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
            for bird in birds:
                if bird.is_alive:
                    bird.score += 5

            if alive_birds:
                varx = int(max(x.score for x in birds))
                print(f"Score: {score} fitness: {varx} highest score: {highest} ")
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if (bird.y + bird.img.get_height() >= setup.height or bird.y < 0) and bird.is_alive:
                birds[x].score -= 1
                bird.is_alive = False
                alive_birds-=1
                # birds.pop(x)
                # nets.pop(x)
                # ge.pop(x)


        draw_window(screen, birds, pipes, score)
        # print(f'alive birds: {alive_birds}')
        # return birds

# @jit(target_backend='cuda')
def revive():
    for bird in birds:
        # print(bird)
        bird.revive(230, 350)


#run - główna pętla programu
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # winner = population.run(fitness_fun, 5000)
    # print('\nBest genome:\n{!s}'.format(winner))



if __name__ == "__main__":
    xd = open("log.txt", "wt")
    xd.write("")
    xd.close()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neatconfig.txt")


    #init
    population = 10
    reproduction_rate = 0.6
    crossover_rate = 0.7
    mutation_rate = 0.1


    for x in range(population):
        birds.append(Bird(230, 350))
    while True:
        GA_fun(population)
        # for bird in birds:
        #     print(f'--- new ptak ---')
        #     bird.net.display()
        breed(reproduction_rate, crossover_rate, mutation_rate)
        # breed_2()
        revive()
        print(f'--- new generation ---')


    # po kazdej generacji musi byc mutacja i crossover
    # i musi być zerowany score
    # i flaga is_alive na True


