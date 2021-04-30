from dataclasses import dataclass
from statistics import mean

from sle_solver import solve


@dataclass
class Cell:
    density: float
    vx: float
    vy: float
    viscosity: float = 1


def measure(x, y):
    assert len(x) == len(y)
    return sum([abs(x_ - y_) for x_, y_ in zip(x, y)])


def diffuse(l):
    new_density = mean([c.density for c in l])
    return Cell(new_density, l[0].vx, l[0].vy)
