from sympy import symbols, Eq, solve

def solve_orbit_equation(velocity):
    r, t = symbols('r t')
    g = 9.8
    eq = Eq(r, velocity * t - (g * t**2) / 2)
    solution = solve(eq, t)
    return str(solution)