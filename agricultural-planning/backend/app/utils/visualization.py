import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


def fig_to_base64(fig):
    """Converte figura matplotlib para base64."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white', edgecolor='none')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return image_base64


# Paleta profissional
COLORS = {
    'primary': '#2196F3',
    'secondary': '#FF6B6B',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'neutral_light': '#F5F5F5',
    'neutral_dark': '#333333',
}

FONT_SETTINGS = {
    'family': 'sans-serif',
    'size': 10,
}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 13,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 10,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#E0E0E0',
    'axes.grid': True,
    'grid.color': '#F0F0F0',
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
})


def plot_sensitivity_heatmap(S, resource_labels, crop_labels):
    """Heatmap profissional de sensibilidade."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.heatmap(
        S,
        annot=True,
        fmt='.2f',
        xticklabels=crop_labels,
        yticklabels=resource_labels,
        cmap='RdYlGn',
        vmin=0.0,
        vmax=0.9,
        cbar_kws={'label': 'Sensibilidade Normalizada'},
        linewidths=1,
        linecolor='white',
        ax=ax,
        square=False,
        annot_kws={'fontsize': 10, 'weight': 'bold'},
    )
    
    ax.set_title('Sensibilidade: Recurso × Cultura (Plano Base)', fontsize=13, fontweight='bold', pad=16)
    ax.set_xlabel('Culturas', fontsize=11, fontweight='600')
    ax.set_ylabel('Recursos', fontsize=11, fontweight='600')
    
    # Estilo limpo
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_base_vs_perturbed(x_base, x_pert, crop_labels, fixed_perturb=0.05):
    """Gráfico profissional: base vs perturbado (comparação com espaço)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    
    x_indices = np.arange(len(crop_labels))
    width = 0.35
    
    bars1 = ax.bar(
        x_indices - width/2,
        x_base,
        width,
        label='Cenário Base',
        color=COLORS['primary'],
        alpha=0.85,
        edgecolor='white',
        linewidth=1.5,
    )
    
    bars2 = ax.bar(
        x_indices + width/2,
        x_pert,
        width,
        label=f'Perturbação {fixed_perturb*100:.1f}%',
        color=COLORS['secondary'],
        alpha=0.85,
        edgecolor='white',
        linewidth=1.5,
    )
    
    ax.set_xticks(x_indices)
    ax.set_xticklabels(crop_labels, fontsize=11, fontweight='600')
    ax.set_ylabel('Área (ha)', fontsize=11, fontweight='600')
    ax.set_title('Áreas por Cultura: Cenário Base vs Perturbado', fontsize=13, fontweight='bold', pad=16)
    
    # Anotações nos topos das barras
    for bar in bars1:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f'{height:.0f}',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='500',
        )
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f'{height:.0f}',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='500',
        )
    
    ax.legend(loc='upper right', framealpha=0.95, edgecolor='#E0E0E0', fancybox=False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Estilo limpo
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_sensitivity_comparison(sens_well, sens_ill):
    """Gráfico profissional: bem vs mal condicionado (horizontal bars)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    
    categories = ['Bem Condicionado', 'Mal Condicionado']
    rel_dx_values = [sens_well['rel_dx'], sens_ill['rel_dx']]
    rel_db_values = [sens_well['rel_db'], sens_ill['rel_db']]
    
    y_indices = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.barh(
        y_indices - width/2,
        rel_db_values,
        width,
        label='||Δb||/||b|| (Recursos)',
        color=COLORS['success'],
        alpha=0.85,
        edgecolor='white',
        linewidth=1.5,
    )
    
    bars2 = ax.barh(
        y_indices + width/2,
        rel_dx_values,
        width,
        label='||Δx||/||x|| (Áreas)',
        color=COLORS['warning'],
        alpha=0.85,
        edgecolor='white',
        linewidth=1.5,
    )
    
    ax.set_yticks(y_indices)
    ax.set_yticklabels(categories, fontsize=11, fontweight='600')
    ax.set_xlabel('Valor Relativo (log)', fontsize=11, fontweight='600')
    ax.set_title('Comparação de Sensibilidade: Bem vs Mal Condicionado', fontsize=13, fontweight='bold', pad=16)
    ax.set_xscale('log')
    
    # Anotações
    for bar in bars1:
        width_val = bar.get_width()
        ax.text(
            width_val,
            bar.get_y() + bar.get_height()/2.,
            f'{width_val:.2e}',
            ha='left',
            va='center',
            fontsize=9,
            fontweight='500',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.7),
        )
    
    for bar in bars2:
        width_val = bar.get_width()
        ax.text(
            width_val,
            bar.get_y() + bar.get_height()/2.,
            f'{width_val:.2e}',
            ha='left',
            va='center',
            fontsize=9,
            fontweight='500',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.7),
        )
    
    ax.legend(loc='lower right', framealpha=0.95, edgecolor='#E0E0E0', fancybox=False)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Estilo limpo
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_regularization(x_normal, x_reg, crop_labels, lam):
    """Gráfico profissional: normal vs regularizado."""
    fig, ax = plt.subplots(figsize=(9, 5))
    
    x_indices = np.arange(len(crop_labels))
    width = 0.35
    
    bars1 = ax.bar(
        x_indices - width/2,
        x_normal,
        width,
        label='Solução Padrão (LS)',
        color=COLORS['neutral_dark'],
        alpha=0.7,
        edgecolor='white',
        linewidth=1.5,
    )
    
    bars2 = ax.bar(
        x_indices + width/2,
        x_reg,
        width,
        label=f'Regularizada (λ={lam})',
        color=COLORS['primary'],
        alpha=0.85,
        edgecolor='white',
        linewidth=1.5,
    )
    
    ax.set_xticks(x_indices)
    ax.set_xticklabels(crop_labels, fontsize=11, fontweight='600')
    ax.set_ylabel('Área (ha)', fontsize=11, fontweight='600')
    ax.set_title('Sistema Mal Condicionado: Solução Padrão vs Regularizada', 
                 fontsize=13, fontweight='bold', pad=16)
    
    # Anotações
    for bar in bars1:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f'{height:.0f}',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='500',
        )
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f'{height:.0f}',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='500',
        )
    
    ax.legend(loc='upper right', framealpha=0.95, edgecolor='#E0E0E0', fancybox=False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Estilo limpo
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig_to_base64(fig)
