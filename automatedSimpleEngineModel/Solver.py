#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#


# Euler Solver
def Integrator_Euler(y_t0, dx, dt):
    return y_t0 + dx * dt


def Integrator(y_t0, dx, dt, dx_prev, method):
    if method == "Euler":
        return y_t0 + dx * dt
    elif method == "Trapezoidal":
        return y_t0 + (dx + dx_prev) * dt / 2
    else:
        raise ValueError(f"Unrecognized method: {method}")
