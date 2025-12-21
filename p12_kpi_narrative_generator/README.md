# p12 — Generador de narrativa ejecutiva para KPIs

**EN title:** KPI Narrative Generator

```mermaid
flowchart TD
  A[Ingest / Load Data] --> B[Validate / Clean]
  B --> C[Feature Engineering]
  C --> D[Model / Logic]
  D --> E[Insights + Plot]
  E --> F[Export: CSV/PNG/HTML]
  F --> G[README: Explain to recruiter]
```


## Objetivo (ES)
Crear una demo **ejecutable** que muestre un flujo completo: datos → features → lógica/modelo → salida (gráfico/artefacto) → explicación.

## Qué incluye
- Dataset simulado: `data/p12_kpi_narrative_generator_data.csv`
- Notebook runnable: `notebooks/p12_kpi_narrative_generator.ipynb`
- Figura exportada: `img/p12_kpi_narrative_generator_plot.png`

## Cómo ejecutar
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

---

# EN — Goal
Build a **runnable** demo: data → features → model/logic → outputs (plot/artifact) → recruiter-ready narrative.
