#!/usr/bin/env python3
"""
regen_project_readmes.py
Genera/actualiza README.md por proyecto (pXX_*) manteniendo diagramas existentes.

Uso:
  python3 regen_project_readmes.py --repo "/ruta/al/repo" --overwrite

Por defecto, busca proyectos con patrón: p??_* (directorios) en la raíz del repo.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path
from typing import Optional, Dict, Tuple, List

# --- Catálogo de proyectos (V1) ---
# Ajusta títulos/descripciones aquí si quieres afinar.
PROJECTS: Dict[str, Dict[str, str]] = {
    "p01_event_early_warning": {
        "title_es": "P01 — Event Early Warning: Detección temprana de anomalías",
        "subtitle_es": "Monitoreo de señales y alertas tempranas para anticipar eventos operacionales.",
        "title_en": "P01 — Event Early Warning: Early anomaly detection",
        "subtitle_en": "Signal monitoring and early alerts to anticipate operational events.",
        "demo_es": "Genera una serie temporal simulada con eventos anómalos, detecta puntos fuera de patrón y produce una alerta simple + figura.",
        "demo_en": "Generates a simulated time series with injected anomalies, detects out-of-pattern points, and outputs a simple alert + figure.",
    },
    "p02_risk_scoring_evolutivo": {
        "title_es": "P02 — Risk Scoring Evolutivo: Riesgo dinámico en el tiempo",
        "subtitle_es": "Score de riesgo que cambia según comportamiento reciente y drift.",
        "title_en": "P02 — Evolutionary Risk Scoring: Dynamic risk over time",
        "subtitle_en": "A risk score that adapts with recent behavior and drift signals.",
        "demo_es": "Simula features y un target de riesgo; entrena un modelo base y muestra cómo el score cambia por ventanas temporales.",
        "demo_en": "Simulates features and a risk target; trains a baseline model and shows how scoring changes across rolling windows.",
    },
    "p03_operational_state_classifier": {
        "title_es": "P03 — Clasificación de estados operacionales",
        "subtitle_es": "Clasifica estados (Normal / Alerta / Crítico) a partir de variables y umbrales/modelo.",
        "title_en": "P03 — Operational state classification",
        "subtitle_en": "Classifies states (Normal / Warning / Critical) from variables using thresholds/model.",
        "demo_es": "Construye etiquetas de estado y entrena un clasificador simple, entregando matriz de confusión y gráfico.",
        "demo_en": "Builds state labels and trains a simple classifier, producing a confusion matrix and plot.",
    },
    "p04_demand_forecast_activation": {
        "title_es": "P04 — Predicción de demanda con activación",
        "subtitle_es": "Forecast + regla de activación (acciones/alertas) según umbrales.",
        "title_en": "P04 — Demand forecasting with activation",
        "subtitle_en": "Forecast + activation rule (actions/alerts) based on thresholds.",
        "demo_es": "Genera demanda simulada; pronostica y dispara una ‘acción’ cuando el forecast supera un umbral.",
        "demo_en": "Generates simulated demand; forecasts and triggers an ‘action’ when forecast crosses a threshold.",
    },
    "p05_situation_detector": {
        "title_es": "P05 — Machine Learning para ‘situaciones’",
        "subtitle_es": "Detecta patrones compuestos (‘situaciones’) combinando señales y contexto.",
        "title_en": "P05 — ML for ‘situations’",
        "subtitle_en": "Detects composite patterns (‘situations’) combining signals and context.",
        "demo_es": "Define reglas/labels de situación y entrena un modelo para predecir ocurrencia; genera explicación simple.",
        "demo_en": "Defines situation rules/labels and trains a model to predict occurrence; outputs a simple explanation.",
    },
    "p06_timeline_prediction_engine": {
        "title_es": "P06 — Timeline Prediction Engine",
        "subtitle_es": "Predice cuándo ocurrirá un hito (ETA) a partir de historial y señales.",
        "title_en": "P06 — Timeline Prediction Engine",
        "subtitle_en": "Predicts when a milestone will happen (ETA) based on history and signals.",
        "demo_es": "Simula tiempos entre hitos; ajusta un modelo simple para estimar ETA y muestra error vs baseline.",
        "demo_en": "Simulates time-to-milestone; fits a simple model for ETA and shows error vs baseline.",
    },
    "p07_trend_atlas": {
        "title_es": "P07 — Atlas de Tendencias",
        "subtitle_es": "Agrupa series/variables y sintetiza tendencias en lenguaje ejecutivo.",
        "title_en": "P07 — Trend Atlas",
        "subtitle_en": "Clusters series/variables and summarizes trends in executive language.",
        "demo_es": "Calcula features de tendencia, agrupa con clustering y genera un mini ‘atlas’ de clusters + gráficos.",
        "demo_en": "Computes trend features, clusters them, and generates a mini ‘atlas’ of clusters + plots.",
    },
    "p08_data_quality_sentinel": {
        "title_es": "P08 — Data Quality Sentinel",
        "subtitle_es": "Vigilante de calidad: nulos, outliers, cambios de esquema y reglas.",
        "title_en": "P08 — Data Quality Sentinel",
        "subtitle_en": "Quality guard: nulls, outliers, schema changes, and rules.",
        "demo_es": "Perfila un dataset simulado, aplica reglas, y emite un reporte de hallazgos con severidad.",
        "demo_en": "Profiles a simulated dataset, applies rules, and outputs a findings report with severity.",
    },
    "p09_model_drift_monitor": {
        "title_es": "P09 — Model Drift Monitor",
        "subtitle_es": "Monitorea drift de datos/modelo para mantener performance.",
        "title_en": "P09 — Model Drift Monitor",
        "subtitle_en": "Monitors data/model drift to keep performance stable.",
        "demo_es": "Simula drift; compara distribuciones y reporta alertas (PSI/estadísticos simples).",
        "demo_en": "Simulates drift; compares distributions and reports alerts (PSI/simple stats).",
    },
    "p10_root_cause_suggester": {
        "title_es": "P10 — Root Cause Suggester",
        "subtitle_es": "Sugiere causas probables cuando hay anomalía (features relevantes).",
        "title_en": "P10 — Root Cause Suggester",
        "subtitle_en": "Suggests likely causes when anomalies occur (important features).",
        "demo_es": "Genera un evento; usa importancia de variables/reglas para proponer hipótesis de causa.",
        "demo_en": "Generates an event; uses feature importance/rules to propose root-cause hypotheses.",
    },
    "p11_ticket_triage_automl": {
        "title_es": "P11 — Ticket Triage (AutoML-lite)",
        "subtitle_es": "Prioriza y enruta tickets con clasificación ligera y reglas.",
        "title_en": "P11 — Ticket Triage (AutoML-lite)",
        "subtitle_en": "Prioritizes and routes tickets via lightweight classification and rules.",
        "demo_es": "Simula tickets; clasifica prioridad; sugiere equipo y SLA; genera tabla de salida.",
        "demo_en": "Simulates tickets; predicts priority; suggests team and SLA; outputs a table.",
    },
    "p12_kpi_narrative_generator": {
        "title_es": "P12 — KPI Narrative Generator",
        "subtitle_es": "Convierte KPIs en narrativa ejecutiva: ‘qué pasó y por qué importa’.",
        "title_en": "P12 — KPI Narrative Generator",
        "subtitle_en": "Turns KPIs into executive narrative: ‘what happened and why it matters’.",
        "demo_es": "Calcula KPIs de ejemplo y genera un texto estructurado con insights y riesgos.",
        "demo_en": "Computes sample KPIs and generates a structured text with insights and risks.",
    },
    "p13_alert_to_action_orchestrator": {
        "title_es": "P13 — Alert-to-Action Orchestrator",
        "subtitle_es": "Orquesta alertas → acciones (simuladas) con reglas y cola simple.",
        "title_en": "P13 — Alert-to-Action Orchestrator",
        "subtitle_en": "Orchestrates alerts → (simulated) actions via rules and a simple queue.",
        "demo_es": "Toma alertas del detector, aplica reglas y genera un ‘plan de acción’ con prioridad.",
        "demo_en": "Consumes detector alerts, applies rules, and outputs an ‘action plan’ with priority.",
    },
    "p14_executive_demo_dashboard": {
        "title_es": "P14 — Executive Demo Dashboard",
        "subtitle_es": "Dashboard HTML simple que junta resultados clave y figuras del repo.",
        "title_en": "P14 — Executive Demo Dashboard",
        "subtitle_en": "A simple HTML dashboard aggregating key results and plots from the repo.",
        "demo_es": "Genera un HTML local con KPIs y enlaces a outputs para demo de entrevista.",
        "demo_en": "Generates a local HTML with KPIs and links to outputs for interview demos.",
    },
}

STANDARD_SECTIONS_ES = [
    "Resumen",
    "Por qué hice este proyecto",
    "Qué demuestra (en trabajo real)",
    "Arquitectura / Flujo",
    "Estructura del proyecto",
    "Qué hace cada archivo",
    "Instalación",
    "Ejecución",
    "Entradas y salidas",
    "Metodología (resumen técnico)",
    "Resultados esperables / cómo interpretar",
    "Contacto & Presencia Online",
]

STANDARD_SECTIONS_EN = [
    "Summary",
    "Why I built this",
    "What this demonstrates (real work)",
    "Architecture / Flow",
    "Project structure",
    "What each file does",
    "Setup",
    "Run",
    "Inputs & outputs",
    "Method (technical summary)",
    "Expected results / how to interpret",
    "Contact & Online Presence",
]


def find_diagram(project_dir: Path) -> Optional[Path]:
    """Find a diagram image file to embed, preferring flow/diagram named assets."""
    candidates: List[Path] = []
    for sub in ["img", "images", "figures"]:
        d = project_dir / sub
        if d.is_dir():
            for ext in ("*.png", "*.svg", "*.jpg", "*.jpeg", "*.webp"):
                candidates.extend(sorted(d.glob(ext)))
    if not candidates:
        return None

    def score(p: Path) -> Tuple[int, int]:
        name = p.name.lower()
        s = 0
        if "flow" in name or "diagram" in name or "arch" in name:
            s += 5
        if "pipeline" in name:
            s += 3
        if name.endswith(".svg"):
            s += 2
        # prefer shorter names and deterministic order
        return (-s, len(name))

    return sorted(candidates, key=score)[0]


def list_structure(project_dir: Path) -> str:
    """Return a short structure snippet like data/, notebooks/, img/, outputs/, src/ if present."""
    parts = []
    for name in ["data", "notebooks", "img", "outputs", "src", "paper"]:
        p = project_dir / name
        if p.exists():
            parts.append(f"- `{name}/`")
    if not parts:
        return "- (estructura mínima)"
    return "\n".join(parts)


def summarize_files(project_dir: Path) -> str:
    """List key files if present (not exhaustive)."""
    items = []
    # common files
    for rel in [
        "notebooks",
        "src",
        "data/DATA_DICTIONARY.md",
        "outputs/OUTPUTS_DICTIONARY.md",
        "README.md",
    ]:
        p = project_dir / rel
        if p.exists():
            items.append(f"- `{rel}`")
    # add main notebook if any
    nb_dir = project_dir / "notebooks"
    if nb_dir.is_dir():
        nbs = sorted(nb_dir.glob("*.ipynb"))
        for nb in nbs[:3]:
            items.append(f"- `notebooks/{nb.name}`")
    return "\n".join(dict.fromkeys(items)) if items else "- (pendiente)"


def read_project_local_dict(project_dir: Path) -> str:
    dd = project_dir / "data" / "DATA_DICTIONARY.md"
    if dd.exists():
        return "`data/DATA_DICTIONARY.md`"
    return "(no encontrado)"


def read_project_outputs_dict(project_dir: Path) -> str:
    od = project_dir / "outputs" / "OUTPUTS_DICTIONARY.md"
    if od.exists():
        return "`outputs/OUTPUTS_DICTIONARY.md`"
    return "(no encontrado)"


def render_readme(project_dir: Path, lang: str) -> str:
    slug = project_dir.name
    meta = PROJECTS.get(slug)
    if not meta:
        # fallback
        meta = {
            "title_es": f"{slug}",
            "subtitle_es": "Proyecto ejecutable y reproducible.",
            "title_en": f"{slug}",
            "subtitle_en": "Executable and reproducible project.",
            "demo_es": "Demo V1 con datos simulados.",
            "demo_en": "V1 demo with simulated data.",
        }

    diagram = find_diagram(project_dir)
    diagram_md = ""
    if diagram:
        rel = diagram.relative_to(project_dir).as_posix()
        diagram_md = f"![{slug} – diagram]({rel})"

    year = dt.datetime.now().year

    # --- Spanish block ---
    es = f"""# {meta['title_es']}

_{meta['subtitle_es']}_

## Resumen

Soy Hugo Baghetti. {meta['demo_es']}

## Por qué hice este proyecto

En escenarios reales, detectar cambios a tiempo reduce costo operacional, evita incidentes y mejora la toma de decisiones.
Este proyecto es una demo **reproducible** (V1) orientada a entrevistas y portafolio.

## Qué demuestra (en trabajo real)

- Diseño de un flujo analítico simple (datos → modelo/reglas → métricas → salida).
- Pensamiento operacional: alertas, umbrales, priorización y trazabilidad.
- Documentación y estructura de proyecto lista para escalar (V2+).

## 🧠 Arquitectura / Flujo

{diagram_md if diagram_md else "_(Diagrama pendiente — deja un PNG/SVG en `img/` o `figures/`)_"} 

## Estructura del proyecto

{list_structure(project_dir)}

## Qué hace cada archivo

{summarize_files(project_dir)}

## Instalación

Desde la **raíz del repo**:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

## Ejecución

- **Notebooks**: abre el notebook en `notebooks/` (VS Code o Jupyter).
- **Scripts** (si existen): ejecuta `python src/<script>.py`.

Ejemplo (si usas Jupyter):

```bash
jupyter notebook
```

## Entradas y salidas

- Diccionario de entradas: {read_project_local_dict(project_dir)}
- Diccionario de salidas: {read_project_outputs_dict(project_dir)}

Además, a nivel repositorio:
- `DATA_DICTIONARY.md`
- `OUTPUTS_DICTIONARY.md`

## Metodología (resumen técnico)

V1 usa datos simulados para reproducibilidad. En V2 se reemplaza por datos reales/abiertos del dominio del proyecto y se agregan:
- validación cruzada / backtesting,
- métricas de negocio,
- monitoreo (drift / calidad).

## Resultados esperables / cómo interpretar

- Verás una figura principal en `img/` y/o tablas en `outputs/`.
- El foco es explicar **qué detectamos**, **por qué**, y **qué acción dispararías**.

## Contacto & Presencia Online

- 📧 `teleobjetivo.boutique@gmail.com`
- 🌐 `www.teleobjetivo.cl`
- 📸 IG: `@tele.objetivo`
- 💻 GitHub: `https://github.com/teleobjetivo`

---
"""

    if lang.lower() == "es":
        return es.strip() + "\n"

    # --- English block ---
    en = f"""# {meta['title_en']}

_{meta['subtitle_en']}_

## Summary

I'm Hugo Baghetti. {meta['demo_en']}

## Why I built this

In real operations, detecting changes early reduces cost, prevents incidents, and improves decision-making.
This is a **reproducible** V1 demo for interviews and portfolio.

## What this demonstrates (real work)

- A simple analytics flow (data → model/rules → metrics → output).
- Operational thinking: alerts, thresholds, prioritization, and traceability.
- A project structure ready to scale (V2+).

## 🧠 Architecture / Flow

{diagram_md if diagram_md else "_(Diagram pending — add a PNG/SVG into `img/` or `figures/`)_"} 

## Project structure

{list_structure(project_dir)}

## What each file does

{summarize_files(project_dir)}

## Setup

From the **repo root**:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

## Run

- **Notebooks**: open the notebook in `notebooks/` (VS Code or Jupyter).
- **Scripts** (if any): run `python src/<script>.py`.

If you use Jupyter:

```bash
jupyter notebook
```

## Inputs & outputs

- Input dictionary: {read_project_local_dict(project_dir)}
- Output dictionary: {read_project_outputs_dict(project_dir)}

Repo-level contracts:
- `DATA_DICTIONARY.md`
- `OUTPUTS_DICTIONARY.md`

## Method (technical summary)

V1 uses simulated data for reproducibility. V2 replaces it with real/open domain data and adds:
- cross-validation / backtesting,
- business metrics,
- monitoring (drift / data quality).

## Expected results / how to interpret

- You'll get a main plot in `img/` and/or tables in `outputs/`.
- The goal is to explain **what was detected**, **why**, and **what action you'd trigger**.

## Contact & Online Presence

- 📧 `teleobjetivo.boutique@gmail.com`
- 🌐 `www.teleobjetivo.cl`
- 📸 IG: `@tele.objetivo`
- 💻 GitHub: `https://github.com/teleobjetivo`

"""
    return (es + "\n" + en).strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Ruta al repo (raíz)")
    ap.add_argument("--lang", default="es+en", choices=["es", "en", "es+en"], help="Idioma del README por proyecto")
    ap.add_argument("--overwrite", action="store_true", help="Sobrescribir README.md existentes")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists():
        raise SystemExit(f"Repo no existe: {repo}")

    projects = sorted([p for p in repo.iterdir() if p.is_dir() and re.match(r"^p\d\d_", p.name)])
    if not projects:
        raise SystemExit("No encontré proyectos con patrón p??_* en la raíz del repo.")

    changed = 0
    for p in projects:
        out = p / "README.md"
        if out.exists() and not args.overwrite:
            continue
        content = render_readme(p, args.lang)
        out.write_text(content, encoding="utf-8")
        changed += 1

    print(f"OK — READMEs generados/actualizados: {changed}/{len(projects)} (lang={args.lang})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
