# OUTPUTS_DICTIONARY — Outputs (V1)

Los proyectos generan artefactos mínimos en V1 (demo runnable).

## Artefactos estándar
| Artefacto | Tipo | Ruta típica | Descripción |
|----------|------|------------|-------------|
| Figura principal | PNG | `img/<project>_plot.png` | señal / resultado visual del demo |
| Notebook runnable | ipynb | `notebooks/<project>.ipynb` | ejecución end-to-end |
| Dataset simulado | CSV | `data/<project>_data.csv` | input de demo |
| Script generador | py | `src/generate_data.py` | recrea dataset simulado |

## Outputs previstos (V2+)
- `outputs/predictions.csv` (scores / forecast)
- `outputs/report.md` (resumen ejecutivo)
- `outputs/metrics.json` (métricas del modelo)
