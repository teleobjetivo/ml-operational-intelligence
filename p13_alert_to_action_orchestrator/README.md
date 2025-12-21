# p13 — Orquestación: alerta → acción

**EN title:** Alert-to-Action Orchestrator

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
- Dataset simulado: `data/p13_alert_to_action_orchestrator_data.csv`
- Notebook runnable: `notebooks/p13_alert_to_action_orchestrator.ipynb`
- Figura exportada: `img/p13_alert_to_action_orchestrator_plot.png`

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
