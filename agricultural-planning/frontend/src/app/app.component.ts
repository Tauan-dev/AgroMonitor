import { Component } from '@angular/core';
import { AnalysisComponent } from './components/analysis/analysis.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [AnalysisComponent],
  template: `<app-analysis></app-analysis>`,
})
export class AppComponent {}
