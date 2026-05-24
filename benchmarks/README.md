# Benchmarks

Evaluation benchmarks for testing agent capabilities in this multi-agent research system.

## Structure

```
benchmarks/
├── README.md                          # This file
├── paper-ingest/                      # Autoresearch agent benchmarks
│   ├── spec.md                        # Benchmark specification
│   └── datasets/                      # Test datasets
│       └── sample-papers/             # Sample paper fixtures
├── paper-review-pipeline/             # Paper-review agent benchmarks
│   └── spec.md                        # Benchmark specification
└── idea-generation/                   # Main agent skill benchmarks
    └── spec.md                        # Benchmark specification
```

## Running Benchmarks

Benchmarks are designed to be executed by agents or humans against live agent sessions. Each benchmark spec defines:

- **Purpose** — what capability is being evaluated
- **Inputs** — test fixtures and data provided to the agent
- **Evaluation criteria** — what counts as a passing result
- **Scoring rubric** — how to grade the output

## Adding New Benchmarks

1. Create a directory under `benchmarks/<benchmark-name>/`
2. Add a `spec.md` with the benchmark specification
3. Add test fixtures under `datasets/` if needed
4. Keep benchmarks independent — each should be runnable in isolation
