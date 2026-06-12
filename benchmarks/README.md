# Benchmarks

Evaluation benchmarks for testing agent capabilities in this multi-agent research system.
The CI workflow (`.github/workflows/benchmark.yml`) runs every benchmark in a dockerized
OpenClaw environment and posts the results as a PR comment.

## Structure

```
benchmarks/
├── README.md                          # This file
├── _common/                           # Shared CI interface (do not put a benchmark here)
│   ├── qa_schema.json                 # JSON Schema for qa.jsonl
│   ├── env_setup.sh                   # Unified env: boot container, health check (docker + container CLI)
│   ├── run_bench.py                   # Generic driver; all metrics.py shim to this
│   ├── run_local_benchmark.sh         # Local single-benchmark runner (docker or Apple container CLI)
│   ├── judge.py                       # Reusable rule/agent judges
│   └── report_pr.py                   # Aggregator + PR comment via `gh api`
├── idea-generate/                     # Benchmarks — each must have env.sh + metrics.py + qa.jsonl
├── paper-review/
├── paper-review-pipeline/
├── paper-ingest/
├── idea-generation/
└── autoresearch/
```

## CI policy (binding — see CLAUDE.md "Benchmark 流程")

1. **Main agent only for benchmark tasks.** The CI invokes `openclaw agent --agent main ...` for each QA task.
   Each QA may declare `target_agent` (autoresearch / paper-review / idea-generate / reviewer);
   `run_bench.py` wraps the prompt with a `[BENCHMARK DIRECTIVE]` instructing main to
   use `sessions_spawn(agentId=target_agent, task=...)` and return the sub-agent's
   final reply verbatim. No benchmark task is allowed to call a task sub-agent directly.
   When `judge: "agent"` is used, the reusable judge runs the dedicated `reviewer`
   agent for scoring.
2. **Unified env first.** `benchmarks/_common/env_setup.sh` must run before any
   benchmark's own `env.sh`. It boots a containerized OpenClaw environment
   (Docker Compose by default, Apple `container` CLI as fallback), rsyncs the
   repo into the container at `/home/node/.openclaw`, and waits for `openclaw health`.
3. **QA schema.** Each `benchmarks/<name>/qa.jsonl` is one JSON per line, conformant
   with `benchmarks/_common/qa_schema.json`. Required: `qa_id`, `question`,
   `agent: "main"`. Optional but recommended: `target_agent`, `gold_answer`,
   `rubric`, `expected_artifacts`. Use `judge: "agent"` when scoring needs the
   strict reviewer LLM judge instead of rule coverage.
4. **Metrics reuse.** `metrics.py` is a 6-line shim that calls
   `benchmarks/_common/run_bench.py:main(name, agent_id="main")`. Custom
   judges must be added in `benchmarks/_common/judge.py`, not duplicated.
5. **PR comment.** `report_pr.py` reads every `bench-results/<name>.json` and
   posts (or upserts) a single Markdown comment with per-benchmark pass rate
   and average score.

## Adding a new benchmark

1. Create `benchmarks/<name>/{env.sh,metrics.py,qa.jsonl}`. Keep `env.sh` small
   (fixture staging only); the heavy lifting is `qa.jsonl`.
2. Add `<name>` to the `BENCH_TARGETS` list in `.github/workflows/benchmark.yml`.
3. Open a PR. The CI workflow will pick it up automatically; the PR comment
   will include the new benchmark's results.

## Running locally

```bash
# 1) Prepare the .env (one-time)
cp docker/.env.bench.example docker/.env.bench
# then edit docker/.env.bench and set MINIMAX_API_KEY.
# Optionally set MODEL_ID / PRIMARY_MODEL to use a different LLM.

# 2) Run exactly one benchmark in the local containerized CI env.
# Auto prefers a running Docker daemon, then falls back to Apple's `container` CLI.
benchmarks/_common/run_local_benchmark.sh idea-generate-1

# Force a runtime when needed:
benchmarks/_common/run_local_benchmark.sh --runtime docker idea-generate-1
benchmarks/_common/run_local_benchmark.sh --runtime container idea-generate-1

# Override model, base URL, or API key on the command line:
benchmarks/_common/run_local_benchmark.sh --model gpt-4o --base-url https://api.openai.com/v1 --api-key sk-xxx idea-generate-1

# Optional: keep the container around for inspection, or dump BENCH_DEBUG artifacts.
benchmarks/_common/run_local_benchmark.sh --keep-container --debug paper-ingest

# 3) Advanced/manual equivalent
bash benchmarks/_common/env_setup.sh
source .bench-runtime/bench-runtime-env.sh
bash benchmarks/idea-generate-1/env.sh
python3 benchmarks/idea-generate-1/metrics.py
cat benchmarks/idea-generate-1/bench-report.json | jq
```

## Legacy notes

The original `spec.md` files remain under each benchmark directory; the unified
QA schema and CI contract are the source of truth for *how* benchmarks run, but
the spec files still describe the *what* (capability, scoring intent, examples).
