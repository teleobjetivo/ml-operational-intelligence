#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re

def already_in_mermaid_block(text: str, idx: int) -> bool:
    """
    Decide si el índice idx cae dentro de un bloque ```mermaid ... ```
    """
    before = text[:idx]
    # Cuenta fences abiertos
    opens = len(re.findall(r"^```mermaid\s*$", before, flags=re.MULTILINE))
    closes = len(re.findall(r"^```\s*$", before, flags=re.MULTILINE))
    return opens > closes

def wrap_flowchart_line(text: str) -> tuple[str, int]:
    """
    Envuelve líneas sueltas que empiezan con 'flowchart ' en ```mermaid ... ```
    Solo si NO están ya dentro de bloque mermaid.
    """
    lines = text.splitlines(True)  # keepends
    changed = 0
    out = []
    pos = 0

    for line in lines:
        m = re.match(r"^(flowchart\s+(LR|RL|TB|BT)\b.*)$", line.strip())
        if m and not already_in_mermaid_block(text, pos):
            flow = m.group(1)

            # Si viene todo en una sola línea con muchos "A --> B", lo partimos un poco
            # Insertamos saltos antes de patrones " X --> " o " X -- yes --> "
            flow2 = re.sub(r"\s+([A-Z])\s+(--\s+yes\s+-->|--\s+no\s+-->|-->)\s+",
                           r"\n  \1 \2 ", flow)

            # Si no quedó multilínea, igual lo dejamos dentro del bloque
            if "\n" not in flow2:
                flow2 = flow

            block = "```mermaid\n" + flow2 + "\n```\n"
            out.append(block)
            changed += 1
        else:
            out.append(line)

        pos += len(line)

    return "".join(out), changed

def main():
    repo = Path(".").resolve()
    total_changed = 0
    files_changed = 0

    for readme in sorted(repo.glob("p??_*/README.md")):
        txt = readme.read_text(encoding="utf-8")
        new_txt, n = wrap_flowchart_line(txt)
        if n > 0 and new_txt != txt:
            readme.write_text(new_txt, encoding="utf-8")
            total_changed += n
            files_changed += 1

    print(f"OK: archivos modificados = {files_changed} | diagramas envueltos = {total_changed}")

if __name__ == "__main__":
    main()
