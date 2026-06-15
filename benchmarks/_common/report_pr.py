#!/usr/bin/env python3
"""Render a single PR comment from every benchmark's bench-report.json.

Inputs (env):
  BENCH_RESULTS_DIR  -- directory containing <name>.json (default: bench-results)
  BENCH_BASE_SUMMARY -- optional path to a previous summary.json for delta
  BENCH_COMMENT_MARKER -- hidden HTML marker used to upsert our comment (default: openclaw-bench-report)
  GH_TOKEN / gh CLI -- for posting; if missing, the script just prints the body to stdout.

Output:
  - Prints the rendered Markdown body to stdout.
  - If gh is available and we are in a PR context, upserts a comment.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

MARKER = "<!-- openclaw-bench-report -->"


def _load(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _summarize(report: dict) -> dict:
    results = report.get("results") or []
    total = len(results)
    if total == 0:
        return {"total": 0, "passed": 0, "pass_rate": 0.0, "avg_score": 0.0, "weight": 0.0}
    weight_total = sum(float(r.get("weight", 1.0)) for r in results)
    weighted_score = sum(float(r.get("score", 0.0)) * float(r.get("weight", 1.0)) for r in results)
    passed = sum(1 for r in results if r.get("pass"))
    return {
        "total": total,
        "passed": passed,
        "pass_rate": passed / total if total else 0.0,
        "avg_score": weighted_score / weight_total if weight_total else 0.0,
    }


def _delta(bench: str, base: dict, current_summary: dict) -> str:
    base_b = base.get("benchmarks", {}).get(bench)
    if not base_b:
        return "—"
    d = current_summary["pass_rate"] - base_b.get("pass_rate", 0.0)
    arrow = "🟢" if d > 0.005 else ("🔴" if d < -0.005 else "⚪")
    return f"{arrow} {d * 100:+.1f}pp"


def render(results_dir: Path, base: dict | None) -> str:
    paths = sorted(glob.glob(str(results_dir / "*.json")))
    if not paths:
        return f"{MARKER}\n_No benchmark reports found in {results_dir}._\n"

    summaries: list[tuple[str, dict, dict]] = []
    for p in paths:
        report = _load(Path(p))
        name = report.get("benchmark") or Path(p).stem
        summaries.append((name, report, _summarize(report)))

    lines = [MARKER, "# OpenClaw Benchmark Report", ""]
    lines.append(f"- Run id: `{os.environ.get('BENCH_RUN_ID', 'local')}`")
    lines.append(f"- Commit: `{os.environ.get('BENCH_COMMIT', 'unknown')}`")
    lines.append(f"- Model: `{os.environ.get('BENCH_MODEL') or os.environ.get('LLM_MODEL', 'default')}`")
    lines.append("")
    lines.append("| Benchmark | QA | Passed | Pass rate | Avg score | Δ vs base |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for name, _, s in summaries:
        delta = _delta(name, base or {}, s) if base else "—"
        lines.append(
            f"| `{name}` | {s['total']} | {s['passed']} | "
            f"{s['pass_rate'] * 100:.1f}% | {s['avg_score']:.3f} | {delta} |"
        )
    lines.append("")

    # Top failures (max 5 across all benchmarks)
    failures: list[dict] = []
    for name, report, _ in summaries:
        for r in report.get("results") or []:
            if not r.get("pass"):
                failures.append({"bench": name, **r})
    failures.sort(key=lambda r: r.get("score", 1.0))
    if failures:
        lines.append("### Top failures")
        lines.append("")
        for f in failures[:5]:
            lines.append(f"- `{f['bench']}/{f.get('qa_id', '?')}` — {f.get('rationale', '')[:200]}")
        lines.append("")

    overall_pass = sum(s["passed"] for _, _, s in summaries)
    overall_total = sum(s["total"] for _, _, s in summaries)
    lines.append(f"**Overall:** {overall_pass}/{overall_total} passed.")
    return "\n".join(lines) + "\n"


def post_comment(body: str) -> bool:
    """Upsert the comment. Returns True on success."""
    pr = os.environ.get("BENCH_PR_NUMBER")
    repo = os.environ.get("BENCH_REPO")  # e.g. ACautomata/research-agent
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not (pr and repo and token):
        return False

    # List comments, look for one with our marker, edit or create.
    list_cmd = ["gh", "api", f"repos/{repo}/issues/{pr}/comments", "--paginate"]
    env = os.environ.copy()
    env["GH_TOKEN"] = token
    try:
        out = subprocess.run(list_cmd, capture_output=True, text=True, env=env, check=True)
    except subprocess.CalledProcessError:
        return False
    try:
        comments = json.loads(out.stdout or "[]")
    except json.JSONDecodeError:
        comments = []
    existing_id = None
    for c in comments:
        if MARKER in (c.get("body") or ""):
            existing_id = c.get("id")
            break

    if existing_id:
        edit_cmd = ["gh", "api", "-X", "PATCH",
                    f"repos/{repo}/issues/comments/{existing_id}",
                    "-f", f"body={body}"]
    else:
        edit_cmd = ["gh", "api", "-X", "POST",
                    f"repos/{repo}/issues/{pr}/comments",
                    "-f", f"body={body}"]
    try:
        subprocess.run(edit_cmd, capture_output=True, text=True, env=env, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main() -> int:
    results_dir = Path(os.environ.get("BENCH_RESULTS_DIR", "bench-results"))
    base_path = os.environ.get("BENCH_BASE_SUMMARY")
    base = None
    if base_path and Path(base_path).exists():
        base = _load(Path(base_path))
    body = render(results_dir, base)
    if not post_comment(body):
        # Always print the body so CI logs and artifact capture it.
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
