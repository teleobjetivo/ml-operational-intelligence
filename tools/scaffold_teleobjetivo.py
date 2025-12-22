#!/usr/bin/env python3
"""TeleObjetivo / OrionLab — Repo & Project Scaffolder

Creates a new repository skeleton and/or adds new pXX projects with the same
structure you already use: data/, notebooks/, img/, README.md, plus root README,
.gitignore, requirements.txt, and VSCode settings.

Usage examples:

  # Create a new repo (kebab-case) with base files and first project
  python scaffold_teleobjetivo.py repo --root "/Users/hugobaghetti/Desktop/PROYECTOS/teleobjetivo-workspace/03_labs_ml_ai" \
      --name "ml-operational-intelligence" --lang "es+en"

  # Add a project to an existing repo
  python scaffold_teleobjetivo.py project --repo "/path/to/ml-operational-intelligence" \
      --code "p02" --slug "risk_scoring_dinamico" --title "Risk Scoring Evolutivo" --lang "es+en"

Notes:
- This script does NOT create GitHub repos; it scaffolds locally.
- It will not overwrite existing files unless you pass --force.
"""

from __future__ import annotations
import argparse
import os
from pathlib import Path
import textwrap
import json

GITIGNORE = textwrap.dedent(""".venv/
__pycache__/
.ipynb_checkpoints/
.DS_Store

# Local/private files
*.pdf
""")

REQUIREMENTS_BASE = textwrap.dedent("""pandas
numpy
matplotlib
jupyter
""")

VSCODE_SETTINGS = {
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": True
}

README_ROOT_ESEN = textwrap.dedent("""# {repo_title} — OrionLab / TeleObjetivo

Este repositorio agrupa proyectos ejecutables, reproducibles y explicables.
Cada proyecto sigue el patrón: `data/`, `notebooks/`, `img/` y su `README.md`.

---

## 📌 Proyectos
{projects_list}

---

## 🚀 Cómo ejecutar

```bash
cd "{repo_path}"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

---

# EN — {repo_title} — OrionLab / TeleObjetivo

This repository groups executable, reproducible, explainable projects.
Each project follows the same pattern: `data/`, `notebooks/`, `img/` plus its `README.md`.

---

## 📌 Projects
{projects_list_en}

---

## 🚀 How to run

```bash
cd "{repo_path}"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```
""")

README_PROJECT_ESEN = textwrap.dedent("""# {code} — {title} ({subtitle_es})

## 📌 Objetivo
{objective_es}

## 🗂 Estructura del proyecto
- `data/` → dataset (simulado o real)
- `notebooks/` → notebook principal
- `img/` → figuras exportadas
- `README.md` → este documento

## 🚀 Cómo ejecutar (desde la raíz del repo)

```bash
cd "{repo_path}"
source .venv/bin/activate
jupyter notebook
```

Abrir:
- `{code}_{slug}/notebooks/{code}_{slug}.ipynb`

---

# EN — {code} — {title} ({subtitle_en})

## 📌 Goal
{objective_en}

## 🗂 Project structure
- `data/` → dataset (simulated or real)
- `notebooks/` → main notebook
- `img/` → exported figures
- `README.md` → this file

## 🚀 How to run (from repo root)

```bash
cd "{repo_path}"
source .venv/bin/activate
jupyter notebook
```

Open:
- `{code}_{slug}/notebooks/{code}_{slug}.ipynb`
""")

def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_json(path: Path, obj: dict, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def ensure_repo(repo_path: Path, lang: str, force: bool) -> None:
    write_file(repo_path / ".gitignore", GITIGNORE, force=force)
    if not (repo_path / "requirements.txt").exists() or force:
        write_file(repo_path / "requirements.txt", REQUIREMENTS_BASE, force=True)
    write_json(repo_path / ".vscode" / "settings.json", VSCODE_SETTINGS, force=force)

def update_root_readme(repo_path: Path, repo_title: str, lang: str, force: bool) -> None:
    # Build project list from p??_* folders
    projects = sorted([p.name for p in repo_path.iterdir() if p.is_dir() and p.name.startswith("p")])
    if projects:
        es_list = "\n".join([f"- `{p}`" for p in projects])
        en_list = es_list
    else:
        es_list = "- (sin proyectos aún)"
        en_list = "- (no projects yet)"
    content = README_ROOT_ESEN.format(
        repo_title=repo_title,
        projects_list=es_list,
        projects_list_en=en_list,
        repo_path=str(repo_path)
    )
    write_file(repo_path / "README.md", content, force=force)

def add_project(repo_path: Path, code: str, slug: str, title: str, lang: str, force: bool) -> Path:
    folder = repo_path / f"{code}_{slug}"
    (folder / "data").mkdir(parents=True, exist_ok=True)
    (folder / "notebooks").mkdir(parents=True, exist_ok=True)
    (folder / "img").mkdir(parents=True, exist_ok=True)

    readme = README_PROJECT_ESEN.format(
        code=code,
        slug=slug,
        title=title,
        subtitle_es="Proyecto",
        subtitle_en="Project",
        objective_es="(Describe el objetivo en 2-3 líneas, directo y vendible.)",
        objective_en="(Describe the goal in 2-3 lines, concise and portfolio-ready.)",
        repo_path=str(repo_path)
    )
    write_file(folder / "README.md", readme, force=force)

    # create a blank notebook placeholder
    nb_path = folder / "notebooks" / f"{code}_{slug}.ipynb"
    if not nb_path.exists() or force:
        nb_min = {
          "cells": [
            {"cell_type":"markdown","metadata":{},"source":[f"# {code} — {title}\n\nNotebook scaffold.\n"]},
            {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":["import pandas as pd\nimport numpy as np\n"]}
          ],
          "metadata": {"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}},
          "nbformat": 4,
          "nbformat_minor": 5
        }
        nb_path.write_text(json.dumps(nb_min, indent=2), encoding="utf-8")
    return folder

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_repo = sub.add_parser("repo", help="Create a new repo skeleton")
    p_repo.add_argument("--root", required=True, help="Parent folder where repo will be created")
    p_repo.add_argument("--name", required=True, help="Repo folder name (kebab-case recommended)")
    p_repo.add_argument("--title", default=None, help="Human title for README")
    p_repo.add_argument("--lang", default="es+en", choices=["es", "en", "es+en"])
    p_repo.add_argument("--force", action="store_true")

    p_proj = sub.add_parser("project", help="Add a new project to an existing repo")
    p_proj.add_argument("--repo", required=True, help="Repo path")
    p_proj.add_argument("--code", required=True, help="Project code like p02")
    p_proj.add_argument("--slug", required=True, help="Project slug like event_early_warning")
    p_proj.add_argument("--title", required=True, help="Project title")
    p_proj.add_argument("--lang", default="es+en", choices=["es", "en", "es+en"])
    p_proj.add_argument("--force", action="store_true")

    args = parser.parse_args()

    if args.cmd == "repo":
        repo_path = Path(args.root).expanduser().resolve() / args.name
        repo_path.mkdir(parents=True, exist_ok=True)
        ensure_repo(repo_path, lang=args.lang, force=args.force)
        update_root_readme(repo_path, repo_title=(args.title or args.name), lang=args.lang, force=args.force)
        print(f"OK repo -> {repo_path}")
    elif args.cmd == "project":
        repo_path = Path(args.repo).expanduser().resolve()
        ensure_repo(repo_path, lang=args.lang, force=args.force)
        folder = add_project(repo_path, code=args.code, slug=args.slug, title=args.title, lang=args.lang, force=args.force)
        update_root_readme(repo_path, repo_title=repo_path.name, lang=args.lang, force=False)
        print(f"OK project -> {folder}")

if __name__ == "__main__":
    main()
