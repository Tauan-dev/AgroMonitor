# AGROMONITOR

<!-- Badges -->

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-%23009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![NumPy](https://img.shields.io/badge/NumPy-%2331323f.svg?logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-%23076aa3.svg?logo=scipy&logoColor=white)](https://www.scipy.org/)
[![Angular](https://img.shields.io/badge/Angular-%23DD0031.svg?logo=angular&logoColor=white)](https://angular.io/)
[![TypeScript](https://img.shields.io/badge/TypeScript-%23007ACC.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Node.js](https://img.shields.io/badge/Node.js-%23339933.svg?logo=node.js&logoColor=white)](https://nodejs.org/)

AgroMonitor é um dashboard web para análise de planejamento agrícola com foco em sensibilidade numérica de modelos de Programação Linear (LP). O sistema ajuda analistas e tomadores de decisão a entenderem a robustez de planos de plantio frente a incertezas em recursos, comparar cenários de lucro e gerar recomendações técnicas automatizadas.

> Visão rápida: Backend em Python/FastAPI (NumPy, SciPy) para resolução numérica e geração de gráficos; Frontend em Angular/TypeScript para interface interativa; módulo de IA para sumarização e recomendações.

---

## Por que usar

- Avalie impacto de pequenas perturbações nos recursos sobre o plano de plantio.
- Calcule o número de condição (κ) para medir estabilidade numérica.
- Compare cenários de lucro: base, pessimista e otimista.
- Aplique regularização de Tikhonov quando necessário.
- Receba resumos executivos e recomendações geradas automaticamente por um módulo de IA.

---

---

## Tecnologias principais

- Backend: Python, FastAPI, NumPy, SciPy, Matplotlib/Pillow
- Frontend: Angular, TypeScript, RxJS
- Dev/Infra: Docker, docker-compose, Node.js, npm, Uvicorn

---

## Estrutura do repositório

```
agricultural-planning/
├─ backend/        # FastAPI + lógica numérica (A, b, profit, análises)
├─ frontend/       # Angular app (UI, SSR optional)
├─ docker-compose.yml
└─ README.md
```

---

## Instalação e execução (desenvolvimento)

> Instruções para Windows (PowerShell). Ajuste comandos para macOS/Linux conforme necessário.

### Backend (FastAPI)

1. Entre na pasta do backend e crie ambiente virtual:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Execute o servidor:

```powershell
uvicorn app.main:app --reload --port 8000
```

O endpoint principal de análise normalmente é: `POST /api/analyze`.

### Frontend (Angular)

1. Instale dependências e rode o dev server:

```powershell
cd frontend
npm install
npx ng serve --open
```

2. Caso a porta 4200 esteja ocupada use outra porta:

```powershell
npx ng serve --port 4300 --open
```

> Dica: se usar SSR, confirme que `main.server.ts` encaminha o `BootstrapContext` para `bootstrapApplication` e que `appConfig` fornece `provideHttpClient()` para evitar erros de injeção (NG0401 / No provider for HttpClient).

---

## Uso básico

1. Abra o frontend e preencha/import os dados do modelo (matriz A, vetores b e profit).
2. Ajuste a `Perturbação Relativa (%)` para simular variações nos recursos.
3. Clique em "Executar Análise". O backend retornará resultados e imagens (base64) com heatmaps e comparações.
4. Leia as métricas técnicas (κ, sensibilidade) e as recomendações geradas pelo módulo de IA.

---

## API (resumo)

- POST /api/analyze
  - Request body: { A: number[][], b: number[], profit: number[], rel_perturb: number, crops?: string[], resources?: string[] }
  - Response: { x_base, profit_base, profit_pert_pessimistic, profit_pert_optimistic, kappa, rel_dx, heatmap, comparison, sensitivity, regularization, diagnostics }

---

## Boas práticas e observações técnicas

- Valores altos de κ indicam perda de estabilidade numérica — use regularização (Tikhonov) para mitigar.
- Prefira servir imagens estáticas em produção com cache apropriado (em vez de base64 inline) para desempenho.
- Em SSR, habilite `withFetch()` no `provideHttpClient()` para melhor compatibilidade no servidor.

---

## Contribuindo

1. Abra uma issue para discutir a feature/bug.
2. Fork e crie branch `feature/descrição` ou `fix/descrição`.
3. Faça commits claros e PR com descrição e screenshots.

---

## Palavras-chave

planiamento agrícola, otimização, programação linear, sensibilidade numérica, Tikhonov, FastAPI, Angular, SciPy, NumPy, dashboard agrícola, análise de sensibilidade

## Licença

MTT License. Veja o arquivo [LICENSE](./LICENSE) para detalhes.

## Contato

Tauan Neres — tnsilva.cic@uesc.br
