from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DATA = PROJECT / "data"
OUT = PROJECT / "outputs"
IMG = PROJECT / "img"

def ensure_dirs():
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)

def simulate_history(n_entities: int = 120, n_days: int = 90, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2025-01-01", periods=n_days, freq="D")
    entities = [f"ENT-{i:03d}" for i in range(1, n_entities + 1)]

    rows = []
    base_risk = rng.uniform(0.05, 0.35, size=n_entities)  # riesgo base por entidad

    for i, ent in enumerate(entities):
        trend = rng.normal(0.0, 0.002)  # drift suave
        noise = rng.normal(0, 1, size=n_days)
        activity = np.clip(rng.normal(50, 15, size=n_days), 5, None)
        incidents = (rng.random(n_days) < (base_risk[i] + np.linspace(0, trend*n_days, n_days))).astype(int)

        # variable de comportamiento (ej: retraso / quejas / señales)
        behavior = np.clip(0.4*noise + 0.6*incidents + rng.normal(0, 0.3, size=n_days), -2, 3)

        for d, a, inc, beh in zip(dates, activity, incidents, behavior):
            rows.append({
                "date": d,
                "entity_id": ent,
                "activity": float(a),
                "incidents": int(inc),
                "behavior_index": float(beh),
            })

    df = pd.DataFrame(rows).sort_values(["entity_id", "date"])
    return df

def score_by_window(df: pd.DataFrame, window_days: int = 14) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # features rolling por entidad
    df["inc_rolling"] = (
        df.groupby("entity_id")["incidents"]
          .rolling(window_days, min_periods=max(3, window_days//3))
          .mean()
          .reset_index(level=0, drop=True)
    )
    df["beh_rolling"] = (
        df.groupby("entity_id")["behavior_index"]
          .rolling(window_days, min_periods=max(3, window_days//3))
          .mean()
          .reset_index(level=0, drop=True)
    )

    # score simple y explicable (logit-ish)
    x = 2.2*df["inc_rolling"].fillna(0) + 0.9*df["beh_rolling"].fillna(0)
    score = 1 / (1 + np.exp(-x))
    df["risk_score"] = np.clip(score, 0, 1)

    # segmentos
    df["segment"] = pd.cut(
        df["risk_score"],
        bins=[-0.001, 0.35, 0.65, 1.001],
        labels=["LOW", "MEDIUM", "HIGH"]
    )

    return df

def derive_actions(latest_scores: pd.DataFrame) -> pd.DataFrame:
    # reglas simples: suficiente para demo y entrevistas
    actions = []
    for _, r in latest_scores.iterrows():
        seg = str(r["segment"])
        if seg == "HIGH":
            action = "CALL + REVIEW"
            reason = "High risk_score"
        elif seg == "MEDIUM":
            action = "MONITOR + NUDGE"
            reason = "Medium risk_score"
        else:
            action = "NO ACTION"
            reason = "Low risk_score"
        actions.append({
            "date": r["date"],
            "entity_id": r["entity_id"],
            "risk_score": float(r["risk_score"]),
            "segment": seg,
            "action": action,
            "reason": reason
        })
    return pd.DataFrame(actions)

def save_outputs(df_scored: pd.DataFrame):
    # dataset scoreado completo (para que se vea evolución)
    df_scored.to_csv(OUT / "scores_timeseries.csv", index=False)

    # última fecha por entidad (lo que usarías operacionalmente)
    last_date = df_scored["date"].max()
    latest = df_scored[df_scored["date"] == last_date][["date","entity_id","risk_score","segment"]].copy()
    latest = latest.sort_values("risk_score", ascending=False)
    latest.to_csv(OUT / "scores.csv", index=False)

    actions = derive_actions(latest)
    actions.to_csv(OUT / "actions.csv", index=False)

    # plot ejemplo: top 1 entidad (serie temporal)
    top_ent = latest.iloc[0]["entity_id"] if len(latest) else None
    if top_ent:
        s = df_scored[df_scored["entity_id"] == top_ent].sort_values("date")
        plt.figure()
        plt.plot(pd.to_datetime(s["date"]), s["risk_score"])
        plt.title(f"P02 — Risk Scoring Evolutivo (top entity: {top_ent})")
        plt.xlabel("date")
        plt.ylabel("risk_score")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(IMG / "p02_risk_scoring_evolutivo_plot.png", dpi=160)
        plt.close()

    # report.md (sin depender de tabulate)
    report = []
    report.append("# P02 — Risk Scoring Evolutivo (V1 report)\n")
    report.append(f"- Entities: {df_scored['entity_id'].nunique()}\n")
    report.append(f"- Days: {df_scored['date'].nunique()}\n")
    report.append(f"- Latest date: {str(last_date.date())}\n")

    seg_counts = latest["segment"].value_counts(dropna=False).to_dict()
    report.append("\n## Segment distribution (latest)\n")
    for k, v in seg_counts.items():
        report.append(f"- {k}: {v}")
    report.append("\n")

    report.append("\n## Top 10 risky entities (latest)\n")
    report.append(latest.head(10).to_csv(index=False))
    report.append("\n")

    (OUT / "report.md").write_text("\n".join(report), encoding="utf-8")

def main():
    ensure_dirs()
    df = simulate_history()
    scored = score_by_window(df, window_days=14)
    save_outputs(scored)

    print("OK — Generated outputs:")
    print(f"- {OUT / 'scores_timeseries.csv'}")
    print(f"- {OUT / 'scores.csv'}")
    print(f"- {OUT / 'actions.csv'}")
    print(f"- {OUT / 'report.md'}")
    print(f"- {IMG / 'p02_risk_scoring_evolutivo_plot.png'}")

if __name__ == "__main__":
    main()
