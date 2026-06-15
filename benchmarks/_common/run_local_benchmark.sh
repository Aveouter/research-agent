#!/usr/bin/env bash
# Run one benchmark end-to-end in the local benchmark container environment.
#
# Examples:
#   benchmarks/_common/run_local_benchmark.sh idea-generate-1
#   benchmarks/_common/run_local_benchmark.sh --runtime container idea-generate-1
#   BENCH_DEBUG=1 benchmarks/_common/run_local_benchmark.sh --keep-container paper-ingest
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUNTIME="${BENCH_CONTAINER_RUNTIME:-auto}"
KEEP_CONTAINER="${BENCH_KEEP_CONTAINER:-}"
DEBUG="${BENCH_DEBUG:-}"
CLI_MODEL=""
CLI_BASE_URL=""
CLI_API_KEY=""
BENCH=""

usage() {
  cat <<'USAGE'
usage: benchmarks/_common/run_local_benchmark.sh [options] <benchmark>

Run exactly one benchmark in the same local containerized OpenClaw environment
used by CI. The runner supports Docker and Apple's `container` CLI.

Options:
  --runtime docker|container|auto  Container runtime to use (default: auto).
                                   auto prefers a running Docker daemon, then
                                   falls back to Apple's `container` CLI.
  --model MODEL                    Override the LLM model (e.g. minimax/MiniMax-M2.7).
                                   Default: read from docker/.env.bench or CI default.
  --base-url URL                   Override the LLM provider base URL.
                                   Default: read from docker/.env.bench or https://api.minimaxi.com/anthropic.
  --api-key KEY                    Override the LLM provider API key.
                                   Default: read from docker/.env.bench or LLM_API_KEY env var.
  --debug                          Enable BENCH_DEBUG=1 artifacts.
  --keep-container                 Do not tear down the benchmark container.
  -h, --help                       Show this help.

Credentials (in priority order):
  1. --api-key / --base-url / --model CLI flags.
  2. docker/.env.bench file (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL).
  3. Environment variables (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)
      [[ $# -ge 2 ]] || { echo "--runtime requires a value" >&2; exit 2; }
      RUNTIME="$2"
      shift 2
      ;;
    --runtime=*)
      RUNTIME="${1#--runtime=}"
      shift
      ;;
    --model)
      [[ $# -ge 2 ]] || { echo "--model requires a value" >&2; exit 2; }
      CLI_MODEL="$2"
      shift 2
      ;;
    --model=*)
      CLI_MODEL="${1#--model=}"
      shift
      ;;
    --base-url)
      [[ $# -ge 2 ]] || { echo "--base-url requires a value" >&2; exit 2; }
      CLI_BASE_URL="$2"
      shift 2
      ;;
    --base-url=*)
      CLI_BASE_URL="${1#--base-url=}"
      shift
      ;;
    --api-key)
      [[ $# -ge 2 ]] || { echo "--api-key requires a value" >&2; exit 2; }
      CLI_API_KEY="$2"
      shift 2
      ;;
    --api-key=*)
      CLI_API_KEY="${1#--api-key=}"
      shift
      ;;
    --debug)
      DEBUG=1
      shift
      ;;
    --keep-container)
      KEEP_CONTAINER=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "${BENCH}" ]]; then
        echo "unexpected extra argument: $1" >&2
        usage >&2
        exit 2
      fi
      BENCH="$1"
      shift
      ;;
  esac
done

[[ -n "${BENCH}" ]] || { usage >&2; exit 2; }
case "${RUNTIME}" in
  docker|container|auto) ;;
  *) echo "unsupported runtime: ${RUNTIME} (expected docker, container, or auto)" >&2; exit 2 ;;
esac

BENCH_DIR="${ROOT}/benchmarks/${BENCH}"
[[ -d "${BENCH_DIR}" ]] || { echo "benchmark not found: ${BENCH_DIR}" >&2; exit 2; }
[[ -f "${BENCH_DIR}/env.sh" ]] || { echo "missing ${BENCH_DIR}/env.sh" >&2; exit 2; }
[[ -f "${BENCH_DIR}/metrics.py" ]] || { echo "missing ${BENCH_DIR}/metrics.py" >&2; exit 2; }

# Make docker/.env.bench values available to env_setup.sh, compose/container run,
# benchmark env.sh, metrics.py, and judge.py. Do not write these secrets into the
# sourceable runtime env file that CI uploads as an artifact.
LOCAL_ENV_FILE="${BENCH_LOCAL_ENV_FILE:-${ROOT}/docker/.env.bench}"
if [[ -f "${LOCAL_ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "${LOCAL_ENV_FILE}"
  set +a
fi
# CLI flags override .env.bench and environment variables.
[[ -n "${CLI_API_KEY}" ]] && export LLM_API_KEY="${CLI_API_KEY}"
[[ -n "${CLI_BASE_URL}" ]] && export LLM_BASE_URL="${CLI_BASE_URL}"
[[ -n "${CLI_MODEL}" ]] && export LLM_MODEL="${CLI_MODEL}"

# Backward-compat: map old MINIMAX_* vars to new LLM_* names.
[[ -z "${LLM_API_KEY:-}" && -n "${MINIMAX_API_KEY:-}" ]] && export LLM_API_KEY="${MINIMAX_API_KEY}"
[[ -z "${LLM_BASE_URL:-}" && -n "${MINIMAX_BASE_URL:-}" ]] && export LLM_BASE_URL="${MINIMAX_BASE_URL}"

[[ -n "${LLM_API_KEY:-}" ]] || {
  echo "LLM_API_KEY is not set. Use --api-key, export it, or set it in docker/.env.bench." >&2
  exit 64
}

safe_bench="$(printf '%s' "${BENCH}" | tr -c 'A-Za-z0-9_.-' '-')"
export BENCH_RUN_ID="${BENCH_RUN_ID:-local-${safe_bench}-$$}"
export BENCH_CONTAINER_RUNTIME="${RUNTIME}"
export BENCH_DEBUG="${DEBUG}"
export BENCH_RESULTS_DIR="${BENCH_RESULTS_DIR:-${ROOT}/bench-results}"
export BENCH_REPORT_PATH="${BENCH_REPORT_PATH:-${BENCH_DIR}/bench-report.json}"
export BENCH_QA_PATH="${BENCH_QA_PATH:-${BENCH_DIR}/qa.jsonl}"

cleanup() {
  local status=$?
  if [[ -z "${KEEP_CONTAINER}" && -f "${ROOT}/.bench-runtime/bench-runtime-env.sh" ]]; then
    # shellcheck disable=SC1091
    . "${ROOT}/.bench-runtime/bench-runtime-env.sh"
    bench_teardown >/dev/null 2>&1 || true
  fi
  exit "${status}"
}
trap cleanup EXIT

echo "[local-bench] benchmark=${BENCH} runtime=${RUNTIME} run_id=${BENCH_RUN_ID}"
bash "${ROOT}/benchmarks/_common/env_setup.sh"

# Load the runtime contract and helper functions for this shell. env.sh also
# sources the same file before calling bench_force_recreate.
# shellcheck disable=SC1091
. "${ROOT}/.bench-runtime/bench-runtime-env.sh"
export BENCH_ENV_FILE="${ROOT}/.bench-runtime/bench-runtime-env.sh"

echo "[local-bench] running env.sh"
bash "${BENCH_DIR}/env.sh"

echo "[local-bench] running metrics.py"
python3 "${BENCH_DIR}/metrics.py"

echo "[local-bench] report: ${BENCH_REPORT_PATH}"
if [[ -f "${BENCH_RESULTS_DIR}/${BENCH}.json" ]]; then
  echo "[local-bench] summary: ${BENCH_RESULTS_DIR}/${BENCH}.json"
fi
