import pygame
import os
import game
import setup
pygame.init()
screen = pygame.display.set_mode((500, 800))
menu_font = pygame.font.Font(None, 40)

class Option:
    hovered = False

    def __init__(self, text, pos):

        self.text = text
        self.pos = pos
        self.set_rect()
        self.save_options = []
        self.draw()

    def draw(self):
        self.set_rend()
        screen.blit(self.rend, self.rect)

    def set_rend(self):
        self.rend = menu_font.render(self.text, True, self.get_color())

    def get_color(self):
        if self.hovered:
            return (255, 255, 255)
        else:
            return (100, 100, 100)

    def do_something(self):
        global options
        global sub_menu
        if 'PLAY' in self.text:
            game.game(color='y')
        if 'CHANGE' in self.text:
            options = sub_menu
            self.draw()
        if 'BLUE' in self.text:
            game.game(color='b')
        if 'YELLOW' in self.text:
            game.game(color='y')
        if 'BLACK' in self.text:
            game.game(color='r')
        if 'QUIT' in self.text:
            quit()
        if 'RETURN' in self.text:
            options = options_menu
            self.draw()

    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos


sub_menu = [Option("YELLOW", (setup.width/5 -30, 155),), Option("BLUE", (setup.width/2 - 30, 155)), Option("BLACK", (setup.width*3/4 - 30, 155)), Option("RETURN", (setup.width/2 - 45, 205))]

options_menu = [Option("PLAY", (140, 105)), Option("CHANGE SKIN", (135, 155)),
           Option("QUIT", (145, 205))]

options = options_menu
while True:
    pygame.event.pump()
    screen.fill((0, 0, 0))
    for option in options:
        if option.rect.collidepoint(pygame.mouse.get_pos()):
            option.hovered = True
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    option.do_something()

        else:
            option.hovered = False
        option.draw()
    pygame.display.update()