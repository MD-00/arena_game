import pygame as pg
import setup
import os
import fps
import random
import boto3
from bird import Bird
from pipe import Pipe
from argparse import ArgumentParser
from datetime import datetime
import copy
import pickle

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

def get_score(e):
    return e.score

def crossover_and_mutate(birds: tuple, crossover_rate, mutation_rate):
    bird_1 = copy.copy(birds[0])
    bird_2 = copy.copy(birds[1])

    new_bird = Bird(230, 350)

    if random.random() < crossover_rate:
        new_bird.net.weights1 = (bird_1.net.weights1 + bird_2.net.weights1) / 2
        new_bird.net.weights2 = (bird_1.net.weights2 + bird_2.net.weights2) / 2

    else:
        new_bird = random.sample((bird_1, bird_2), 1)[0]

    if random.random() < mutation_rate:
        new_bird = Bird(230, 350)

    return new_bird


def pop_random(lst):
    idx = random.randrange(0, len(lst))
    return lst[idx]

def breed(reproduction_rate, crossover_rate, mutation_rate, population):
    global birds
    parent_birds = sorted(birds, key=get_score, reverse=True)
    birds = []

    birds.append(parent_birds[0])
    birds.append(parent_birds[1])

    children_birds = parent_birds[0:int(reproduction_rate * len(parent_birds))]

    fulfillment = random.sample(children_birds, len(parent_birds)-len(children_birds))
    children_birds = children_birds + fulfillment

    pairs = []
    for x in range(population-2):
        rand_1 = pop_random(children_birds)
        rand_2 = pop_random(children_birds)
        pairs.append((rand_1, rand_2))

    for pair in pairs:
        birds.append(crossover_and_mutate(pair, crossover_rate, mutation_rate))


# def breed_2():
#     global birds
#     children_birds = []
#     parent_birds = sorted(birds, key=get_score, reverse=True)
#     for x in range(4):
#         children_birds.append(parent_birds[0])
#
#     best = crossover_and_mutate([parent_birds[0], parent_birds[1]])
#     children_birds.append(best[0])
#     children_birds.append(best[1])
#
#     for x in range(3):
#         new = crossover_and_mutate(random.sample(parent_birds, 2))
#         children_birds.append(new[0])
#         children_birds.append(new[1])
#
#     children_birds.append(random.sample(parent_birds, 1))
#     children_birds.append(random.sample(parent_birds, 1))
#
#     birds = children_birds


def GA_fun(generation):
    global birds

    pipes = [Pipe(700)]
    score = 0
    clock = pg.time.Clock()
    game_on = True

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
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if (bird.y + bird.img.get_height() >= setup.height or bird.y < 0) and bird.is_alive:
                birds[x].score -= 1
                bird.is_alive = False
                alive_birds-=1

        draw_window(screen, birds, pipes, score)

    max_fitness = max(x.score for x in birds)
    average_fitness = sum(x.score for x in birds) / len(birds)
    f.write(f"{generation}, {max_fitness}, {average_fitness}, {score}\n")
    print(f"Generation: {generation}, max fitness: {max_fitness}, avg fitness: {average_fitness}, score: {score}")

def revive():
    for bird in birds:
        bird.revive(230, 350)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-p",
        "--population",
        type=int,
        default=10,
    )
    parser.add_argument(
        "-r",
        "--reproduction_rate",
        type=float,
        default=0.6,
    )
    parser.add_argument(
        "-c",
        "--crossover_rate",
        type=float,
        default=0.7,
    )
    parser.add_argument(
        "-m",
        "--mutation_rate",
        type=float,
        default=0.1,
    )
    parser.add_argument(
        "-g",
        "--generations",
        type=int,
        default=5,
    )
    parser.add_argument(
        "-a",
        "--access",
        type=str,
    )
    parser.add_argument(
        "-k",
        "--key",
        type=str,
    )

    args = parser.parse_args()

    population = args.population
    reproduction_rate = args.reproduction_rate
    crossover_rate = args.crossover_rate
    mutation_rate = args.mutation_rate
    generations = args.generations
    access = args.access
    key = args.key
    print(f'Population: {population}, reproduction: {reproduction_rate}, crossover: {crossover_rate}, mutation: {mutation_rate}, generations: {generations}')


    for x in range(population):
        birds.append(Bird(230, 350))

    nets = list()
    with open('start-nets.pickle', 'rb') as handle:
        nets = pickle.load(handle)

    for i in range(len(birds)):
        birds[i].net = nets[i]

    f = open("results.txt", "w")
    f.write(f'Population: {population}, reproduction: {reproduction_rate}, crossover: {crossover_rate}, mutation: {mutation_rate}, generations: {generations}\n')
    f.write(f"generation, max_fitness, average_fitness, score\n")
    for generation in range(generations):
        GA_fun(generation)
        breed(reproduction_rate, crossover_rate, mutation_rate, population)
        revive()

    f.close()

    with open('save-data.pickle', 'wb') as handle:
        pickle.dump(nets, handle, protocol=pickle.HIGHEST_PROTOCOL)

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-H%H-M%M-S%S")

    s3=boto3.client('s3', aws_access_key_id=access, aws_secret_access_key=key, region_name="us-east-1")
    # s3.upload_file(
    #     Filename="results.txt",
    #     Bucket="ag-data-flappy-bird",
    #     Key=f'results/p{population}-r{int(reproduction_rate*100)}-c{int(crossover_rate*100)}-m{int(mutation_rate*100)}-g{generations}.txt',
    # )
    # s3.upload_file(
    #     Filename="save-data.pickle",
    #     Bucket="ag-data-flappy-bird",
    #     Key=f'pickles/p{population}-r{int(reproduction_rate*100)}-c{int(crossover_rate*100)}-m{int(mutation_rate*100)}-g{generations}.pickle',
    # )
