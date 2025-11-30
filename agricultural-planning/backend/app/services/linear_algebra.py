import numpy as np
from scipy import linalg

def solve_linear_system(A, b):
    """Resolve A x ≈ b em mínimos quadrados."""
    x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    return x

def condition_number(A):
    """Número de condição kappa_2(A)."""
    return np.linalg.cond(A, 2)

def tikhonov_regularization(A, b, lam):
    """Resolve min ||A x - b||^2 + lam ||x||^2."""
    m, n = A.shape
    I = np.eye(n)
    AtA = A.T @ A
    Atb = A.T @ b
    x_reg = np.linalg.solve(AtA + lam * I, Atb)
    return x_reg

def compare_regularized_solution(A, b, lam=10.0):
    """Compara solução normal vs regularizada."""
    x_normal = solve_linear_system(A, b)
    x_reg = tikhonov_regularization(A, b, lam)
    return x_normal, x_reg
