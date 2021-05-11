import numpy as np

def lerp(from_, to, t):
    return from_ + t * (to - from_)

class Grid:
    def __init__(self, width, height, viscosity=0.5):
        self.width = width
        self.height = height
        self.viscosity = viscosity
        
        self.u = np.zeros((width, height))
        self.v = np.zeros((width, height))
        
        self.dens = np.zeros((width, height))
        
    def get_grid(self):
        return self.dens, self.u, self.v
        
    def get_in_range(self, i, j):
        return (i + self.width) % self.width, (j + self.height) % self.height

        
    def add_density(self, i, j, to, t=1, size=3):
        for di in range(-size, size+1):
            for dj in range(-size, size+1):
                i_, j_ = self.get_in_range(i+di, j+dj)
                self.dens[i_][j_] = to#lerp(self.dens[i_][j_], to, t)
                
    def add_velocity(self, i, j, vx, vy, t=0.5, size=3):
        for di in range(-size, size+1):
            for dj in range(-size, size+1):
                i_, j_ = self.get_in_range(i+di, j+dj)
                self.u[i_][j_] = lerp(self.u[i_][j_], vx, t)
                self.v[i_][j_] = lerp(self.v[i_][j_], vy, t)
    
    def set_bnd(self, b, x):
        x[0, :]  = -x[1, :]  if b == 1 else x[1, :]
        x[-1, :] = -x[-2, :] if b == 1 else x[-2, :]
        x[:, 0]  = -x[:, 1]  if b == 2 else x[:, 1]
        x[:, -1] = -x[:, -2] if b == 2 else x[:, -2]
        x[0,0]   = 0.5 * (x[1,0]   + x[0,1])
        x[0,-1]  = 0.5 * (x[1,-1]  + x[0,-2]) 
        x[-1,0]  = 0.5 * (x[-2,0]  + x[-1,1])
        x[-1,-1] = 0.5 * (x[-2,-1] + x[-2,-1])
        return x
        
    def diffuse(self, x, x0, dt, diff, b):
        a = dt * diff * self.width * self.height
        
        for _ in range(20):
            N = np.roll(x, shift=-1, axis=0)
            S = np.roll(x, shift=1, axis=0)
            E = np.roll(x, shift=1, axis=1)
            W = np.roll(x, shift=-1, axis=1)
            x = (x0 + a*(N+S+E+W)) / (1+4*a)
        
        x = self.set_bnd(b, x)
        return x
            
    def advect(self, d0, dt, b):
        dt0 = dt * self.width
        dt1 = dt * self.height
        i, j = np.indices((self.width, self.height))
        x = i - dt0 * self.u
        y = j - dt1 * self.v
        
        x[x<0.5] = 0.5
        x[x>self.width-1.5] = self.width - 1.5
        i0 = x.astype(int)
        i1 = i0 + 1
        
        y[y<0.5] = 0.5
        y[y>self.height-1.5] = self.height - 1.5
        j0 = y.astype(int)
        j1 = j0 + 1
        
        s1 = x - i0
        s0 = 1 - s1
        t1 = y - j0
        t0 = 1 - t1
        d = (s0 * (t0*d0[i0,j0] + t1*d0[i0,j1]) +
             s1 * (t0*d0[i1,j0] + t1*d0[i1,j1]))
        
        d = self.set_bnd(b, d)
        return d
    
    def dens_step(self, dt):
        prev_dens = np.array(self.dens)
        self.dens = self.diffuse(self.dens, prev_dens, dt, self.viscosity, 0)
        self.dens = self.advect(self.dens, dt, 0);
        
        # print(np.sum(self.dens))
        
    def project(self):
        h1 = 1 / self.width
        h2 = 1 / self.height
        
        N = np.roll(self.v, shift=-1, axis=0)
        S = np.roll(self.v, shift=1, axis=0)
        E = np.roll(self.u, shift=1, axis=1)
        W = np.roll(self.u, shift=-1, axis=1)
        
        div = -0.5 * (h1 * (W - E) + h2 * (N - S))
        p = np.zeros((self.width, self.height))
        div = self.set_bnd(0, div)
        p = self.set_bnd(0, p)
        
        for _ in range(20):
            N = np.roll(p, shift=-1, axis=0)
            S = np.roll(p, shift=1, axis=0)
            E = np.roll(p, shift=1, axis=1)
            W = np.roll(p, shift=-1, axis=1)
            p = (div + N+S+E+W) / 4
            p = self.set_bnd(0, p)
        
        N = np.roll(p, shift=-1, axis=0)
        S = np.roll(p, shift=1, axis=0)
        E = np.roll(p, shift=1, axis=1)
        W = np.roll(p, shift=-1, axis=1)
        
        self.u -= 0.5 * (W - E) / h1
        self.v -= 0.5 * (N - S) / h2
        
    def vel_step(self, dt):
        prev_u = np.array(self.u)
        prev_v = np.array(self.v)
        self.u = self.diffuse(self.u, prev_u, dt, self.viscosity, 1)
        self.v = self.diffuse(self.v, prev_v, dt, self.viscosity, 2)
        
        self.project()
        
        self.u = self.advect(self.u, dt, 1)
        self.v = self.advect(self.v, dt, 2)
        
        self.project()
        