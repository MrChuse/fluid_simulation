from cell import Cell
from cell import diffuse

import numpy as np
from scipy.signal import convolve2d
import time

def lerp(from_, to, t):
    return from_ + t * (to - from_)

class Grid:
    def __init__(self, width, height, viscosity=0.5):
        self.width = width
        self.height = height
        self.viscosity = viscosity
        # self.g = []
        # for i in range(width):
            # row = []
            # for j in range(height):
                # row.append(Cell(0, 0, 0))
            # self.g.append(row)
        self.density = np.indices((width, height))[0] / width
        print(self.density)
        self.vx = np.zeros((width, height))
        self.vy = np.zeros((width, height))
        size = 0
        for row in range(self.width//2 - size, self.width//2 + size + 1):
            for cell in range(self.height//2 - size, self.height//2 + size + 1):
                self.density[row][cell] = 1
                
        self.diffuse = self.diffuse2

    def get_grid(self):
        return self.density, self.vx, self.vy

    def get_in_range(self, i, j):
        return (i + self.width) % self.width, (j + self.height) % self.height

    def add_density(self, i, j, to, t=0.5, size=3):
        # look into using mode='wrap' in numpy, idk
        # irange = np.arange(i-size, i+size+1) 
        # jrange = np.arange(j-size, j+size+1)
        # region = self.density.take(i-size:i+size+1
        for di in range(-size, size+1):
            for dj in range(-size, size+1):
                i_, j_ = self.get_in_range(i+di, j+dj)
                self.density[i_][j_] = lerp(self.density[i_][j_], to, t)
                
    def add_velocity(self, i, j, vx, vy, t=0.5, size=3):
        for di in range(-size, size+1):
            for dj in range(-size, size+1):
                i_, j_ = self.get_in_range(i+di, j+dj)
                self.vx[i_][j_] = lerp(self.vx[i_][j_], vx, t)
                self.vy[i_][j_] = lerp(self.vy[i_][j_], vy, t)

    def diffuse1(self):
        ker = [[0, 0.2, 0],[0.2, 0.2, 0.2], [0, 0.2, 0]]
        self.density = convolve2d(self.density, ker, boundary='wrap')
        self.density = np.roll(self.density, -1)
        self.density = np.roll(self.density, -1, axis=0)
        
    def diffuse_step(self, original, current):
        N = np.roll(current, shift=-1, axis=0)
        S = np.roll(current, shift=1, axis=0)
        E = np.roll(current, shift=1, axis=1)
        W = np.roll(current, shift=-1, axis=1)
        
        # N[-1, :] = 0
        # S[0,:] = 0
        # E[:,0] = 0
        # W[:,-1] = 0
        
        
        return (self.density + self.viscosity * (N + S + E + W) / 4) / (1 + self.viscosity)
        
    def diffuse2(self, iterations=5):
        new_d = np.zeros((self.width, self.height))
        new_vx = np.zeros((self.width, self.height))
        new_vy = np.zeros((self.width, self.height))
        
        # simple iterations:
        for _ in range(iterations):
            new_d = self.diffuse_step(self.density, new_d)
            #new_vx = self.diffuse_step(self.vx, new_vx)
            #new_vy = self.diffuse_step(self.vy, new_vy)
        self.density = new_d
        #self.vx = new_vx
        #self.vy = new_vy

    def advection_step(self, param, fractx, fracty):
        W = np.roll(param, shift=-1, axis=1)
        N = np.roll(param, shift=-1, axis=0)
        # N[-1, :] = 0
        # W[:,-1] = 0
        
        NW = np.roll(N, shift=-1, axis=1)
        # NW[:,-1] = 0
        z1 = lerp(param, W, fractx)
        z2 = lerp(N, NW, fractx)
        # print('fractx')
        # print(fractx)
        # print('z1')
        # print(z1)
        # print('z2')
        # print(z2)
        res = lerp(z1, z2, fracty)
        return res
        
    def advection(self, dt=1):
        s = self.density.shape
        
        x, y = np.indices(s)
        
        fx = x - self.vx * dt # calculate from where to get
        fy = y - self.vy * dt # new parameters (density, etc)
        fx[fx<0] -= 1
        fy[fy<0] -= 1
        fx += s[0]
        fy += s[1]
        

        fractx, floorx = np.modf(fx)
        fracty, floory = np.modf(fy)
        floorx = floorx.astype(np.uint) % s[0]
        floory = floory.astype(np.uint) % s[1]
        # print('self.density: ')
        # print(self.density)
        # print('floorx: ')
        # print(floorx)
        # print('floory: ')
        # print(floory)
        
        get_density = self.density[floorx, floory]
        get_vx = self.vx[floorx, floory]
        get_vy = self.vy[floorx, floory]
        # print('get_density')
        # print(get_density)
        self.density = self.advection_step(get_density, fractx, fracty)
        print(np.sum(self.density))
        self.vx = self.advection_step(get_vx, fractx, fracty)
        self.vy = self.advection_step(get_vy, fractx, fracty)
        # print('self.density')
        # print(self.density)
        # print()
        
    def step_divergence(self, p, delta_v):
        N = np.roll(p, shift=-1, axis=0)
        S = np.roll(p, shift=1, axis=0)
        E = np.roll(p, shift=1, axis=1)
        W = np.roll(p, shift=-1, axis=1)
        # N[-1, :] = 0
        # S[0,:] = 0
        # E[:,0] = 0
        # W[:,-1] = 0
        return (N + S + E + W - delta_v) / 4
        
    def clear_divergence(self, iterations=5):
        Nx = np.roll(self.vx, shift=-1, axis=0)
        Sx = np.roll(self.vx, shift=1, axis=0)
        # Nx[-1, :] = 0
        # Sx[0,:] = 0
        delta_v = (Nx - Sx) / 2
        Ny = np.roll(self.vy, shift=-1, axis=1)
        Sy = np.roll(self.vy, shift=1, axis=1)
        # Sy[:,0] = 0
        # Ny[:,-1] = 0
        delta_v += (Ny - Sy) / 2
        
        p = np.zeros((self.width, self.height))
        for _ in range(iterations):
            p = self.step_divergence(p, delta_v)
        
        Nx = np.roll(p, shift=-1, axis=0)
        Sx = np.roll(p, shift=1, axis=0)
        # Nx[-1, :] = 0
        # Sx[0,:] = 0
        delta_px = (Nx - Sx) / 2
        Ny = np.roll(p, shift=-1, axis=1)
        Sy = np.roll(p, shift=1, axis=1)
        # Sy[:,0] = 0
        # Ny[:,-1] = 0
        delta_py = (Ny - Sy) / 2
        
        self.vx -= delta_px
        self.vy -= delta_py
        
