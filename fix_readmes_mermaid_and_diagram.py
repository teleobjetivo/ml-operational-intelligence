#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re

def fix_one(readme: Path) -> bool:
    txt = readme.read_text(encoding="utf-8")
    original = txt

    # 1) Envolver mermaid si aparece "flowchart <DIR>" fuera de ```mermaid
    # Capturamos desde "flowchart LR|RL|TB|BT" hasta antes del siguiente heading "##" o "###" etc.
    # Si ya está envuelto en ```mermaid, no hacemos nada.
    if "```mermaid" not in txt:
        pattern = re.compile(
            r"(?m)^(flowchart\s+(LR|RL|TB|BT)\b[\s\S]*?)(?=^\#{1,6}\s|\Z)"
        )
        m = pattern.search(txt)
        if m:
            block = m.group(1).rstrip("\n")
            # Si el bloque ya tenía fences genéricos, lo limpiamos
            block = re.sub(r"(?m)^```.*$", "", block).strip("\n")
            wrapped = f"```mermaid\n{block}\n```\n\n"
            txt = txt[:m.start()] + wrapped + txt[m.end():]

    # 2) Quitar la “imagen-diagrama” que en realidad es un plot *_plot.png
    # Línea tipo: ![p02_xxx – diagram](img/p02_xxx_plot.png)
    txt = re.sub(
        r"(?m)^\!\[.*?– diagram\]\(img\/.*?_plot\.png\)\s*$\n?",
        "",
        txt
    )

    changed = (txt != original)
    if changed:
        readme.write_text(txt, encoding="utf-8")
    return changed

def main():
    repo = Path(".").resolve()
    readmes = sorted(repo.glob("p??_*/README.md"))
    changed_files = 0
    for r in readmes:
        if fix_one(r):
            changed_files += 1
    print(f"OK: READMEs modificados = {changed_files} / {len(readmes)}")

if __name__ == "__main__":
    main()
