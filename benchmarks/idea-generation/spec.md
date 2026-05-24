# Benchmark: Idea Generation

**Skill:** idea-generate (main agent skill)
**Capability:** Research idea generation from paper evidence

## Purpose

Evaluate the idea-generate skill's ability to produce structured, evidence-grounded research ideas from a set of input papers.

## Inputs

- A `paper/` directory containing 2-5 related research papers
- Optional: topic description and constraints

## Procedure

1. Place papers in a test `paper/` directory.
2. Run the idea-generate skill (full demo workflow or core workflow).
3. Evaluate the output artifacts in the generated run directory.

## Output Artifacts

Expected files in the run directory:

- `paper-context.md` — extracted paper context
- `paper-context.json` — structured context data
- `paper-analysis.md` — cross-paper analysis
- `ideas.dedup.json` — deduplicated idea cards
- `recommended-ideas.md` — final output

## Evaluation Criteria

### Hard Rules (any violation = automatic fail)

| Rule | Description |
|------|-------------|
| Evidence grounding | Every idea traces back to paper evidence in `paper-context.md` |
| Minimum validation | Each idea includes at least one concrete validation experiment |
| Metric named | Each idea specifies at least one metric it expects to change |
| Risk identified | Each idea acknowledges at least one failure mode |
| No fabrication | No claims that don't appear in extracted paper context |

### Quality Dimensions (scored 0-2 each)

| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| **Novelty** | All ideas are restatements of paper future work | Some new combinations or angles | Genuine synthesis with non-obvious connections |
| **Testability** | Ideas too vague to test | Testable but underspecified | Clear experimental setup with expected outcomes |
| **Cross-paper synthesis** | Ideas drawn from single papers only | Some cross-paper connections | Rich transferable insights between papers |
| **Idea card structure** | Missing required fields | All fields present but some weak | Well-structured cards with strong rationale and evidence |
| **Signal-to-noise** | Many weak or duplicate ideas | Some filtering but mixed quality | 5-10 high-signal, well-differentiated ideas |

### Scoring

- **Pass**: All hard rules met + quality score >= 6/10
- **Strong pass**: All hard rules met + quality score >= 8/10
- **Fail**: Any hard rule violated

## Test Scenarios

- **Familiar domain**: Papers from an existing wiki domain (tests reuse of wiki knowledge)
- **Novel domain**: Papers from a new research area (tests cold-start capability)
- **Contradictory papers**: Papers with conflicting findings (tests tension handling)
- **Single paper**: Only one input paper (tests depth of extraction)
