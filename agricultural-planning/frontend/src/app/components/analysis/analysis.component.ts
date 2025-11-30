import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { DomSanitizer } from '@angular/platform-browser';
import { AnalysisService } from '../../services/analysis.service';
import {
  AnalysisInterpreterService,
  InterpretedAnalysis,
} from '../../services/analysis-interpreter.service';
import { ModelInput, AnalysisOutput } from '../../models/analysis.model';

// Pipe para renderizar HTML seguro
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'safe',
  standalone: true,
})
export class SafePipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}
  transform(value: string) {
    return this.sanitizer.bypassSecurityTrustHtml(value);
  }
}

@Component({
  selector: 'app-analysis',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, SafePipe],
  templateUrl: './analysis.component.html',
  styleUrls: ['./analysis.component.css'],
})
export class AnalysisComponent {
  loading = false;
  result: AnalysisOutput | null = null;
  error: string | null = null;
  interpretedResult: InterpretedAnalysis | null = null;

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
  ) {}

  analyze(): void {
    this.loading = true;
    this.error = null;
    this.interpretedResult = null;

    this.analysisService.analyze(this.input).subscribe(
      (data) => {
        console.log('API Response:', data);
        this.result = data;

        // NOVO: Interpretar resultados com Ciência de Dados
        this.interpretedResult = this.interpreterService.interpret(
          data,
          this.input.crops,
          this.input.resources
        );
        console.log('Interpretação:', this.interpretedResult);

        this.loading = false;
      },
      (err) => {
        console.error('API Error:', err);
        this.error = err.error?.detail || 'Erro na análise';
        this.loading = false;
      }
    );
  }

  updatePerturbation(value: string): void {
    this.input.rel_perturb = parseFloat(value);
  }

  get hasResult(): boolean {
    return this.result !== null;
  }
}
