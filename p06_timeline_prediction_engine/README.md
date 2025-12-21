# p06 — Predicción de fechas/atrasos con timeline

**EN title:** Timeline Prediction Engine

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
- Dataset simulado: `data/p06_timeline_prediction_engine_data.csv`
- Notebook runnable: `notebooks/p06_timeline_prediction_engine.ipynb`
- Figura exportada: `img/p06_timeline_prediction_engine_plot.png`

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
