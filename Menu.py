import pygame
import os
import game
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
            self.save_options = options
            options = sub_menu
            self.draw()
        if 'BLUE' in self.text:
            game.game(color='b')
        if 'YELLOW' in self.text:
            game.game(color='y')
        if 'NIGER' in self.text:
            game.game(color='r')
        if 'QUIT' in self.text or 'EXIT' in self.text:
            pygame.quit()

    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos


pygame.init()
screen = pygame.display.set_mode((500, 800))
menu_font = pygame.font.Font(None, 40)
sub_menu = [Option("YELLOW", (60, 155),), Option("BLUE", (240, 155)), Option("NIGER", (380, 155)), Option("EXIT", (145, 205))]

options = [Option("PLAY", (140, 105)), Option("CHANGE SKIN", (135, 155)),
           Option("QUIT", (145, 205))]


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