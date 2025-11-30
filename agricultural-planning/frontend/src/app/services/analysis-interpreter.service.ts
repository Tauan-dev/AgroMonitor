import { Injectable } from '@angular/core';
import { AnalysisOutput } from '../models/analysis.model';

export interface InterpretedAnalysis {
  summary: string;
  dataScienceInsight: string;
  agriculturalContext: string;
  predictiveDiagnosis: string;
  recommendations: string[];
  riskFlags: RiskFlag[];
}

interface RiskFlag {
  level: 'critical' | 'warning' | 'info';
  message: string;
  affectedCrops?: string[];
}

@Injectable({
  providedIn: 'root',
})
export class AnalysisInterpreterService {
  interpret(
    result: AnalysisOutput,
    crops: string[],
    resources: string[]
  ): InterpretedAnalysis {
    const kappa = result.kappa;
    const relDx = result.rel_dx;
    const relDb = result.rel_db ?? 0;
    const profitBase = result.profit_base;
    const diagnostics = result.diagnostics ?? {};

    return {
      summary: this.generateSummary(
        kappa,
        relDx,
        profitBase,
        result.profit_pert_pessimistic,
        result.profit_pert_optimistic
      ),
      dataScienceInsight: this.generateDataScienceInsight(
        kappa,
        relDx,
        relDb,
        diagnostics
      ),
      agriculturalContext: this.generateAgriculturalContext(crops, result),
      predictiveDiagnosis: this.generatePredictiveDiagnosis(
        kappa,
        relDx,
        profitBase,
        result.profit_pert_pessimistic
      ),
      recommendations: this.generateRecommendations(kappa, relDx, result),
      riskFlags: this.identifyRiskFlags(kappa, relDx, result),
    };
  }

  private calculateElasticity(profitBase: number, profitPert: number): number {
    if (profitBase === 0) return 0;
    return Math.abs((profitPert - profitBase) / profitBase) * 100;
  }

  private generateSummary(
    kappa: number,
    relDx: number,
    profitBase: number,
    profitPessimistic: number,
    profitOptimistic: number
  ): string {
    let conditionText = '';
    if (kappa < 1e2) conditionText = 'bem condicionado e estável';
    else if (kappa < 1e4)
      conditionText = 'moderadamente condicionado com sensibilidade moderada';
    else
      conditionText = 'mal condicionado com alta sensibilidade a perturbações';

    const pessimisticImpact = (
      ((profitBase - profitPessimistic) / profitBase) *
      100
    ).toFixed(1);
    const optimisticGain = (
      ((profitOptimistic - profitBase) / profitBase) *
      100
    ).toFixed(1);

    return (
      `O sistema está ${conditionText}. ` +
      `Cenário Base: R$ ${profitBase.toFixed(2)} | ` +
      `Cenário Pessimista (-${relDx * 100}%): -${pessimisticImpact}% | ` +
      `Cenário Otimista (+${relDx * 100}%): +${optimisticGain}%.`
    );
  }

  private generateDataScienceInsight(
    kappa: number,
    relDx: number,
    relDb: number,
    diagnostics: any
  ): string {
    const kappaWell = diagnostics?.kappa_well || 0;
    const kappaIll = diagnostics?.kappa_ill || 0;
    const ratioCondition = kappaIll / (kappaWell + 1e-10);

    let insight = `**Número de Condição (κ = ${kappa.toExponential(2)})**: `;

    if (kappa < 1e2) {
      insight +=
        'O sistema é numericamente estável. Pequenas perturbações em **b** resultam em pequenas mudanças em **x**. ';
    } else if (kappa < 1e4) {
      insight +=
        'O sistema tem instabilidade moderada. A propagação de erro é controlada, mas requer atenção em decisões críticas. ';
    } else {
      insight +=
        'O sistema é numericamente frágil. Erros pequenos em recursos podem amplificar significativamente as soluções. ';
    }

    insight += `\n\n**Elasticidade: ||Δx||/||x|| = ${relDx.toExponential(
      2
    )}**: `;
    insight += `Uma mudança de 1% nos recursos causa aproximadamente ${(
      relDx * 100
    ).toFixed(2)}% de mudança nas áreas plantadas. `;

    insight +=
      `\n\n**Comparação Bem vs Mal Condicionado**: Sistema bem condicionado (κ=${kappaWell.toExponential(
        2
      )}) ` +
      `vs sistema mal condicionado (κ=${kappaIll.toExponential(
        2
      )}). Razão: ${ratioCondition.toFixed(1)}x. ` +
      `Seu sistema é ${
        ratioCondition > 100
          ? 'significativamente mais sensível'
          : 'razoavelmente estável'
      } ` +
      `em comparação ao pior caso.`;

    return insight;
  }

  private generateAgriculturalContext(
    crops: string[],
    result: AnalysisOutput
  ): string {
    return (
      `**Interpretação Agrícola**: \n\n` +
      `O plano otimizado sugere alocação de áreas baseado no retorno marginal de cada cultura sob os recursos ` +
      `disponíveis (terra, mão de obra, água, fertilizante). \n\n` +
      `A sensibilidade observada (${result.rel_dx.toExponential(
        2
      )}) reflete como o mix de culturas reage a ` +
      `flutuações em oferta de insumos — comum em agricultura onde clima, disponibilidade de água e custos de ` +
      `fertilizante variam sazonalmente. \n\n` +
      `Culturas com maior peso na matriz de sensibilidade são aquelas mais críticas para a estabilidade do plano.`
    );
  }

  private generatePredictiveDiagnosis(
    kappa: number,
    relDx: number,
    profitBase: number,
    profitPertPessimistic: number
  ): string {
    let diagnosis = `**Diagnóstico Preditivo**:\n\n`;

    // compute elasticity in percent between base and pessimistic profit
    const elasticityPercent = this.calculateElasticity(
      profitBase,
      profitPertPessimistic
    );

    if (kappa < 1e2) {
      diagnosis += `✓ **Tendência**: Sistema previsível e robusto. Comportamento linear esperado em perturbações até ~10-15%.\n`;
      diagnosis += `✓ **Projeção**: Reduções de 5% em recursos devem resultar em redução ~${(
        relDx * 5
      ).toFixed(2)}% nas áreas.\n`;
    } else if (kappa < 1e4) {
      diagnosis += `⚠ **Tendência**: Instabilidade moderada. Comportamento linear mantém-se até ~5-8% de perturbação.\n`;
      diagnosis += `⚠ **Projeção**: Reduções de 5% em recursos podem resultar em redução ${(
        relDx *
        5 *
        1.5
      ).toFixed(2)}% a ${(relDx * 5 * 2).toFixed(
        2
      )}% nas áreas (amplificação de erro).\n`;
    } else {
      diagnosis += `🔴 **Tendência**: Sistema frágil. Comportamento linear pode quebrar rapidamente com perturbações > 2-3%.\n`;
      diagnosis += `🔴 **Projeção**: Pequenas mudanças em insumos podem causar mudanças desproporcionais e impredizíveis no plano.\n`;
    }

    diagnosis += `\n**Intervalo de Risco Aproximado**: Perturbações até ${Math.min(
      10,
      Math.max(2, 100 / kappa)
    ).toFixed(1)}% são seguras para planejamento linear.`;

    diagnosis += `\n\n**Elasticidade de Lucro (pessimista vs base)**: ${elasticityPercent.toFixed(
      2
    )}% de variação no lucro entre o cenário base e o pessimistico.`;

    return diagnosis;
  }

  private generateRecommendations(
    kappa: number,
    relDx: number,
    result: AnalysisOutput
  ): string[] {
    const recommendations: string[] = [];

    if (kappa < 1e2) {
      recommendations.push(
        '✓ Plano é robusto: considere implementá-lo com confiança.'
      );
      recommendations.push(
        '✓ Monitorar recursos em margem de ±10% sem necessidade de replanejar frequentemente.'
      );
    } else if (kappa < 1e4) {
      recommendations.push(
        '⚠ Implementar com controle: revisar plano se recursos deviarem > 5%.'
      );
      recommendations.push(
        '⚠ Priorizar estabilidade de insumos críticos (especialmente água e fertilizante).'
      );
      recommendations.push(
        '⚠ Considerar regularização (Tikhonov) para reduzir sensibilidade numérica.'
      );
    } else {
      recommendations.push(
        '🔴 Usar com cautela: sistema é sensível e requer ajustes frequentes.'
      );
      recommendations.push(
        '🔴 Implementar diversificação de culturas para reduzir dependência em recursos críticos.'
      );
      recommendations.push(
        '🔴 Considerar reservas estratégicas de insumos (5-10% acima do planejado).'
      );
      recommendations.push(
        '🔴 Revisar dados de entrada: matriz A pode estar mal condicionada; validar consumos por cultura.'
      );
    }

    recommendations.push(
      `📊 Sensibilidade atual: mudança de 1% em recursos → ${(
        relDx * 100
      ).toFixed(2)}% mudança em áreas.`
    );

    return recommendations;
  }

  private identifyRiskFlags(
    kappa: number,
    relDx: number,
    result: AnalysisOutput
  ): RiskFlag[] {
    const flags: RiskFlag[] = [];

    if (kappa > 1e4) {
      flags.push({
        level: 'critical',
        message:
          'Sistema extremamente sensível. Erros numéricos podem comprometer a solução.',
      });
    }

    if (
      result.profit_pert_pessimistic / result.profit_base < 0.5 &&
      result.profit_pert_pessimistic > 0
    ) {
      flags.push({
        level: 'warning',
        message:
          'Perturbação de recursos resulta em redução > 50% do lucro. Plano é vulnerável.',
      });
    }

    if (relDx > 1.0) {
      flags.push({
        level: 'warning',
        message:
          'Elasticidade alta (>1.0): mudanças pequenas em recursos causam mudanças proporcionalmente maiores em áreas.',
      });
    }

    if (result.profit_pert_pessimistic < 0) {
      flags.push({
        level: 'critical',
        message:
          'Lucro negativo sob perturbação. Plano não é viável com essa variação de recursos.',
      });
    }

    return flags;
  }
}
