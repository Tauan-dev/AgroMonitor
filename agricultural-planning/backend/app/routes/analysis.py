from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
from ..models import ModelInput, AnalysisOutput
from ..services.linear_algebra import (
    solve_linear_system, condition_number, 
    tikhonov_regularization, compare_regularized_solution
)
from ..services.sensitivity import sensitivity_analysis, local_sensitivity_matrix
from ..utils.visualization import (
    plot_sensitivity_heatmap, plot_base_vs_perturbed,
    plot_sensitivity_comparison, plot_regularization
)




router = APIRouter(prefix="/api", tags=["analysis"])

def build_ill_conditioned_example():
    """Exemplo mal condicionado."""
    A_ill = np.array([
        [1.0,   1.0,   1.0],
        [2.01,  2.00,  1.99],
        [3.01,  3.00,  2.99]
    ])
    b_ill = np.array([100.0, 200.0, 300.0])
    return A_ill, b_ill

@router.post("/analyze")
async def analyze(input_data: ModelInput):
    try:
        A_base = np.array(input_data.A)
        b_base = np.array(input_data.b)
        profit = np.array(input_data.profit)

        # Solução base
        A_eq = A_base[:3, :]
        b_eq = b_base[:3]
        x_base = solve_linear_system(A_eq, b_eq)
        kappa_base = condition_number(A_eq)
        total_profit_base = float(profit @ x_base)

        # Sensibilidade COM perturbação do usuário (para diagnósticos)
        sens_base = sensitivity_analysis(A_eq, b_eq, input_data.rel_perturb)
        
        # NOVO: Lucro perturbado PESSIMISTA (redução de recursos)
        b_perturbed_pessimistic = b_eq * (1 - input_data.rel_perturb)
        x_pert_pessimistic = solve_linear_system(A_eq, b_perturbed_pessimistic)
        total_profit_pert_pessimistic = float(profit @ x_pert_pessimistic)
        
        # Lucro perturbado OTIMISTA (aumento de recursos)
        b_perturbed_optimistic = b_eq * (1 + input_data.rel_perturb)
        x_pert_optimistic = solve_linear_system(A_eq, b_perturbed_optimistic)
        total_profit_pert_optimistic = float(profit @ x_pert_optimistic)

        # Bem x mal condicionado
        A_ill, b_ill = build_ill_conditioned_example()
        sens_well = sensitivity_analysis(A_eq, b_eq, input_data.rel_perturb)
        sens_ill = sensitivity_analysis(A_ill, b_ill, input_data.rel_perturb)

        # Regularização
        lam = 10.0
        x_normal_ill, x_reg_ill = compare_regularized_solution(A_ill, b_ill, lam=lam)

        # Visualizações
        S_base = local_sensitivity_matrix(A_base, x_base)
        heatmap_img = plot_sensitivity_heatmap(S_base, input_data.resources, input_data.crops)
        comparison_img = plot_base_vs_perturbed(
            sens_base["x_base"],
            sens_base["x_pert_b"],
            input_data.crops,
            fixed_perturb=input_data.rel_perturb
        )
        sensitivity_img = plot_sensitivity_comparison(sens_well, sens_ill)
        regularization_img = plot_regularization(x_normal_ill, x_reg_ill, ["C1", "C2", "C3"], lam)

        return {
            "x_base": [float(x) for x in x_base],
            "kappa": float(kappa_base),
            "profit_base": total_profit_base,
            "profit_pert_pessimistic": total_profit_pert_pessimistic,  # NOVO
            "profit_pert_optimistic": total_profit_pert_optimistic,    # NOVO
            "rel_dx": float(sens_base["rel_dx"]),
            "rel_db": float(sens_base["rel_db"]),
            "bound": float(sens_base["bound"]),
            "heatmap": heatmap_img,
            "comparison": comparison_img,
            "sensitivity": sensitivity_img,
            "regularization": regularization_img,
            "diagnostics": {
                "kappa_well": float(sens_well["kappa"]),
                "kappa_ill": float(sens_ill["kappa"]),
                "rel_dx_well": float(sens_well["rel_dx"]),
                "rel_dx_ill": float(sens_ill["rel_dx"]),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


