export interface ModelInput {
  resources: string[];
  crops: string[];
  A: number[][];
  b: number[];
  profit: number[];
  rel_perturb: number;
}

export interface AnalysisOutput {
  x_base: number[];
  kappa: number;
  profit_base: number;
  profit_pert: number;
  rel_dx: number;
  rel_db: number;
  bound: number;
  heatmap: string;
  comparison: string;
  sensitivity: string;
  regularization: string;
  diagnostics: {
    kappa_well?: number;
    kappa_ill?: number;
    rel_dx_well?: number;
    rel_dx_ill?: number;
  };
}

