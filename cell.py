from dataclasses import dataclass


@dataclass
class Cell:
    density: float
    vx: float
    vy: float


def diffuse(l):
    mean_density = sum([c.density for c in l]) / len(l)
    return Cell(mean_density, l[0].vx, l[0].vy)
