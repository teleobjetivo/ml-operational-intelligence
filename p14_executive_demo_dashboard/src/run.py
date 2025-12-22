from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DATA = PROJECT / "data"
OUT = PROJECT / "outputs"
DIST = PROJECT / "dist"
IMG = PROJECT / "img"

def ensure_dirs():
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    DIST.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)

def simulate_kpis(seed: int = 21) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    today = pd.Timestamp("2025-12-01")

    areas = ["Operations", "Finance", "Customer", "Risk", "Data Platform"]
    kpis = [
        ("Incidents (7d)", "count"),
        ("SLA Compliance", "pct"),
        ("Cost per Ticket", "clp"),
        ("Risk Alerts (7d)", "count"),
        ("Pipeline Success Rate", "pct"),
        ("Forecast Error (MAPE)", "pct"),
        ("Data Quality Score", "pct"),
    ]

    rows = []
    for area in areas:
        for name, kind in kpis:
            if kind == "count":
                value = int(rng.integers(5, 140))
                target = int(max(1, value * rng.uniform(0.6, 1.1)))
                direction = "down" if "Incidents" in name or "Alerts" in name or "Error" in name else "up"
                unit = ""
            elif kind == "pct":
                value = float(np.clip(rng.normal(0.88, 0.08), 0.35, 0.99))
                target = float(np.clip(value + rng.normal(0.04, 0.03), 0.40, 0.995))
                direction = "up"
                unit = "%"
            else:  # clp
                value = float(np.clip(rng.normal(22000, 6000), 8000, 60000))
                target = float(np.clip(value * rng.uniform(0.75, 0.95), 7000, 60000))
                direction = "down"
                unit = "CLP"

            # tendencia vs semana anterior
            delta = float(np.clip(rng.normal(0.0, 0.12), -0.35, 0.35))

            rows.append({
                "date": today,
                "area": area,
                "kpi": name,
                "value": value,
                "target": target,
                "unit": unit,
                "direction": direction,   # "up" means higher is better, "down" means lower is better
                "wow_delta": delta,       # week-over-week change approx
            })

    df = pd.DataFrame(rows)
    return df

def format_value(v: float, unit: str) -> str:
    if unit == "%":
        return f"{v*100:,.1f}%"
    if unit == "CLP":
        return f"${v:,.0f}"
    # counts / raw
    if float(v).is_integer():
        return f"{int(v):,}"
    return f"{v:,.2f}"

def status(row) -> str:
    # compare value vs target using direction
    v = float(row["value"])
    t = float(row["target"])
    dir_ = row["direction"]
    if dir_ == "up":
        return "OK" if v >= t else "WATCH"
    else:
        return "OK" if v <= t else "WATCH"

def build_html(df: pd.DataFrame) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Precompute fields
    dfx = df.copy()
    dfx["status"] = dfx.apply(status, axis=1)
    dfx["value_fmt"] = [format_value(v, u) for v, u in zip(dfx["value"], dfx["unit"])]
    dfx["target_fmt"] = [format_value(v, u) for v, u in zip(dfx["target"], dfx["unit"])]
    dfx["wow_fmt"] = [f"{x*100:+.1f}%" for x in dfx["wow_delta"]]

    # Simple KPI cards grouped by area
    sections = []
    for area, sub in dfx.groupby("area"):
        cards = []
        for _, r in sub.iterrows():
            badge = "ok" if r["status"] == "OK" else "watch"
            cards.append(f"""
            <div class="card">
              <div class="kpi-title">{r["kpi"]}</div>
              <div class="kpi-value">{r["value_fmt"]}</div>
              <div class="kpi-meta">
                <span class="badge {badge}">{r["status"]}</span>
                <span class="muted">Target: {r["target_fmt"]}</span>
                <span class="muted">WoW: {r["wow_fmt"]}</span>
              </div>
            </div>
            """)
        sections.append(f"""
        <section class="section">
          <h2>{area}</h2>
          <div class="grid">
            {''.join(cards)}
          </div>
        </section>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>P14 — Executive Demo Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial; margin: 0; background: #0b1220; color: #e8eefc; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 22px; }}
    .top {{ display:flex; justify-content:space-between; align-items:flex-end; gap: 16px; }}
    .title {{ font-size: 22px; font-weight: 700; }}
    .subtitle {{ font-size: 13px; color: #a9b7d4; margin-top: 6px; }}
    .chip {{ font-size: 12px; color: #a9b7d4; border: 1px solid rgba(169,183,212,0.25); padding: 6px 10px; border-radius: 999px; }}
    .section {{ margin-top: 18px; }}
    h2 {{ font-size: 16px; margin: 18px 0 10px; color: #d9e5ff; }}
    .grid {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
    .card {{ background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 14px; }}
    .kpi-title {{ font-size: 12px; color: #a9b7d4; }}
    .kpi-value {{ font-size: 24px; font-weight: 800; margin-top: 6px; }}
    .kpi-meta {{ display:flex; gap: 10px; align-items:center; margin-top: 10px; flex-wrap: wrap; }}
    .badge {{ font-size: 11px; padding: 4px 8px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.14); }}
    .badge.ok {{ background: rgba(39, 174, 96, 0.18); }}
    .badge.watch {{ background: rgba(241, 196, 15, 0.18); }}
    .muted {{ font-size: 12px; color: #a9b7d4; }}
    .footer {{ margin-top: 18px; font-size: 12px; color: #8fa2c7; }}
    @media (max-width: 980px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (max-width: 640px) {{ .grid {{ grid-template-columns: 1fr; }} .top {{ flex-direction: column; align-items:flex-start; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <div class="title">P14 — Executive Demo Dashboard</div>
        <div class="subtitle">Portable V1 dashboard (simulated KPIs) · TeleObjetivo / Orion Lab</div>
      </div>
      <div class="chip">Generated: {generated}</div>
    </div>

    {''.join(sections)}

    <div class="footer">
      Tip: open this file locally in your browser. Next V2: wire real outputs from P01–P13.
    </div>
  </div>
</body>
</html>
"""
    return html

def save_outputs(df: pd.DataFrame, html: str):
    df.to_csv(OUT / "kpis.csv", index=False)
    (OUT / "report.md").write_text(
        "\n".join([
            "# P14 — Executive Demo Dashboard (V1 report)\n",
            f"- Rows: {len(df)}",
            f"- Areas: {df['area'].nunique()}",
            f"- KPIs per area: ~{len(df) // max(1, df['area'].nunique())}\n",
            "## Notes\n",
            "- This is a simulated KPI set for demo purposes.\n",
            "- V2 can ingest outputs from other projects and render a consolidated executive view.\n",
        ]),
        encoding="utf-8"
    )
    (DIST / "dashboard.html").write_text(html, encoding="utf-8")

def main():
    ensure_dirs()
    df = simulate_kpis()
    html = build_html(df)
    save_outputs(df, html)

    print("OK — Generated outputs:")
    print(f"- {OUT / 'kpis.csv'}")
    print(f"- {OUT / 'report.md'}")
    print(f"- {DIST / 'dashboard.html'}")

if __name__ == "__main__":
    main()
