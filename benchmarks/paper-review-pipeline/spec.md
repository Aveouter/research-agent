# Benchmark: Paper Review Pipeline

**Agent:** paper-review
**Capability:** 5-stage paper analysis pipeline

## Purpose

Evaluate the paper-review agent's ability to execute the full 5-stage analysis pipeline on a research paper, producing well-structured outputs at each stage that can serve as inputs for the next stage.

## Pipeline Stages

1. **paper-wiki-entry-organizer** — Produce a structured wiki entry from the paper
2. **paper-experiment-deep-extractor** — Extract detailed experiment information
3. **paper-review-style-problem-analyzer** — Generate review-style critique and questions
4. **paper-validation-experiment-designer** — Design validation experiments
5. **codex-validation-task-prompt-generator** — Generate prompts for Codex execution

## Inputs

- A paper (PDF or text) provided to the agent
- The paper may be one already ingested in the autoresearch wiki, or a new paper

## Procedure

1. Send a full-pipeline request to the paper-review agent.
2. Evaluate each stage output independently.
3. Evaluate whether outputs chain correctly between stages.

## Evaluation Criteria

### Per-Stage (scored 0-2)

| Stage | 0 (Fail) | 1 (Partial) | 2 (Pass) |
|-------|----------|-------------|----------|
| Wiki entry | Missing or unreadable | Present but missing key sections | All required sections filled with substance |
| Experiment extraction | No numbers extracted | Some numbers but incomplete | Full extraction: datasets, sizes, baselines, hyperparameters, metrics |
| Problem analysis | Generic or unfounded critique | Some valid points but lacks depth | Specific, evidence-grounded, constructive critique with clear severity ratings |
| Validation design | Unfeasible or vague experiments | Reasonable but hard to attribute | Small-scale, controlled, attributable experiments reusing original setup |
| Codex prompts | Not runnable | Runnable but ambiguous | Specific, self-contained prompts with expected outputs and success criteria |

### Cross-Stage Quality

| Criterion | Description |
|-----------|-------------|
| **Output chainability** | Each stage's output can serve as input to the next without manual reformatting |
| **No fabrication** | No claims that aren't traceable to the paper text |
| **Uncertainty marking** | Missing information explicitly noted rather than guessed |
| **Markdown suitability** | All outputs are valid Markdown suitable for file storage |

### Scoring

- **Pass**: Per-stage total >= 7/10 + all cross-stage criteria met
- **Strong pass**: Per-stage total >= 9/10 + all cross-stage criteria met
- **Fail**: Any stage scores 0, or cross-stage criteria not met

## Variations

- **Single-stage**: Run only one stage to test isolated skill quality.
- **Partial pipeline**: Run stages 1-3 to test analysis without experiment design.
- **Full pipeline**: Run all 5 stages end-to-end.
