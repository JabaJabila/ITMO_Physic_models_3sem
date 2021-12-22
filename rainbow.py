import pygame as pg

pg.init()

# project config
display_x = 1000
display_y = 600
fps = 60

# Window configuration
win = pg.display.set_mode([display_x, display_y])
pg.display.set_caption('Моделирование радуги')
clock = pg.time.Clock()

pg.display.flip()

while True:
    clock.tick(fps)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
