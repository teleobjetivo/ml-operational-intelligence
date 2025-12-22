#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
COMMIT_MSG="chore(repo): deps+cleanup+sync (tabulate + duplicate folders)"

# --- Helpers ---
log() { printf "\n\033[1m%s\033[0m\n" "$*"; }
warn() { printf "\n\033[33mWARN:\033[0m %s\n" "$*"; }
die() { printf "\n\033[31mERROR:\033[0m %s\n" "$*"; exit 1; }

# --- Preconditions ---
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "No estás dentro de un repo git. Entra a ml-operational-intelligence."
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

log "Repo root: $ROOT"
log "Branch actual: $(git branch --show-current 2>/dev/null || echo 'unknown')"

# --- 1) Fix requirements: add tabulate if missing ---
REQ="$ROOT/requirements.txt"
if [[ ! -f "$REQ" ]]; then
  warn "No existe requirements.txt en raíz. Lo creo."
  touch "$REQ"
fi

if ! grep -qiE '^\s*tabulate\s*([=<>!~].*)?$' "$REQ"; then
  log "Agregando 'tabulate' a requirements.txt (faltaba)..."
  printf "\n# Optional dependency used by pandas.to_markdown\nTABULATE_FIX=tabulate\n" >> "$REQ"
  # Replace line to keep it clean
  # shellcheck disable=SC2016
  python3 - <<'PY'
from pathlib import Path
p = Path("requirements.txt")
lines = p.read_text(encoding="utf-8").splitlines()
out = []
for ln in lines:
    if ln.strip() == "TABULATE_FIX=tabulate":
        out.append("tabulate")
    else:
        out.append(ln)
p.write_text("\n".join(out).strip() + "\n", encoding="utf-8")
PY
else
  log "requirements.txt ya incluye tabulate ✅"
fi

# --- 2) Cleanup duplicate folders like "data 2", "img 2", etc. (SAFE: no deletions if has content) ---
log "Buscando carpetas duplicadas tipo '* 2' dentro de p??_* ..."

DUP_ROOT="$ROOT/_private_docs/duplicates_backup"
mkdir -p "$DUP_ROOT"

shopt -s nullglob
dup_dirs=()
for d in p??_*/; do
  # Only within each project top-level
  for x in "$d"*" 2"/; do
    [[ -d "$x" ]] && dup_dirs+=("$x")
  done
done

if [[ ${#dup_dirs[@]} -eq 0 ]]; then
  log "No encontré carpetas '* 2' ✅"
else
  log "Encontré ${#dup_dirs[@]} carpeta(s) duplicada(s). Haré limpieza segura:"
  for x in "${dup_dirs[@]}"; do
    # Trim trailing slash
    x="${x%/}"
    base="${x% 2}"            # remove " 2"
    proj="$(echo "$x" | cut -d/ -f1)"
    name="$(basename "$x")"
    base_name="$(basename "$base")"

    if [[ -d "$base" ]]; then
      # If duplicate folder is empty -> delete
      if [[ -z "$(ls -A "$x" 2>/dev/null || true)" ]]; then
        log "Borrando carpeta vacía: $x"
        rmdir "$x" || rm -rf "$x"
      else
        # Has content: MOVE to private backup (no data loss)
        ts="$(date +%Y%m%d_%H%M%S)"
        dest="$DUP_ROOT/$proj/$base_name/$ts"
        log "Moviendo contenido privado (NO se pierde): $x -> $dest"
        mkdir -p "$dest"
        mv "$x"/* "$dest"/
        # Remove now-empty dir
        rmdir "$x" || rm -rf "$x"
        warn "Contenido de '$name' se movió a _private_docs/duplicates_backup (no se sube a GitHub)."
      fi
    else
      # Base folder doesn't exist -> rename (safe)
      log "Renombrando: $x -> $base"
      mv "$x" "$base"
    fi
  done
fi

# --- 3) Ensure _private_docs is ignored (in case it isn't) ---
GI="$ROOT/.gitignore"
if [[ -f "$GI" ]]; then
  if ! grep -qE '^\s*_private_docs/\s*$' "$GI"; then
    log "Agregando _private_docs/ a .gitignore (para evitar subir backups privados)..."
    printf "\n# Private / local workspace\n_private_docs/\n" >> "$GI"
  else
    log ".gitignore ya ignora _private_docs/ ✅"
  fi
else
  warn "No existe .gitignore en raíz. Lo creo e ignoro _private_docs/."
  printf "_private_docs/\n" > "$GI"
fi

# --- 4) Commit + sync + push (handles your previous 'fetch first') ---
log "Estado git antes:"
git status -sb

log "Agregando cambios..."
git add -A

if git diff --cached --quiet; then
  log "No hay cambios para commitear ✅ (igual sincronizo con remote)"
else
  log "Commit: $COMMIT_MSG"
  git commit -m "$COMMIT_MSG"
fi

log "Sincronizando con origin (pull --rebase) ..."
git pull --rebase

log "Push a origin ..."
git push

log "LISTO ✅ Repo actualizado en GitHub."
log "Tip: si moví algo a _private_docs/duplicates_backup, quedó local y privado."
