import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#from scipy import linalg   # SciPy para álgebra linear


# ============================================================
# MODELO AGRÍCOLA BÁSICO EM FORMA MATRICIAL
# ============================================================

def build_base_model():
    """
    Constrói a matriz A e o vetor b para o problema agrícola base.
    Linhas de A: Terra, Mão de obra, Água, Fertilizante.
    Colunas de A: Milho, Soja, Trigo.
    """
    A = np.array([
        [1.0,   1.0,   1.0],      # terra (ha)
        [10.0,  8.0,  12.0],      # mão de obra (h)
        [3000., 2500., 1500.],    # água (m3)
        [150.,  120.,  100.]      # fertilizante (kg)
    ])

    b = np.array([
        100.0,     # terra total (ha)
        900.0,     # mão de obra (h)
        220000.0,  # água (m3)
        12000.0    # fertilizante (kg)
    ])

    profit = np.array([
        3000.0,  # milho
        2800.0,  # soja
        2000.0   # trigo
    ])

    return A, b, profit


# ============================================================
# ÁLGEBRA LINEAR: SOLUÇÃO E CONDICIONAMENTO
# ============================================================

def solve_linear_system(A, b):
    """
    Resolve A x ≈ b em mínimos quadrados.
    """
    x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    return x


def condition_number(A):
    """
    Número de condição kappa_2(A) (norma 2).
    Usa numpy.linalg.cond.
    """
    return np.linalg.cond(A, 2)


# ============================================================
# ANÁLISE DE SENSIBILIDADE
# ============================================================

def perturb_vector(b, rel_perturb=0.05, random_state=0):
    """
    Perturba b em uma fração relativa da sua norma.
    """
    rng = np.random.default_rng(random_state)
    noise = rng.normal(size=b.shape)
    noise = noise / np.linalg.norm(noise)
    delta_b = rel_perturb * np.linalg.norm(b) * noise
    return b + delta_b, delta_b


def perturb_matrix(A, rel_perturb=0.02, random_state=1):
    """
    Perturba A para simular incerteza nos coeficientes.
    """
    rng = np.random.default_rng(random_state)
    noise = rng.normal(size=A.shape)
    noise = noise / np.linalg.norm(noise)
    delta_A = rel_perturb * np.linalg.norm(A) * noise
    return A + delta_A, delta_A


def sensitivity_analysis(A, b, rel_perturb=0.05, random_state=0):
    """
    Calcula sensibilidade de x em relação a variações em b, com perturbação controlada.

    - Usa SEMPRE a mesma fração relativa rel_perturb.
    - Isso permite comparar honestamente bem vs mal condicionado.
    """
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


# ============================================================
# MATRIZES BEM E MAL CONDICIONADAS
# ============================================================

def build_well_conditioned_example():
    """
    Usa o modelo base como exemplo razoavelmente bem condicionado.
    """
    A, b, _ = build_base_model()
    # Usamos as 3 primeiras linhas (terra, mão de obra, água)
    return A[:3, :], b[:3]


def build_ill_conditioned_example():
    """
    Constrói um exemplo mal condicionado (linhas quase múltiplas).
    """
    A_ill = np.array([
        [1.0,   1.0,   1.0],
        [2.01,  2.00,  1.99],  # quase 2 * primeira linha
        [3.01,  3.00,  2.99]   # quase 3 * primeira linha
    ])
    b_ill = np.array([
        100.0,
        200.0,
        300.0
    ])
    return A_ill, b_ill


def demo_conditioning(rel_perturb=0.05):
    """
    Compara sensibilidade para bem x mal condicionado,
    usando a MESMA escala de perturbação relativa.
    """
    A_well, b_well = build_well_conditioned_example()
    sens_well = sensitivity_analysis(A_well, b_well,
                                     rel_perturb=rel_perturb,
                                     random_state=0)

    A_ill, b_ill = build_ill_conditioned_example()
    sens_ill = sensitivity_analysis(A_ill, b_ill,
                                    rel_perturb=rel_perturb,
                                    random_state=0)

    return sens_well, sens_ill, A_well, b_well, A_ill, b_ill


# ============================================================
# REGULARIZAÇÃO DE TIKHONOV
# ============================================================

def tikhonov_regularization(A, b, lam):
    """
    Resolve min ||A x - b||^2 + lam ||x||^2.
    """
    m, n = A.shape
    I = np.eye(n)
    AtA = A.T @ A
    Atb = A.T @ b
    x_reg = np.linalg.solve(AtA + lam * I, Atb)
    return x_reg


def compare_regularized_solution(A, b, lam=1.0):
    """
    Compara solução normal x_regularizada.
    """
    x_normal = solve_linear_system(A, b)
    x_reg = tikhonov_regularization(A, b, lam)
    return x_normal, x_reg


# ============================================================
# SENSIBILIDADE LOCAL E HEATMAP (com Seaborn)
# ============================================================

def local_sensitivity_matrix(A, x):
    Ax = A @ x
    norm_Ax = np.linalg.norm(Ax)
    if norm_Ax == 0:
        return np.zeros_like(A)
    S = np.abs(A * x[np.newaxis, :]) / norm_Ax
    return S


def plot_sensitivity_heatmap(S, resource_labels, crop_labels, title):
    plt.figure(figsize=(7, 4))
    sns.heatmap(
        S,
        annot=True, fmt=".2f",
        xticklabels=crop_labels,
        yticklabels=resource_labels,
        cmap="RdYlGn",        # verde (baixo) → amarelo → vermelho (alto)
        vmin=0.0, vmax=0.9,     # limita o contraste (ajuste se quiser)
        linewidths=0.3, linecolor="white",
        cbar_kws={"label": "Sensibilidade local (normalizada)"}
    )
    
   

    plt.title(title)
    plt.tight_layout()




# ============================================================
# VISUALIZAÇÕES (GRÁFICOS)
# ============================================================

def plot_base_vs_perturbed(x_base, x_pert, crop_labels):
    """
    Gráfico de barras: áreas base vs áreas com b perturbado.
    """
    x_indices = np.arange(len(crop_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))
    bars1 = ax.bar(x_indices - width/2, x_base, width, label="Base", color="#4C72B0")
    bars2 = ax.bar(x_indices + width/2, x_pert, width, label="Perturbado", color="#DD8452")

    ax.set_xticks(x_indices)
    ax.set_xticklabels(crop_labels)
    ax.set_ylabel("Área (ha)")
    ax.set_title("Áreas por cultura: solução base vs perturbada")
    ax.legend()

    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.annotate(f"{h:.1f}", (bar.get_x() + bar.get_width()/2, h),
                    ha="center", va="bottom", fontsize=8)

    plt.tight_layout()


def plot_sensitivity_well_vs_ill(sens_well, sens_ill):
    """
    Gráfico comparando ||Δb||/||b|| e ||Δx||/||x|| para
    sistema bem e mal condicionado.
    """
    labels = ["Bem condicionado", "Mal condicionado"]
    rel_db = [sens_well["rel_db"], sens_ill["rel_db"]]
    rel_dx = [sens_well["rel_dx"], sens_ill["rel_dx"]]

    x_indices = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))
    bars1 = ax.bar(x_indices - width/2, rel_db, width,
                   label="||Δb||/||b|| (recursos)", color="#55A868")
    bars2 = ax.bar(x_indices + width/2, rel_dx, width,
                   label="||Δx||/||x|| (áreas)", color="#C44E52")

    ax.set_xticks(x_indices)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Valor relativo")
    ax.set_title("Sensibilidade: recursos vs áreas (bem x mal condicionado)")
    ax.legend()
    ax.grid(axis='y', linestyle=':', linewidth=0.8)

    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.annotate(f"{h:.2e}", (bar.get_x() + bar.get_width()/2, h),
                    ha="center", va="bottom", fontsize=8)

    plt.tight_layout()


def plot_normal_vs_regularized(x_normal, x_reg, crop_labels, lam):
    """
    Gráfico de barras: solução normal vs Tikhonov para
    o sistema mal condicionado.
    """
    x_indices = np.arange(len(crop_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))
    bars1 = ax.bar(x_indices - width/2, x_normal, width,
                   label="Normal (LS)", color="#2E91E5")
    bars2 = ax.bar(x_indices + width/2, x_reg, width,
                   label=f"Tikhonov (λ={lam})", color="#E15F99")

    ax.set_xticks(x_indices)
    ax.set_xticklabels(crop_labels)
    ax.set_ylabel("Área (ha)")
    ax.set_title("Sistema mal condicionado: normal vs regularizado")
    ax.legend()

    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.annotate(f"{h:.1f}", (bar.get_x() + bar.get_width()/2, h),
                    ha="center", va="bottom", fontsize=8)

    plt.tight_layout()


# ============================================================
# MAIN: EXECUÇÃO COMPLETA + RESUMO DINÂMICO
# ============================================================

def main():
    crop_labels = ["Milho", "Soja", "Trigo"]
    resource_labels = ["Terra", "Mão de obra", "Água", "Fertilizante"]

    # ---------- Modelo base ----------
    A_base, b_base, profit = build_base_model()
    A_eq = A_base[:3, :]   # terra, mão de obra, água como igualdade
    b_eq = b_base[:3]

    x_base = solve_linear_system(A_eq, b_eq)
    kappa_base = condition_number(A_eq)
    total_profit = profit @ x_base

    # Sensibilidade no modelo base
    sens_base = sensitivity_analysis(A_eq, b_eq)

    # ---------- Bem x mal condicionado ----------
    sens_well, sens_ill, A_well, b_well, A_ill, b_ill = demo_conditioning()

    # ---------- Regularização ----------
    lam = 10.0
    x_normal_ill, x_reg_ill = compare_regularized_solution(A_ill, b_ill, lam=lam)

    # ====================================================
    # IMPRESSÕES TEXTUAIS (DINÂMICAS)
    # ====================================================

    print("========== MODELO AGRÍCOLA BASE ==========\n")
    print("Solução base (área em ha) para [milho, soja, trigo]:")
    print(x_base)
    print(f"Número de condição kappa_2(A_eq): {kappa_base:.2e}")
    print(f"Lucro estimado do plano (R$): {total_profit:.2f}\n")

    print("========== SENSIBILIDADE (BASE) ==========\n")
    print("Solução com recursos perturbados (b + Δb):")
    print(sens_base["x_pert_b"])
    print(f"||Δx||/||x|| = {sens_base['rel_dx']:.3e}")
    print(f"||Δb||/||b|| = {sens_base['rel_db']:.3e}")
    print(f"kappa(A_eq)*||Δb||/||b|| ≈ {sens_base['bound']:.3e}\n")

    print("========== BEM VS MAL CONDICIONADO ==========\n")
    print(f"kappa_2(A_well) (bem condicionado) = {sens_well['kappa']:.2e}")
    print(f"kappa_2(A_ill)  (mal condicionado) = {sens_ill['kappa']:.2e}")
    print(
        f"Sistema bem condicionado: ||Δx||/||x|| ≈ {sens_well['rel_dx']:.3e} "
        f"para ||Δb||/||b|| ≈ {sens_well['rel_db']:.3e}"
    )
    print(
        f"Sistema mal condicionado: ||Δx||/||x|| ≈ {sens_ill['rel_dx']:.3e} "
        f"para ||Δb||/||b|| ≈ {sens_ill['rel_db']:.3e}\n"
    )

    print("========== REGULARIZAÇÃO (MAL CONDICIONADO) ==========\n")
    print("Solução normal (LS):", x_normal_ill)
    print(f"Solução Tikhonov (λ={lam}):", x_reg_ill, "\n")

    def classify_cond(kappa):
        if kappa < 1e2:
            return "bem condicionado (decisões robustas)"
        elif kappa < 1e4:
            return "moderadamente condicionado"
        else:
            return "mal condicionado (decisões frágeis)"

    print("========== RESUMO NUMÉRICO E AGRONÔMICO ==========\n")
    print(f"A_eq: kappa_2 ≈ {kappa_base:.2e} -> {classify_cond(kappa_base)}")
    print(
        f"No modelo base, uma perturbação relativa de recursos de "
        f"{sens_base['rel_db']:.2%} gerou uma variação relativa "
        f"de áreas de {sens_base['rel_dx']:.2%}."
    )
    print(
        "Isso quantifica, em termos de álgebra linear, a robustez do plano de "
        "plantio frente a incertezas em terra, mão de obra e água.\n"
    )

    print(
        f"No exemplo mal condicionado (kappa ≈ {sens_ill['kappa']:.2e}), a mesma "
        f"ordem de ||Δb||/||b|| provoca ||Δx||/||x|| muito maior,\n"
        "indicando que pequenas mudanças de recursos podem virar grandes "
        "mudanças de área, o que é arriscado na prática.\n"
    )

    print(
        "A comparação entre a solução normal e a solução regularizada mostra "
        "que a regularização reduz extremos nas áreas de cultivo,\n"
        "tornando o plano mais estável numericamente e mais conservador "
        "agronomicamente frente às incertezas.\n"
    )

    # ====================================================
    # GRÁFICOS
    # ====================================================

    # 1) Heatmap de sensibilidade local (plano base)
    S_base = local_sensitivity_matrix(A_base, x_base)
    plot_sensitivity_heatmap(
        S_base,
        resource_labels=resource_labels,
        crop_labels=crop_labels,
        title="Heatmap de sensibilidade recurso × cultura (plano base)",
    )

    # 2) Áreas base vs perturbadas (modelo base)
    plot_base_vs_perturbed(sens_base["x_base"], sens_base["x_pert_b"], crop_labels)

    # 3) Sensibilidade bem x mal condicionado
    plot_sensitivity_well_vs_ill(sens_well, sens_ill)

    # 4) Normal vs Tikhonov no mal condicionado
    plot_normal_vs_regularized(x_normal_ill, x_reg_ill,
                               crop_labels=["C1", "C2", "C3"], lam=lam)

    plt.show()


if __name__ == "__main__":
    main()
