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

def simulate_pipeline(seed: int = 6, n_jobs: int = 220) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Jobs with planned ETA and signals observed during execution
    start_dates = pd.to_datetime("2025-10-01") + pd.to_timedelta(rng.integers(0, 60, size=n_jobs), unit="D")
    planned_duration_h = np.clip(rng.normal(6.0, 2.2, size=n_jobs), 1.0, 18.0)

    # signals: queue wait, retries, cpu pressure, data size
    queue_wait_h = np.clip(rng.gamma(2.0, 0.6, size=n_jobs), 0.0, 6.0)
    retries = rng.poisson(0.4, size=n_jobs)
    cpu_pressure = np.clip(rng.normal(0.55, 0.18, size=n_jobs), 0.05, 0.98)
    data_gb = np.clip(rng.lognormal(mean=2.0, sigma=0.55, size=n_jobs), 1.0, 400.0)

    # ground truth: actual duration depends on signals (simple and explainable)
    actual_duration_h = (
        planned_duration_h
        + 0.7 * queue_wait_h
        + 0.9 * retries
        + 3.2 * np.maximum(cpu_pressure - 0.65, 0)
        + 0.006 * np.maximum(data_gb - 60, 0)
        + rng.normal(0, 0.8, size=n_jobs)
    )
    actual_duration_h = np.clip(actual_duration_h, 0.7, 40.0)

    df = pd.DataFrame({
        "job_id": [f"JOB-{i:04d}" for i in range(1, n_jobs + 1)],
        "start_time": start_dates,
        "planned_duration_h": planned_duration_h.round(2),
        "queue_wait_h": queue_wait_h.round(2),
        "retries": retries.astype(int),
        "cpu_pressure": cpu_pressure.round(3),
        "data_gb": data_gb.round(1),
        "actual_duration_h": actual_duration_h.round(2),
    })

    df["planned_end"] = df["start_time"] + pd.to_timedelta(df["planned_duration_h"], unit="h")
    df["actual_end"] = df["start_time"] + pd.to_timedelta(df["actual_duration_h"], unit="h")
    df["delay_h"] = (df["actual_duration_h"] - df["planned_duration_h"]).round(2)
    return df.sort_values("start_time")

def predict_eta(df: pd.DataFrame) -> pd.DataFrame:
    # lightweight "model": linear-ish scoring -> predicted additional hours
    dfx = df.copy()

    # normalize data size a bit (log)
    size_term = np.log1p(dfx["data_gb"])  # smooth
    # risk of delay proxy
    delay_risk = (
        0.55 * dfx["queue_wait_h"]
        + 0.75 * dfx["retries"]
        + 5.0 * np.maximum(dfx["cpu_pressure"] - 0.65, 0)
        + 0.9 * np.maximum(size_term - np.log1p(60), 0)
    )

    # map to predicted delay in hours (bounded)
    pred_delay = np.clip(0.35 * delay_risk, 0, 18.0)
    dfx["pred_delay_h"] = pred_delay.round(2)
    dfx["pred_duration_h"] = (dfx["planned_duration_h"] + dfx["pred_delay_h"]).round(2)
    dfx["pred_end"] = dfx["start_time"] + pd.to_timedelta(dfx["pred_duration_h"], unit="h")

    # confidence heuristic (for demo): lower variance signals => higher confidence
    conf = 1.0 - np.clip(
        0.12 * dfx["retries"] + 0.10 * (dfx["queue_wait_h"] / 6.0) + 0.22 * np.maximum(dfx["cpu_pressure"] - 0.7, 0),
        0, 0.7
    )
    dfx["confidence"] = conf.round(2)

    # buckets
    dfx["risk_band"] = pd.cut(
        dfx["pred_delay_h"],
        bins=[-0.01, 1.0, 3.0, 6.0, 99],
        labels=["ON_TIME", "MINOR", "MODERATE", "SEVERE"]
    )
    return dfx

def actions(df_pred: pd.DataFrame) -> pd.DataFrame:
    actions = []
    for _, r in df_pred.iterrows():
        band = str(r["risk_band"])
        if band == "SEVERE":
            action = "ESCALATE + REPLAN"
            reason = "High predicted delay"
        elif band == "MODERATE":
            action = "ALLOCATE RESOURCES"
            reason = "Moderate predicted delay"
        elif band == "MINOR":
            action = "MONITOR"
            reason = "Minor predicted delay"
        else:
            action = "NO ACTION"
            reason = "On time"
        actions.append({
            "job_id": r["job_id"],
            "start_time": r["start_time"],
            "planned_end": r["planned_end"],
            "pred_end": r["pred_end"],
            "pred_delay_h": float(r["pred_delay_h"]),
            "risk_band": band,
            "confidence": float(r["confidence"]),
            "action": action,
            "reason": reason,
        })
    return pd.DataFrame(actions)

def plot(df_pred: pd.DataFrame):
    # show planned vs predicted end spread (sample 60 jobs)
    s = df_pred.sort_values("start_time").tail(60).copy()
    x = np.arange(len(s))
    planned = (pd.to_datetime(s["planned_end"]) - pd.to_datetime(s["start_time"])).dt.total_seconds() / 3600.0
    pred = (pd.to_datetime(s["pred_end"]) - pd.to_datetime(s["start_time"])).dt.total_seconds() / 3600.0

    plt.figure()
    plt.plot(x, planned, label="planned duration (h)")
    plt.plot(x, pred, label="predicted duration (h)")
    plt.title("P06 — Timeline Prediction Engine (sample jobs)")
    plt.xlabel("job index (ordered by start_time)")
    plt.ylabel("duration (hours)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(IMG / "p06_timeline_prediction_engine_plot.png", dpi=160)
    plt.close()

def save(df_pred: pd.DataFrame):
    df_pred.to_csv(OUT / "timeline_predictions.csv", index=False)

    act = actions(df_pred)
    act.sort_values(["pred_delay_h"], ascending=False).to_csv(OUT / "actions.csv", index=False)

    # mini metrics for report
    mae = float(np.mean(np.abs(df_pred["pred_duration_h"] - df_pred["actual_duration_h"])))
    severe = int((df_pred["risk_band"] == "SEVERE").sum())
    moderate = int((df_pred["risk_band"] == "MODERATE").sum())

    report = []
    report.append("# P06 — Timeline Prediction Engine (V1 report)\n")
    report.append(f"- Jobs simulated: {len(df_pred)}")
    report.append(f"- MAE (duration hours): {mae:.2f}")
    report.append(f"- Risk bands: SEVERE={severe}, MODERATE={moderate}\n")
    report.append("## Top 10 predicted delays\n")
    top = df_pred.sort_values("pred_delay_h", ascending=False)[["job_id","pred_delay_h","risk_band","confidence","retries","queue_wait_h","cpu_pressure","data_gb"]].head(10)
    report.append(top.to_csv(index=False))
    (OUT / "report.md").write_text("\n".join(report), encoding="utf-8")

def main():
    ensure_dirs()
    df = simulate_pipeline()
    dfp = predict_eta(df)
    plot(dfp)
    save(dfp)

    print("OK — Generated outputs:")
    print(f"- {OUT / 'timeline_predictions.csv'}")
    print(f"- {OUT / 'actions.csv'}")
    print(f"- {OUT / 'report.md'}")
    print(f"- {IMG / 'p06_timeline_prediction_engine_plot.png'}")

if __name__ == "__main__":
    main()
