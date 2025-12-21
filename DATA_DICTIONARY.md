# DATA_DICTIONARY — Inputs (V1)

Este repositorio usa **datasets simulados** en V1 para demostrar flujos de ML operacional.
Cada proyecto puede agregar campos específicos en su propio diccionario, pero el patrón base es consistente.

## Formato base de series temporales (V1)
Archivo típico: `data/<project>_data.csv`

| Campo | Tipo | Ejemplo | Nulos | Descripción | Reglas |
|------|------|---------|------:|-------------|--------|
| t | int | 120 | 0% | índice temporal | creciente, >= 0 |
| value | float | 52.31 | 0% | valor de señal | rango esperado aprox. 30–80 |

## Notas
- Semilla fija para reproducibilidad.
- Los valores incluyen ruido y eventos anómalos inyectados.
