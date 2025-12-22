from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
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

def generate_synthetic_events(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ts = pd.date_range("2025-01-01", periods=n, freq="h")
    # señal base + ruido
    signal = rng.normal(0, 1, size=n).cumsum() * 0.02 + 10
    noise = rng.normal(0, 0.5, size=n)
    value = signal + noise

    # inyectar eventos anómalos (picos)
    event_idx = rng.choice(np.arange(200, n-200), size=12, replace=False)
    value[event_idx] += rng.normal(6, 2, size=len(event_idx))

    df = pd.DataFrame({
        "timestamp": ts,
        "value": value,
        "asset_id": rng.choice(["TRUCK-01","TRUCK-02","TRUCK-03"], size=n, replace=True),
    }).sort_values("timestamp")
    return df

def detect_anomalies(df: pd.DataFrame, z: float = 3.0) -> pd.DataFrame:
    # método simple y explicable: z-score por ventana rolling
    s = df["value"].astype(float)
    roll_mean = s.rolling(48, min_periods=24).mean()
    roll_std = s.rolling(48, min_periods=24).std().replace(0, np.nan)
    zscore = (s - roll_mean) / roll_std
    df = df.copy()
    df["zscore"] = zscore.fillna(0.0)
    df["is_anomaly"] = (df["zscore"].abs() >= z).astype(int)
    return df

def save_outputs(df: pd.DataFrame):
    alerts = df.loc[df["is_anomaly"] == 1, ["timestamp", "asset_id", "value", "zscore"]].copy()
    alerts = alerts.sort_values("timestamp")
    df.to_csv(OUT / "events_scored.csv", index=False)
    alerts.to_csv(OUT / "alerts.csv", index=False)

    # plot ejemplo
    plt.figure()
    plt.plot(pd.to_datetime(df["timestamp"]), df["value"])
    a = df[df["is_anomaly"] == 1]
    if len(a) > 0:
        plt.scatter(pd.to_datetime(a["timestamp"]), a["value"])
    plt.title("P01 — Event Early Warning (example plot)")
    plt.xlabel("timestamp")
    plt.ylabel("value")
    plt.tight_layout()
    plt.savefig(IMG / "p01_event_early_warning_plot.png", dpi=160)
    plt.close()

    # reporte ejecutivo simple
    report = []
    report.append("# P01 — Event Early Warning (V1 report)\n")
    report.append(f"- Rows: {len(df)}\n")
    report.append(f"- Alerts: {int(df['is_anomaly'].sum())}\n")
    if len(alerts) > 0:
        report.append("\n## Last 5 alerts\n")
        report.append(alerts.tail(5).to_markdown(index=False))
        report.append("\n")
    (OUT / "report.md").write_text("\n".join(report), encoding="utf-8")

def main():
    ensure_dirs()
    # siempre regeneramos por ser demo V1; si quieres lo hacemos incremental después.
    df = generate_synthetic_events()
    scored = detect_anomalies(df)
    save_outputs(scored)
    print("OK — Generated outputs:")
    print(f"- {OUT / 'events_scored.csv'}")
    print(f"- {OUT / 'alerts.csv'}")
    print(f"- {OUT / 'report.md'}")
    print(f"- {IMG / 'p01_event_early_warning_plot.png'}")

if __name__ == "__main__":
    main()
