import {
  Component,
  Pipe,
  PipeTransform,
  ViewEncapsulation,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { trigger, transition, style, animate } from '@angular/animations';

import { AnalysisService } from '../../services/analysis.service';
import {
  AnalysisInterpreterService,
  InterpretedAnalysis,
} from '../../services/analysis-interpreter.service';
import { ModelInput, AnalysisOutput } from '../../models/analysis.model';

/* ========= PIPE STANDALONE PARA HTML SEGURO ========= */
@Pipe({
  name: 'safe',
  standalone: true,
})
export class SafePipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}

  transform(value: string | null | undefined): SafeHtml {
    if (!value) return '';
    return this.sanitizer.bypassSecurityTrustHtml(value);
  }
}

/* ========= COMPONENTE STANDALONE PRINCIPAL ========= */
@Component({
  selector: 'app-analysis',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, SafePipe],
  templateUrl: './analysis.component.html',
  styleUrls: ['./analysis.component.css'],
  encapsulation: ViewEncapsulation.None,
  animations: [
    trigger('fadeIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(10px)' }),
        animate(
          '300ms ease-out',
          style({ opacity: 1, transform: 'translateY(0)' })
        ),
      ]),
    ]),
    trigger('slideIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateX(-20px)' }),
        animate(
          '500ms ease-out',
          style({ opacity: 1, transform: 'translateX(0)' })
        ),
      ]),
    ]),
  ],
})
export class AnalysisComponent {
  // ===== NAVEGAÇÃO =====
  showAnalysis: boolean = false;

  // ===== ESTADO DA ANÁLISE =====
  loading: boolean = false;
  result: AnalysisOutput | null = null;
  error: string | null = null;
  interpretedResult: InterpretedAnalysis | null = null;

  // ===== DADOS DE ENTRADA DO MODELO =====
  input: ModelInput = {
    resources: ['Terra', 'Mão de obra', 'Água', 'Fertilizante'],
    crops: ['Milho', 'Soja', 'Trigo'],
    A: [
      [1.0, 1.0, 1.0],
      [10.0, 8.0, 12.0],
      [3000.0, 2500.0, 1500.0],
      [150.0, 120.0, 100.0],
    ],
    b: [100.0, 900.0, 220000.0, 12000.0],
    profit: [3000.0, 2800.0, 2000.0],
    rel_perturb: 0.05,
  };

  constructor(
    private analysisService: AnalysisService,
    private interpreterService: AnalysisInterpreterService
  ) {
    console.log('✅ AnalysisComponent inicializado');
  }

  // ===== MÉTODOS DE NAVEGAÇÃO =====

  /**
   * Navega para a página de análise
   */
  startAnalysis(): void {
    this.showAnalysis = true;
    console.log('🚀 Navegando para análise...');
    window.scrollTo(0, 0);
  }

  /**
   * Volta para a landing page
   */
  backToLanding(): void {
    this.showAnalysis = false;
    this.clearResults();
    console.log('⬅️ Voltando para landing page...');
    window.scrollTo(0, 0);
  }

  // ===== MÉTODOS DE ANÁLISE =====

  /**
   * Executa a análise chamando o backend
   */
  analyze(): void {
    this.loading = true;
    this.error = null;
    this.interpretedResult = null;

    console.log('🔬 Iniciando análise com dados:', this.input);

    this.analysisService.analyze(this.input).subscribe({
      next: (data: AnalysisOutput) => {
        console.log('✅ Resposta da API recebida:', data);
        this.result = data;

        // Gera insights interpretados
        this.interpretedResult = this.interpreterService.interpret(
          data,
          this.input.crops,
          this.input.resources
        );
        console.log(
          '✅ Interpretação gerada com sucesso:',
          this.interpretedResult
        );

        this.loading = false;
      },
      error: (err) => {
        console.error('❌ Erro na API:', err);
        this.error =
          err.error?.detail ||
          err.message ||
          'Erro ao conectar com o servidor. Verifique se o backend está rodando em http://localhost:8000';
        this.loading = false;
      },
      complete: () => {
        console.log('✅ Análise concluída com sucesso');
      },
    });
  }

  /**
   * Atualiza o valor da perturbação relativa
   */
  updatePerturbation(value: string): void {
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue >= 0.01 && numValue <= 0.3) {
      this.input.rel_perturb = numValue;
      console.log(
        `📊 Perturbação atualizada para: ${(numValue * 100).toFixed(1)}%`
      );
    }
  }

  /**
   * Verifica se há resultados disponíveis
   */
  get hasResult(): boolean {
    return this.result !== null;
  }

  /**
   * Limpa todos os resultados e erros
   */
  clearResults(): void {
    this.result = null;
    this.interpretedResult = null;
    this.error = null;
    console.log('🧹 Resultados limpos');
  }
}
