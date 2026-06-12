#!/usr/bin/env python3
"""Reusable scoring for benchmark metrics.py scripts.

Two judges:
  judge_with_rules(answer, qa)  -- rule-based, uses qa.gold_answer and must_contain-style hints.
  judge_with_agent(qa, answer, agent_id, model=None) -- LLM judge via direct `openclaw agent --agent reviewer`.

Both return a dict: {score: float (0-1), pass: bool, rationale: str, dimensions?: dict}.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import uuid
from typing import Any

# --- Rule-based judge --------------------------------------------------------

_KEYWORD_HINT = re.compile(r"必须[：:]\s*([^\n]+)|must_contain[：:]\s*([^\n]+)", re.I)


def _extract_must_contain(gold: Any) -> list[str]:
    """Pull a flat list of required tokens out of a gold_answer.

    Recognized shapes:
      - string: "Term1\nTerm2" (one per line) or "Term1, Term2"
      - object: {"must_contain": ["Term1", ...]} or {"fields": [...]}
    """
    if gold is None:
        return []
    if isinstance(gold, str):
        m = _KEYWORD_HINT.search(gold)
        if m:
            tail = m.group(1) or m.group(2) or ""
            return [t.strip() for t in re.split(r"[\n,，；;]", tail) if t.strip()]
        return [t.strip() for t in re.split(r"[\n,，；;]", gold) if t.strip() and len(t.strip()) > 1]
    if isinstance(gold, dict):
        out = list(gold.get("must_contain") or [])
        out += list(gold.get("fields") or [])
        return [str(t) for t in out if str(t).strip()]
    return []


def judge_with_rules(answer: str, qa: dict) -> dict:
    """Score an answer against qa.gold_answer with simple keyword coverage.

    Score = covered / required (0 if no requirements). Pass when score >= qa.pass_threshold.
    """
    required = _extract_must_contain(qa.get("gold_answer"))
    if not required:
        # No gold answer means we can only do a soft pass: not-empty + length sanity.
        text = (answer or "").strip()
        if not text:
            return {"score": 0.0, "pass": False, "rationale": "empty answer, no gold to check against"}
        score = min(1.0, len(text) / 200.0)
        return {"score": score, "pass": score >= qa.get("pass_threshold", 0.5),
                "rationale": f"no gold_answer; scored on length={len(text)}"}

    text = (answer or "").lower()
    missing = [r for r in required if r.lower() not in text]
    covered = len(required) - len(missing)
    score = covered / len(required)
    return {
        "score": round(score, 4),
        "pass": score >= qa.get("pass_threshold", 0.5),
        "rationale": f"covered {covered}/{len(required)}; missing={missing[:5]}",
        "missing": missing,
    }


def _container_cli() -> str:
    """Return the container runtime CLI used for benchmark exec calls."""
    cli = os.environ.get("BENCH_CONTAINER_CLI") or os.environ.get("BENCH_CONTAINER_RUNTIME") or "docker"
    return "docker" if cli == "auto" else cli


# --- LLM judge ---------------------------------------------------------------


def _extract_judge_text(stdout: str) -> str:
    """Extract the reviewer text from `openclaw agent --json` stdout."""
    text = stdout or ""
    if not text.strip():
        return ""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text

    if isinstance(data, dict):
        if "score" in data:
            return json.dumps(data, ensure_ascii=False)
        payloads = data.get("payloads")
        if isinstance(payloads, list):
            joined = "\n".join(
                str(p.get("text", "")) for p in payloads
                if isinstance(p, dict) and p.get("text")
            )
            if joined.strip():
                return joined
        result = data.get("result")
        if isinstance(result, dict):
            payloads = result.get("payloads")
            if isinstance(payloads, list):
                joined = "\n".join(
                    str(p.get("text", "")) for p in payloads
                    if isinstance(p, dict) and p.get("text")
                )
                if joined.strip():
                    return joined
    return text


def judge_with_agent(qa: dict, answer: str, agent_id: str = "reviewer",
                     model: str | None = None, timeout: int = 600,
                     container: str | None = None) -> dict:
    """Run a one-shot LLM judge by directly invoking the reviewer agent.

    The reviewer prompt asks for a JSON verdict: {"score": 0-1, "rationale": "..."}.
    Falls back to rule scoring if the CLI is unavailable.

    The judge call is bounded by `timeout` (default 600s) plus a 30s grace on
    the subprocess side; a hung judge therefore cannot stall the whole
    benchmark run. The fallback to rule scoring is tagged so the report
    shows the difference between a real judge verdict and a degraded one.
    """
    agent_id = "reviewer"
    rubric = qa.get("rubric") or "Score how well the answer matches the gold answer on a 0-1 scale."
    gold = qa.get("gold_answer")
    prompt = (
        "You are the dedicated OpenClaw Reviewer agent: honest, uncompromising, and fair. "
        "Read the QA, the reference answer, the rubric, and the candidate. "
        "Score strictly according to the rubric and required fields. "
        "Reply with a single JSON object only: {\"score\": <0..1>, \"rationale\": \"<one short sentence>\"}.\n\n"
        f"QA: {qa.get('question', '')}\n\n"
        f"REFERENCE: {json.dumps(gold, ensure_ascii=False) if gold else '(none)'}\n\n"
        f"RUBRIC: {rubric}\n\n"
        f"PASS_THRESHOLD: {qa.get('pass_threshold', 0.5)}\n\n"
        f"CANDIDATE:\n{(answer or '')[:8000]}\n"
    )

    session_key = f"agent:{agent_id}:bench-judge-{os.getpid()}-{uuid.uuid4().hex}"
    cmd = ["openclaw", "agent", "--agent", agent_id, "--message", prompt, "--json", "--local",
           "--session-key", session_key, "--timeout", str(timeout)]
    container = container or os.environ.get("BENCH_CONTAINER")
    if container:
        cmd = [
            _container_cli(), "exec", "-i",
            "-e", "MINIMAX_API_KEY", "-e", "MINIMAX_BASE_URL",
            container,
        ] + cmd
    if model:
        cmd += ["--model", model]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
    except subprocess.TimeoutExpired as e:
        # Fallback: degrade to rules so the report still has a score, but
        # surface the timeout so the PR comment can flag it. Without this
        # tag a 10-minute judge hang would be indistinguishable from a
        # normal rule-based pass.
        fallback = judge_with_rules(answer, qa)
        fallback["rationale"] = f"agent judge timed out after {timeout}s ({e}); " + fallback["rationale"]
        return fallback
    except FileNotFoundError as e:
        fallback = judge_with_rules(answer, qa)
        fallback["rationale"] = f"agent judge unavailable ({e}); " + fallback["rationale"]
        return fallback

    # Only look at stdout for the JSON verdict; with --json, diagnostics
    # are routed to stderr (per docs.openclaw.ai/tools/agent-send).  OpenClaw
    # normally wraps replies in payloads[].text, so extract that before looking
    # for the reviewer's requested JSON verdict.
    text = _extract_judge_text(out.stdout or "")
    m = re.search(r"\{.*?\"score\".*?\}", text, re.S)
    if not m:
        fallback = judge_with_rules(answer, qa)
        fallback["rationale"] = f"agent judge parse fail; " + fallback["rationale"]
        return fallback
    try:
        verdict = json.loads(m.group(0))
        score = float(verdict.get("score", 0.0))
    except (ValueError, TypeError):
        fallback = judge_with_rules(answer, qa)
        fallback["rationale"] = "agent judge JSON parse fail; " + fallback["rationale"]
        return fallback
    score = max(0.0, min(1.0, score))
    return {"score": round(score, 4),
            "pass": score >= qa.get("pass_threshold", 0.5),
            "rationale": str(verdict.get("rationale", ""))[:500]}


# --- Entry point for direct CLI use -----------------------------------------


def main() -> int:
    """CLI: `python3 judge.py rules|agent <qa.json> <answer.txt>` prints JSON verdict."""
    if len(sys.argv) != 4:
        print("usage: judge.py {rules|agent} <qa.json> <answer.txt>", file=sys.stderr)
        return 2
    mode, qa_path, ans_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(qa_path, "r", encoding="utf-8") as f:
        qa = json.load(f)
    with open(ans_path, "r", encoding="utf-8") as f:
        answer = f.read()
    if mode == "rules":
        verdict = judge_with_rules(answer, qa)
    elif mode == "agent":
        verdict = judge_with_agent(qa, answer)
    else:
        print(f"unknown mode: {mode}", file=sys.stderr)
        return 2
    print(json.dumps(verdict, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
