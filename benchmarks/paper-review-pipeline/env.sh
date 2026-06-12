#!/usr/bin/env bash
# benchmarks/paper-review-pipeline/env.sh
# Full 5-stage pipeline benchmark. Reuses paper-review fixtures.
# qa.jsonl is read by run_bench.py on the host — no need to stage it.
set -euo pipefail

: "${BENCH_CONTAINER:?must be exported by env_setup.sh}"
: "${BENCH_MOUNT:?must be exported by env_setup.sh}"
: "${BENCH_RUN_ID:=local}"

HERE="$(cd "$(dirname "$0")" && pwd)"
log() { printf '\n[paper-review-pipeline.env] %s\n' "$*"; }

# Bring up a fresh container.
if [[ -n "${BENCH_ENV_FILE:-}" && -f "${BENCH_ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  . "${BENCH_ENV_FILE}"
  bench_force_recreate
fi

# Delegate to paper-review's shared env (stages wiki vault + links).
PARENT="$(cd "${HERE}/../paper-review" && pwd)"
# shellcheck disable=SC1090
. "${PARENT}/_env_shared.sh"
