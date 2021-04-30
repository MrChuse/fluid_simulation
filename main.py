import pygame

from cell import Cell
from grid import Grid

WIDTH = 800
HEIGHT = 600

GRID_W = 200
GRID_H = 150

X_SIZE = WIDTH / GRID_W
Y_SIZE = HEIGHT / GRID_H


def main():
    pygame.init()
    pygame.display.set_caption('Paper Kingdom')
    window = pygame.display.set_mode((WIDTH, HEIGHT))

    grid = Grid(GRID_W, GRID_H)

    blit_w = pygame.Surface((1, 1))

    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        grid.diffuse()

        for i, row in enumerate(grid.get_grid()):
            for j, cell in enumerate(row):
                pygame.draw.rect(window, pygame.Color(int(cell.density * 255),
                                                      int(cell.density * 255),
                                                      int(cell.density * 255)),
                                 (i * X_SIZE, j * Y_SIZE, X_SIZE, Y_SIZE))
        pygame.display.update()


if __name__ == '__main__':
    main()
