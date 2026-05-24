# Benchmark: Paper Ingest

**Agent:** autoresearch
**Capability:** Paper ingestion and wiki page creation

## Purpose

Evaluate the autoresearch agent's ability to ingest a research paper and produce a complete, well-structured wiki page that meets the minimum quality bar defined in `workspace-autoresearch/AGENTS.md`.

## Inputs

- A PDF or text-extracted paper placed in `datasets/sample-papers/`
- Target domain specified by the evaluator

## Procedure

1. Place the test paper in `raw/inbox/` of the autoresearch workspace.
2. Send an ingest request to the autoresearch agent (e.g. "ingest this paper into the `<domain>` domain").
3. After completion, evaluate the output against the criteria below.

## Evaluation Criteria

### Must Have (minimum bar — any failure = 0 points)

| Criterion | Description |
|-----------|-------------|
| Raw source captured | Paper file exists in `raw/sources/` with canonical naming |
| Paper page created | Wiki page exists at `wiki/domains/<domain>/papers/<slug>.md` |
| Frontmatter complete | Has `title`, `type: paper`, `domain`, `evidence_level`, `created`, `updated` |
| Concrete results | At least one concrete number (accuracy, FPR, etc.) in Results section |
| Index updated | `wiki/index.md` lists the new paper page |
| Log entry | `wiki/log.md` has an append-only entry for this ingest |

### Quality Dimensions (scored 0-2 each)

| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| **Experiments detail** | Missing or vague | Datasets/baselines named but incomplete | Full dataset sizes, baselines, hyperparameters, evaluation protocol |
| **Results specificity** | No numbers or only qualitative | Some numbers but gaps in coverage | Best method, strongest baseline, and gap for each main claim |
| **Cross-page updates** | Only paper page touched | 1-2 related pages updated | Relevant method/dataset/task/metric/topic pages also updated |
| **Bibliographic metadata** | Title only | Title + authors + year | Full: authors, year, venue, DOI/arXiv, code links |
| **Atomic claims** | None | 1-2 claims | Meaningful atomic claims on relevant topic/comparison pages |

### Scoring

- **Pass**: All "Must Have" criteria met + total quality score >= 6/10
- **Strong pass**: All "Must Have" criteria met + total quality score >= 8/10
- **Fail**: Any "Must Have" criterion missing

## Test Datasets

### sample-papers/

Place representative papers here. Each test run should use a paper not previously ingested into the wiki. Suggested categories:

- A well-known paper in an existing domain (tests quality on familiar ground)
- A paper in a new domain (tests domain creation and placement decisions)
- A short paper / letter (tests handling of limited content)
