import pygame

from cell import Cell
from grid2 import Grid
from grid import lerp

WIDTH = 800
HEIGHT = 600

GRID_W = 200
GRID_H = 150

X_SIZE = WIDTH / GRID_W
Y_SIZE = HEIGHT / GRID_H


def main():
    pygame.init()
    pygame.display.set_caption('FluidSim')
    window = pygame.display.set_mode((WIDTH, HEIGHT))

    grid = [Grid(GRID_W, GRID_H) for _ in (0, 1, 2)]

    blit_w = pygame.Surface((1, 1))

    add_size = 1
    sizesqrd = (2 * add_size + 1) ** 2
    spacebar_clicker = False
    current_grid = 0
    mouse_down = False
    prev_mouse = None
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                button = event.button
                #print(button)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                prev_mouse = None
            elif event.type == pygame.MOUSEWHEEL:
                add_size += event.y
                add_size = max(min(add_size, 15), 0)
                sizesqrd = (2 * add_size + 1) ** 2
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    spacebar_clicker = not spacebar_clicker
                elif event.key == pygame.K_TAB:
                    current_grid = (current_grid + 1) % 3
                
        
        if mouse_down:
            x, y = pygame.mouse.get_pos()
            x, y = int(x / X_SIZE), int(y / Y_SIZE)
            if prev_mouse is None:
                if not spacebar_clicker:
                    grid[current_grid].add_density(x, y,t=1, to=1 if button==1 else 0, size=add_size)
                prev_mouse = x, y
            else:
                sizesqrd = (2 * add_size + 1)
                dirx = x - prev_mouse[0]
                diry = y - prev_mouse[1]
                length = ((dirx) ** 2 + (diry) ** 2) ** 0.5
                if length > 0:
                    norm_dirx = dirx / (length)
                    norm_diry = diry / (length)
                    #print(norm_dirx, norm_diry)
                points = length // sizesqrd + 1
                dt = 1 / points
                t = dt
                while t <= 1:
                    x_ = int(lerp(prev_mouse[0], x, t))
                    y_ = int(lerp(prev_mouse[1], y, t))
                    if not spacebar_clicker:
                        grid[current_grid].add_density(x_, y_, to=1 if button==1 else 0, size=add_size)
                    if length > 0:
                        if spacebar_clicker:
                            for g in grid:
                                g.add_velocity(x_, y_, norm_dirx, norm_diry, size=add_size)
                            #print('added vel')
                    t += dt
                prev_mouse = x, y
                
        #grid.diffuse(50)
        #grid.clear_divergence()
        #grid.advection()
        #grid.clear_divergence()
        for g in grid:
            g.dens_step(0.1)
            g.vel_step(0.1)
        
        density = []
        vx = []
        vy = []
        for g in grid:
            d, x, y = g.get_grid()
            density.append(d)
        for i, row in enumerate(density[0]):
            for j, cell in enumerate(row):
                pygame.draw.rect(window, pygame.Color(int(density[0][i][j] * 255),
                                                      int(density[1][i][j] * 255),
                                                      int(density[2][i][j] * 255)),
                                 (i * X_SIZE, j * Y_SIZE, X_SIZE, Y_SIZE))
                                 
        # for i, (rowx, rowy) in enumerate(zip(vx,vy)):
            # for j, (vx_, vy_) in enumerate(zip(rowx, rowy)):
                # pygame.draw.line(window, pygame.Color('black'),
                                 # (i * X_SIZE + X_SIZE // 2, j * Y_SIZE + Y_SIZE // 2),
                                 # (i * X_SIZE + X_SIZE // 2 +  vx_ * 100, j * Y_SIZE + Y_SIZE // 2 + vy_*100))
        pygame.display.update()


if __name__ == '__main__':
    main()
