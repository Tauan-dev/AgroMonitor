from pydantic import BaseModel
from typing import List

class ModelInput(BaseModel):
    """Input para análise agrícola"""
    resources: List[str]  # ["Terra", "Mão de obra", "Água", "Fertilizante"]
    crops: List[str]      # ["Milho", "Soja", "Trigo"]
    A: List[List[float]]  # matriz de coeficientes
    b: List[float]        # vetor de recursos disponíveis
    profit: List[float]   # lucro por cultura
    rel_perturb: float = 0.05

class AnalysisOutput(BaseModel):
    """Output da análise"""
    x_base: List[float]
    kappa: float
    profit: float
    rel_dx: float
    rel_db: float
    bound: float
    heatmap_base64: str  # Imagem base64
    comparison_base64: str
    sensitivity_base64: str
    regularization_base64: str
