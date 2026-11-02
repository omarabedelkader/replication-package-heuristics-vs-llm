# Replication package: Can Small Code Models Improve Semantic Code Completion? Evidence from Pharo

## Run

```bash
./run.sh
```

Needs Python 3.8+ only, and takes seconds. `./run.sh` does two things:

1. It regenerates every table and figure of the paper from the benchmark checkpoints into `results/paper/`.
2. It checks them against the paper.

## Summary

| Paper | File in `results/paper/` |
|---|---|
| Table I: MRR by prefix length | `tab-mrr-by-prefix.tex` |
| Table II: names returned by (un)constrained generation | `tab-vocabulary-constraints.tex` |
| Table III: coverage and ranking by prefix length | `tab-reranking-coverage.tex` |
| Figure 3: mean completion time | `fig-quality-and-time.tex` |
| Figure 4: MRR against completion time | `fig-summary.tex` |
| Additional results (not in the paper) | `tab-top-k-accuracy.tex`, `tab-name-validity-by-prefix.tex`, `tab-prefix-policies.tex`, `fig-package-mrr.tex` |

Figures 1 and 2 show the method and contain no results.

## Re-run the benchmarks

```bash
./run.sh --rerun
```

This re-runs the 1,034 benchmarks (47 packages × 2 tasks × 11 configurations) in the frozen Pharo image with the three models served by Ollama, then checks the new results the same way. It needs a GPU and about 25 GB for the models, and it takes days. Completion times depend on the hardware, so those checks will differ. `./run.sh --help` lists the options.

## Contents

| Path | What |
|---|---|
| `run.sh` | The only command |
| `data/checkpoints/` | The results of the paper's run: one folder per package, one `part.json` per task × configuration, with the counts, hits, reciprocal-rank sums and times for each prefix length |
| `data/experiment/` | The 47 packages, the model names and digests, and the SHA-256 of the image |
| `lib/` | The Smalltalk benchmark source |
| `frozen-image/` | The Pharo 14 image of the paper's run |
| `pipeline/` | The benchmark pipeline used by `--rerun`, with its tests |
| `analysis/` | `reproduce_paper.py` (builds the tables and figures) and `verify_paper.py` (compares them with the paper) |
| `expected/` | The paper's table and figure files, and the reference statistics |
| `results/` | The output of `./run.sh` |
| `tests/` | Tests of the analysis (`python3 -m unittest tests/test_analysis.py`) |
| `SHA256SUMS` | Checksums of every file (`shasum -a 256 -c SHA256SUMS`) |

## Configuration names

| In the checkpoints | In the paper |
|---|---|
| `heuristicsBaseline` | Baseline |
| `heuristicsDependency` | Dependency |
| `llmUnvalidated15B`, `llmUnvalidated3B`, `llmUnvalidated7B` | Unconstrained generation (1.5B, 3B, 7B) |
| `llm15B`, `llm3B`, `llm7B` | Constrained generation |
| `hybrid15B`, `hybrid3B`, `hybrid7B` | CLM reranking |

`messages` are method selectors, and `variables` are class names.
