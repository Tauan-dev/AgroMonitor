import { TestBed } from '@angular/core/testing';

import { AnalysisInterpreterService } from './analysis-interpreter.service';

describe('AnalysisInterpreterService', () => {
  let service: AnalysisInterpreterService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AnalysisInterpreterService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
