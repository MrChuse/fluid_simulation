from cell import Cell
from cell import diffuse


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.g = []
        for i in range(width):
            row = []
            for j in range(height):
                row.append(Cell(0, 0, 0))
            self.g.append(row)
        for row in self.g[self.width//2 - 3:self.width//2 + 4]:
            for cell in row[self.height//2 - 3:self.height//2 + 4]:
                cell.density = 1

    def get_grid(self):
        return self.g

    def get_in_range(self, i, j):
        return (i + self.width) % self.width, (j + self.height) % self.height

    def diffuse(self):
        new_g = []
        for i, row in enumerate(self.g):
            new_row = []
            for j, cell_ in enumerate(row):
                to_diffuse = [cell_]
                for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    actual_i, actual_j = self.get_in_range(i+di, j+dj)
                    to_diffuse.append(self.g[actual_i][actual_j])
                new_row.append(diffuse(to_diffuse))
            new_g.append(new_row)
        self. g = new_g
