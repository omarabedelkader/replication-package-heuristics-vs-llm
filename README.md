# Replication package: Can Small Code Models Improve Semantic Code Completion? Evidence from Pharo

Everything is run with one command:

```bash
./run.sh
```

## What `./run.sh` produces

`results/paper/` holds every results table and figure of the paper, as drop-in replacements for the paper's `supplemental/` files:

| Paper | File |
|---|---|
| Table I: MRR by prefix length | `tab-mrr-by-prefix.tex` |
| Table II: names returned by (un)constrained generation | `tab-vocabulary-constraints.tex` |
| Table III: coverage and ranking by prefix length | `tab-reranking-coverage.tex` |
| Figure 3: mean completion time per observation | `fig-quality-and-time.tex` |
| Supplementary | `tab-top-k-accuracy.tex`, `tab-name-validity-by-prefix.tex`, `tab-prefix-policies.tex`, `fig-package-mrr.tex` |

Figures 1 and 2 are method diagrams and contain no results.

`./run.sh` then checks the regenerated results against the paper (`analysis/verify_paper.py`), with three checks:

1. every generated file is identical to the paper's supplemental file (`expected/paper-supplemental/`, comment lines ignored);
2. all 546 statistics are identical to `expected/analysis-stats.reference.json`;
3. every number and comparison in the paper's text (abstract to conclusion), and every stated setting (inference, search, timeout, hardware, Ollama versions, workers, image), is recomputed from the checkpoints, the benchmark source and the provenance. Each one is listed in `results/verification-report.md`.

It exits with status 0 only if all checks pass.

## The 47 packages

`data/experiment/analysed-packages.txt` lists the 47 analysed packages, with one checkpoint directory each in `data/checkpoints/`.

## Re-running the benchmarks

```bash
./run.sh --rerun                                               # EXPERIMENT_DIR=experiment, 8 benchmarks at once
BENCHMARK_JOBS=2 OLLAMA_MAX_LOADED_MODELS=1 ./run.sh --rerun   # with less GPU memory
```

## Contents

| Path | What |
|---|---|
| `run.sh` | The single entry point |
| `data/checkpoints/<package>/benchmarks/<kind>-<strategy>/part.json` | 1,316 checkpoints, one directory for each of the 47 packages (47 × 28): per package × kind × strategy × prefix (2–8): observations, Top-1/2/3/10 hits, reciprocal-rank sum, time, Pharo memory change, generated/valid candidates |
| `data/experiment/` | The 47 packages, image/source pins, model tags |
| `data/provenance/` | `workers.json` (run ID, input SHA-256s), model digests, per-task timings and hosts, worker invocations, job and Ollama logs (usernames anonymized) |
| `lib/HeuristicCompletion-Benchmarks-Multiples/` | Frozen Smalltalk benchmark source loaded in the image; the pipeline always uses this copy and downloads nothing from GitHub |
| `frozen-image/` | The exact Pharo 14 image, changes and sources files |
| `pipeline/` | Benchmark pipeline used by `./run.sh --rerun`, with its tests; `workers.json` pins three of these files (unchanged) |
| `analysis/` | `reproduce_paper.py` (tables, figures, statistics) and `verify_paper.py` (checks against the paper), called by `./run.sh` |
| `expected/` | The paper's supplemental files and reference statistics |
| `results/` | Output of `./run.sh`, as shipped |
| `tests/` | Tests of the analysis |
| `SHA256SUMS` | Checksums of every shipped file (`shasum -a 256 -c SHA256SUMS`) |

## Strategy names

The checkpoints use internal names; the paper uses these labels:

| Checkpoint | Paper |
|---|---|
| `heuristicsBaseline` | Baseline |
| `heuristicsDependency` | Dependency |
| `llmUnvalidated{05B,15B,3B,7B}` | Unconstrained generation |
| `llm{05B,15B,3B,7B}` | Constrained generation |
| `hybrid{05B,15B,3B,7B}` | CLM reranking (of Dependency's candidates) |

`messages` = method selectors; `variables` = class names.
