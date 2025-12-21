# Data Dictionary — p06_timeline_prediction_engine (V1)

## Input
Archivo: `data/p06_timeline_prediction_engine_data.csv`

| Campo | Tipo | Ejemplo | Nulos | Descripción | Reglas |
|------|------|---------|------:|-------------|--------|
| t | int | 120 | 0% | índice temporal | creciente, >= 0 |
| value | float | 52.31 | 0% | señal simulada | ruido + eventos anómalos |

## Notas
- Dataset simulado para demo V1.
- En V2 se reemplaza por datos reales/abiertos del dominio del proyecto.
