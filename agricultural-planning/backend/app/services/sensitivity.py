import numpy as np
from .linear_algebra import solve_linear_system, condition_number

def sensitivity_analysis(A, b, rel_perturb=0.05, random_state=0):
    """Calcula sensibilidade de x em relação a variações em b."""
    x_base = solve_linear_system(A, b)

    rng = np.random.default_rng(random_state)
    noise = rng.normal(size=b.shape)
    noise = noise / np.linalg.norm(noise)
    delta_b = rel_perturb * np.linalg.norm(b) * noise
    b_pert = b + delta_b

    x_pert = solve_linear_system(A, b_pert)

    delta_x = x_pert - x_base
    rel_dx = np.linalg.norm(delta_x) / np.linalg.norm(x_base)
    rel_db = np.linalg.norm(delta_b) / np.linalg.norm(b)

    kappa = condition_number(A)
    bound = kappa * rel_db

    return {
        "x_base": x_base,
        "x_pert_b": x_pert,
        "rel_dx": rel_dx,
        "rel_db": rel_db,
        "kappa": kappa,
        "bound": bound,
    }

def local_sensitivity_matrix(A, x):
    """Calcula matriz de sensibilidade local recurso × cultura."""
    Ax = A @ x
    norm_Ax = np.linalg.norm(Ax)
    if norm_Ax == 0:
        return np.zeros_like(A)
    S = np.abs(A * x[np.newaxis, :]) / norm_Ax
    return S
