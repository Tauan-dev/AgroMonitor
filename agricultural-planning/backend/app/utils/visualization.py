import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


def fig_to_base64(fig):
    """Converte figura matplotlib para base64."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return image_base64


def plot_sensitivity_heatmap(S, resource_labels, crop_labels):
    """Heatmap de sensibilidade."""
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.heatmap(
        S,
        annot=True, fmt=".2f",
        xticklabels=crop_labels,
        yticklabels=resource_labels,
        cmap="RdYlGn",
        vmin=0.0, vmax=0.9,
        linewidths=0.3, linecolor="white",
        cbar_kws={"label": "Sensibilidade local (normalizada)"},
        ax=ax
    )
    ax.collections[0].set_alpha(0.7)
    ax.set_title("Heatmap de sensibilidade recurso × cultura (plano base)")
    return fig_to_base64(fig)


def plot_base_vs_perturbed(x_base, x_pert, crop_labels, fixed_perturb=0.05):
    """Gráfico de barras base vs perturbado com label da perturbação fixa."""
    x_indices = np.arange(len(crop_labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 4))
    bars1 = ax.bar(x_indices - width/2, x_base, width, label="Base", color="#4C72B0")
    bars2 = ax.bar(x_indices + width/2, x_pert, width, label="Perturbado", color="#DD8452")
    ax.set_xticks(x_indices)
    ax.set_xticklabels(crop_labels)
    ax.set_ylabel("Área (ha)")
    ax.set_title(f"Áreas por cultura: solução base vs perturbada (perturbação: {fixed_perturb*100:.1f}%)")
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.annotate(f"{h:.1f}", (bar.get_x() + bar.get_width()/2, h),
                    ha="center", va="bottom", fontsize=8)
    return fig_to_base64(fig)


def plot_sensitivity_comparison(sens_well, sens_ill):
    """Gráfico bem vs mal condicionado."""
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
    ax.set_yscale("log")
    ax.legend()
    ax.grid(axis='y', alpha=0.3, which='both')
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.annotate(f"{h:.2e}", (bar.get_x() + bar.get_width()/2, h),
                    ha="center", va="bottom", fontsize=8)
    return fig_to_base64(fig)


def plot_regularization(x_normal, x_reg, crop_labels, lam):
    """Gráfico normal vs regularizado."""
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
    ax.grid(axis='y', alpha=0.3)
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.annotate(f"{h:.1f}", (bar.get_x() + bar.get_width()/2, h),
                    ha="center", va="bottom", fontsize=8)
    return fig_to_base64(fig)
