# Replication package: Can Small Code Models Improve Semantic Code Completion? Evidence from Pharo

Everything is run with one command:

```bash
./run.sh
```

It regenerates every table and figure of the paper from the released benchmark checkpoints and checks that they are identical to the paper. It needs Python 3.8+ only (standard library) and takes a few seconds.

To re-run the whole experiment from scratch instead (days, GPU), see [Re-running the benchmarks](#re-running-the-benchmarks): `./run.sh --rerun`.

## What `./run.sh` produces

`results/paper/` holds every results table and figure of the paper, as drop-in replacements for the paper's `supplemental/` files:

| Paper | File in `results/paper/` |
|---|---|
| Table I: MRR by prefix length | `tab-mrr-by-prefix.tex` |
| Table II: names returned by unconstrained and constrained generation | `tab-vocabulary-constraints.tex` |
| Table III: coverage and ranking by prefix length | `tab-reranking-coverage.tex` |
| Figure 3: mean completion time per observation | `fig-quality-and-time.tex` |
| Supplementary material | `tab-top-k-accuracy.tex`, `tab-name-validity-by-prefix.tex`, `tab-prefix-policies.tex`, `fig-package-mrr.tex` |

Figures 1 and 2 are method diagrams and contain no results.

`./run.sh` then checks the results and exits with 0 only if all three checks pass:

1. Each of the 8 generated tables and figures equals the paper's file in `expected/paper-supplemental/` (comment lines are ignored).
2. All 546 statistics equal `expected/analysis-stats.reference.json`, the statistics file the paper was written from.
3. Every number and comparison stated in the paper's text (75 claims, section by section: MRR, Top-1, Recall@10, gains, validity, list lengths, times, corpus and observation counts) is recomputed from unrounded values, and the 15 settings the paper states (search and request parameters, hardware, Ollama versions, workers, F16 weights, Pharo image) are read from the shipped source, image and provenance logs. The report is `results/verification-report.md`.

Every checkpoint is first validated with the benchmark pipeline's own validators. The statistics are also written to `results/analysis-stats.json`.

**Packages.** The study covers 47 packages of the Pharo 14 image (`data/experiment/analysed-packages.txt`), each with all 28 benchmarks (2 kinds × 14 strategies): 1,316 checkpoints, one directory per package in `data/checkpoints/`.

## Re-running the benchmarks

```bash
./run.sh --rerun                                               # EXPERIMENT_DIR=experiment, 8 benchmarks at once
BENCHMARK_JOBS=2 OLLAMA_MAX_LOADED_MODELS=1 ./run.sh --rerun   # with less GPU memory
```

Needs curl, Ollama ≥ 0.12.11 (on Linux it is downloaded automatically; elsewhere install it or set `OLLAMA_BIN`), a GPU and about 25 GB for the models. It takes days. `./run.sh --rerun`:

1. prepares the experiment in `EXPERIMENT_DIR` (default `experiment/`): it extracts the exact Pharo image (SHA-256 `5af77f5f…5859`), installs a Pharo 14 VM for your platform, copies the benchmark source of `lib/` (nothing is downloaded from GitHub), checks the image and source against the pinned hashes, and checks that the image holds the 47 packages;
2. runs the 1,316 benchmarks with `pipeline/pipeline-benchmarks.sh` and the Ollama server settings of the paper's run: `OLLAMA_NUM_PARALLEL=8`, `OLLAMA_MAX_LOADED_MODELS=4`, `OLLAMA_KEEP_ALIVE=-1` and `OLLAMA_CONTEXT_LENGTH=4096` (a server default only: every request sets `num_ctx` to 8,192 tokens, the context window reported in the paper). The pipeline pulls the four models `pharo-llm/Qwen2.5-Coder-SFT:{0.5B,1.5B,3b,7b}` (F16); the expected digests are in `data/provenance/ollama-tags.json`;
3. regenerates the paper's tables from the new checkpoints in `EXPERIMENT_DIR/paper-results/` and checks them against the paper, as `./run.sh` does.

The run is resumable: run the same command again, or set `BENCHMARK_RESUME_DIR=experiment/benchmark-run.XXXXXX`; completed benchmarks are kept.

**GPU memory.** The defaults keep all four F16 models loaded (about 25 GB) and serve 8 benchmarks at once, as on the paper's 64 GB GPUs. With less memory, Ollama keeps evicting and reloading models, and benchmarks fail with `ConnectionTimedOut: Data receive timed out` in their `worker.log`; lower the load as shown above. Quality metrics do not depend on these settings, only times do.

**What to expect.** Prompts and decoding are deterministic: temperature 0, seed 42, fixed beam search. The paper's run used Grid5000 nodes with AMD Instinct MI210 GPUs (Ollama 0.40.5, 8 workers per host); the two heuristics and most 0.5B benchmarks were completed on an Apple M4 Max (Ollama 0.40.7, 2 workers).
- **Heuristics (Baseline, Dependency):** identical to the paper.
- **CLM configurations:** expect differences of about **±0.1%** on other hardware. F16 inference rounds slightly differently across GPUs and batch sizes, so when the model scores two candidates almost equally, their order can swap.
- **Completion times:** depend on hardware and server load, and are not expected to match.

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
