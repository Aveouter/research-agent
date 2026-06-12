#!/usr/bin/env bash
# benchmarks/idea-generate/_env_shared.sh
# Shared env logic for idea-generate shards.
# Called from each shard's env.sh.
#
# Responsibility: prepare container filesystem only.
# qa.jsonl is read by run_bench.py on the host — no need to stage it.
set -euo pipefail

log() { printf '\n[idea-generate.env] %s\n' "$*"; }

# Bring up a fresh container for this shard.
if [[ -n "${BENCH_ENV_FILE:-}" && -f "${BENCH_ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  . "${BENCH_ENV_FILE}"
  bench_force_recreate
fi

log "env ready (no container-side staging needed)"
