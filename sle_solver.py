def solve(initial_cond, f, measure, eps=0.01):
    x = initial_cond
    meas = eps + 1
    while meas > eps:
        old_x = x[:]
        x = f(x)
        meas = measure(old_x, x)
