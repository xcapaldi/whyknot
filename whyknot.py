import sys
import pygame as pg

pg.init()

width = 320
height = 240
background = [0, 0, 0]

screen = pg.display.set_mode((width, height))

while 1:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
    screen.fill(background)
    pg.display.flip()
