#!/usr/bin/env bash
# benchmarks/paper-review/_env_shared.sh
# Shared env logic for paper-review shards.
# Called from each shard's env.sh.
#
# Responsibility: prepare container filesystem only.
# - Stage wiki fixtures into the wiki vault (~/.openclaw/wiki/main/)
# - Stage full-text papers into the vault
# - Link benchmarks/ into workspace for path resolution
# qa.jsonl is read by run_bench.py on the host — no need to stage it.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
log() { printf '\n[paper-review.env] %s\n' "$*"; }

# Bring up a fresh container for this shard.
if [[ -n "${BENCH_ENV_FILE:-}" && -f "${BENCH_ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  . "${BENCH_ENV_FILE}"
  bench_force_recreate
fi
if ! declare -F bench_container_cli >/dev/null; then
  bench_container_cli() {
    local cli="${BENCH_CONTAINER_CLI:-${BENCH_CONTAINER_RUNTIME:-docker}}"
    [[ "${cli}" == "auto" ]] && cli=docker
    "${cli}" "$@"
  }
fi

# ── 1. Stage wiki fixtures into the wiki vault ─────────────────────
# openclaw.json configures memory-wiki vault at ~/.openclaw/wiki/main.
# QA prompts reference wiki files via this vault path.
WIKI_VAULT="${BENCH_MOUNT}/wiki/main"
MATERIALS_SRC="${HERE}/materials"

if [[ -d "${MATERIALS_SRC}" ]]; then
  log "staging wiki materials -> ${WIKI_VAULT}"
  bench_container_cli exec "${BENCH_CONTAINER}" mkdir -p "${WIKI_VAULT}"

  # Wiki entries
  if [[ -d "${MATERIALS_SRC}/wiki" ]]; then
    for f in "${MATERIALS_SRC}/wiki"/*; do
      [[ -f "$f" ]] || continue
      bench_container_cli cp "$f" "${BENCH_CONTAINER}:${WIKI_VAULT}/$(basename "$f")"
    done
  fi

  # Full-text papers
  for f in "${MATERIALS_SRC}"/*; do
    [[ -f "$f" ]] || continue
    bench_container_cli cp "$f" "${BENCH_CONTAINER}:${WIKI_VAULT}/$(basename "$f")"
  done
  log "staged materials into wiki vault"
fi

# ── 2. Link benchmarks/ into workspace for agent path resolution ───
# QA prompts reference benchmarks/paper-review/materials/* paths.
# OpenClaw tools resolve relative paths from the workspace root.
log "linking repo benchmarks into workspace"
bench_container_cli exec "${BENCH_CONTAINER}" bash -lc \
  "for ws in workspace workspace/extract workspace/critic workspace/design workspace/spec workspace/audit; do
     mkdir -p '${BENCH_MOUNT}/\${ws}'
     rm -f '${BENCH_MOUNT}/\${ws}/benchmarks'
     ln -s '${BENCH_MOUNT}/benchmarks' '${BENCH_MOUNT}/\${ws}/benchmarks'
   done"

# ── 3. Output directories ──────────────────────────────────────────
log "ensuring output dirs"
bench_container_cli exec "${BENCH_CONTAINER}" mkdir -p \
  "${BENCH_MOUNT}/workspace/extract/outputs/bench-${BENCH_RUN_ID}"

log "env ready"
