#!/usr/bin/env bash
# benchmarks/idea-generation/env.sh
# Stages a tiny paper/ directory for the main agent's idea-generate skill.
# qa.jsonl is read by run_bench.py on the host — no need to stage it.
set -euo pipefail

: "${BENCH_CONTAINER:?must be exported by env_setup.sh}"
: "${BENCH_MOUNT:?must be exported by env_setup.sh}"
: "${BENCH_RUN_ID:=local}"

HERE="$(cd "$(dirname "$0")" && pwd)"
log() { printf '\n[idea-generation.env] %s\n' "$*"; }

# Bring up a fresh container.
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

# Stage tiny test papers into the ideate workspace so the agent can find them.
TARGET="${BENCH_MOUNT}/workspace/ideate/bench-fixtures/bench-${BENCH_RUN_ID}/paper"
log "staging paper fixture at ${TARGET}"
bench_container_cli exec "${BENCH_CONTAINER}" mkdir -p "${TARGET}"

PAPER_A='---
title: "TinyRec: A Toy Recommender Note"
authors: ["Bench Author"]
year: 2026
---
We propose a tiny two-tower recommender. We use L2 normalization on item
embeddings and a temperature of 0.07. On MovieLens-1M we get Recall@20 = 0.18
vs MF baseline 0.15.
'
PAPER_B='---
title: "SparseRec: Sparse Routing For Retrieval"
authors: ["Bench Author"]
year: 2026
---
We replace dense item tower with top-k sparse routing (k=8). On the same
MovieLens-1M split we get Recall@20 = 0.16, but inference FLOPs drop 40%.
'
printf '%s' "${PAPER_A}" | bench_container_cli exec -i "${BENCH_CONTAINER}" bash -lc "cat > ${TARGET}/tinyrec.md"
printf '%s' "${PAPER_B}" | bench_container_cli exec -i "${BENCH_CONTAINER}" bash -lc "cat > ${TARGET}/sparserec.md"

log "env ready"
