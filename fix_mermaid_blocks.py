#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re

def fix_readme(readme: Path) -> bool:
    txt = readme.read_text(encoding="utf-8")
    original = txt

    # Caso típico que te está pasando:
    # Bajo "Arquitectura / Flujo" quedó una línea tipo:
    # flowchart LR A[...] --> B[...] ...
    #
    # Lo convertimos en bloque Mermaid multilínea.
    def repl(match: re.Match) -> str:
        header = match.group(1)
        flow = match.group(2).strip()

        # Partir la cadena en "tokens" para meter saltos de línea razonables
        # Separar por " B --> " etc. sin romper demasiado
        flow = flow.replace(" --> ", " --> ")
        flow = flow.replace(" -- ", " -- ")

        # Intento simple: separar por patrones " X --> " / " X -- yes --> " etc.
        # Insertar newline antes de cada " <Letra> --" o " <Letra> -->"
        flow = re.sub(r"\s+([A-Z])\s+(--\s+yes\s+-->|--\s+no\s+-->|-->|--)\s+", r"\n  \1 \2 ", flow)

        # Asegurar que empieza con 'flowchart'
        if not flow.startswith("flowchart"):
            flow = "flowchart LR\n  " + flow
        else:
            # Si quedó en una sola línea, lo forzamos a dos líneas mínimo
            parts = flow.split(None, 2)
            if len(parts) >= 2:
                # flowchart LR ...
                rest = parts[2] if len(parts) == 3 else ""
                flow = f"{parts[0]} {parts[1]}\n  {rest}".rstrip()

        return f"{header}\n\n```mermaid\n{flow}\n```\n"

    # Busca el encabezado de sección y la línea flowchart que quedó como texto plano
    pattern = re.compile(
        r"(?:^##\s+.*Arquitectura\s*/\s*Flujo.*$)\s*\n+"
        r"(flowchart\s+LR.*)$",
        re.MULTILINE
    )

    txt, n = pattern.subn(repl, txt, count=1)

    # Si ya tiene bloque mermaid correcto, no tocamos nada.
    if txt != original:
        readme.write_text(txt, encoding="utf-8")
        return True
    return False

def main():
    repo = Path(".").resolve()
    changed = 0
    for p in sorted(repo.glob("p??_*/README.md")):
        if fix_readme(p):
            changed += 1
    print(f"OK: READMEs actualizados = {changed}")

if __name__ == "__main__":
    main()
