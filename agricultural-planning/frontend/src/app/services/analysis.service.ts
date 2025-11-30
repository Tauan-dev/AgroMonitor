import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ModelInput, AnalysisOutput } from '../models/analysis.model';

@Injectable({
  providedIn: 'root',
})
export class AnalysisService {
  // use o backend FastAPI na porta 8000
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  analyze(input: ModelInput): Observable<AnalysisOutput> {
    return this.http.post<AnalysisOutput>(`${this.apiUrl}/analyze`, input);
  }
}
