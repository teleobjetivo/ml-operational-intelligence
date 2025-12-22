#!/usr/bin/env python3
"""
fix_readmes_diagrams.py
Reemplaza imágenes *_plot.png usadas como "diagrama" por diagramas Mermaid (flowchart).
GitHub renderiza Mermaid automáticamente.

Uso:
  python3 fix_readmes_diagrams.py --repo /path/to/ml-operational-intelligence
"""
from __future__ import annotations
import argparse, re
from pathlib import Path

MERMAID = {
  "p01_event_early_warning": "flowchart LR\n  A[Input: events.csv] --> B[Feature engineering]\n  B --> C[Baseline model / thresholds]\n  C --> D[Early warning score]\n  D --> E{Alert?}\n  E -- yes --> F[Create alert + context]\n  E -- no --> G[Store score]\n  F --> H[Outputs: alerts.csv + report]\n  G --> H\n",
  "p02_risk_scoring_evolutivo": "flowchart LR\n  A[Input: entities.csv + history.csv] --> B[Windowing / time features]\n  B --> C[Train / update model]\n  C --> D[Score (risk_t)]\n  D --> E[Calibration + segments]\n  E --> F{Threshold crossed?}\n  F -- yes --> G[Trigger action plan]\n  F -- no --> H[Monitoring]\n  G --> I[Outputs: scores.csv + actions.csv]\n  H --> I\n",
  "p03_operational_state_classifier": "flowchart LR\n  A[Input: sensor_ops.csv] --> B[Clean + resample]\n  B --> C[Label/State definition]\n  C --> D[Classifier training]\n  D --> E[State prediction]\n  E --> F[Confusion + metrics]\n  F --> G[Outputs: states.csv + metrics.json]\n",
  "p04_demand_forecast_activation": "flowchart LR\n  A[Input: demand_timeseries.csv] --> B[Split train/test]\n  B --> C[Forecast model]\n  C --> D[Forecast horizon]\n  D --> E[Rules / activation logic]\n  E --> F{Act?}\n  F -- yes --> G[Create task/order]\n  F -- no --> H[Log only]\n  G --> I[Outputs: forecast.csv + actions.csv]\n  H --> I\n",
  "p05_situation_detector": "flowchart LR\n  A[Inputs: signals + context] --> B[Pattern library]\n  B --> C[Situation rules/ML]\n  C --> D[Situation detected]\n  D --> E[Explain (top factors)]\n  E --> F[Outputs: situations.csv + explanations.json]\n",
  "p06_timeline_prediction_engine": "flowchart LR\n  A[Input: tasks/events.csv] --> B[Feature extraction]\n  B --> C[Duration model]\n  C --> D[ETA predictions]\n  D --> E[Risk of delay]\n  E --> F[Outputs: timeline.csv + risk_flags.csv]\n",
  "p07_trend_atlas": "flowchart LR\n  A[Input: multi-source trends] --> B[Normalize + align]\n  B --> C[Clustering/topics]\n  C --> D[Trend scoring]\n  D --> E[Atlas views]\n  E --> F[Outputs: trends.csv + atlas_report.md]\n",
  "p08_data_quality_sentinel": "flowchart LR\n  A[Input: dataset.csv] --> B[Schema + profiling]\n  B --> C[Rules: nulls/outliers/drift]\n  C --> D[Quality score]\n  D --> E{Fail?}\n  E -- yes --> F[Block + ticket]\n  E -- no --> G[Approve]\n  F --> H[Outputs: dq_report.md + dq_metrics.csv]\n  G --> H\n",
  "p09_model_drift_monitor": "flowchart LR\n  A[Input: baseline + new batch] --> B[Feature drift metrics]\n  B --> C[Prediction drift metrics]\n  C --> D[Drift score]\n  D --> E{Drift?}\n  E -- yes --> F[Retrain recommendation]\n  E -- no --> G[Continue]\n  F --> H[Outputs: drift_report.md + drift_metrics.csv]\n  G --> H\n",
  "p10_root_cause_suggester": "flowchart LR\n  A[Input: incidents + signals] --> B[Join context]\n  B --> C[Candidate causes]\n  C --> D[Ranking/attribution]\n  D --> E[Top root-cause suggestions]\n  E --> F[Outputs: root_causes.csv + notes.md]\n",
  "p11_ticket_triage_automl": "flowchart LR\n  A[Input: tickets.csv] --> B[Text preprocessing]\n  B --> C[AutoML / baseline models]\n  C --> D[Priority + routing]\n  D --> E[Human review loop]\n  E --> F[Outputs: triage.csv + model_card.md]\n",
  "p12_kpi_narrative_generator": "flowchart LR\n  A[Input: kpis.csv] --> B[Compute deltas]\n  B --> C[Detect anomalies]\n  C --> D[NLG templates]\n  D --> E[Generate narrative]\n  E --> F[Outputs: narrative.md + highlights.csv]\n",
  "p13_alert_to_action_orchestrator": "flowchart LR\n  A[Input: alerts.csv] --> B[Enrich context]\n  B --> C[Policy engine]\n  C --> D[Action selection]\n  D --> E[Execute: notify/task]\n  E --> F[Audit log]\n  F --> G[Outputs: actions.csv + audit_log.csv]\n",
  "p14_executive_demo_dashboard": "flowchart LR\n  A[Inputs: outputs from p01..p13] --> B[Aggregate KPIs]\n  B --> C[Build charts]\n  C --> D[Render HTML dashboard]\n  D --> E[Outputs: dist/dashboard.html]\n"
}

def detect_project_dirs(repo: Path):
    for p in sorted(repo.iterdir()):
        if p.is_dir() and re.match(r"^p\d\d_", p.name):
            yield p

def insert_or_replace_diagram(text: str, project_name: str) -> str:
    flow = MERMAID.get(project_name)
    if not flow:
        return text

    mermaid_block = "\n```mermaid\n" + flow.strip() + "\n```\n"

    # Replace first markdown image that points to *_plot.png (the wrong placeholder)
    plot_img_re = re.compile(r"^!\[[^\]]*\]\((?:[^)]+_plot\.png)\)\s*$", re.MULTILINE)
    if plot_img_re.search(text):
        return plot_img_re.sub(mermaid_block, text, count=1)

    # If there's a Diagram section, inject under it
    hdr_re = re.compile(r"^(##\s+(?:Diagrama|Diagram)\b.*)$", re.MULTILINE)
    m = hdr_re.search(text)
    if m:
        i = m.end()
        return text[:i] + "\n" + mermaid_block + text[i:]

    # Fallback: insert after H1
    h1_re = re.compile(r"^#\s+.+$", re.MULTILINE)
    m = h1_re.search(text)
    if m:
        i = m.end()
        return text[:i] + "\n\n" + mermaid_block + text[i:]

    return mermaid_block + "\n" + text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists():
        raise SystemExit(f"Repo no existe: {repo}")

    scanned = changed = 0
    for proj in detect_project_dirs(repo):
        readme = proj / "README.md"
        if not readme.exists():
            continue
        scanned += 1
        old = readme.read_text(encoding="utf-8")
        new = insert_or_replace_diagram(old, proj.name)
        if new != old:
            readme.write_text(new, encoding="utf-8")
            changed += 1

    print(f"OK — READMEs escaneados: {scanned}, actualizados: {changed}")

if __name__ == "__main__":
    main()
