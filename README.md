# Replication package: Can Small Code Models Improve Semantic Code Completion? Evidence from Pharo

This package contains everything needed to reproduce the paper:
- the benchmark checkpoints behind every reported number;
- the exact Pharo image and Smalltalk benchmark source;
- the benchmark pipeline exactly as it was run;
- the analysis that turns checkpoints into the paper's tables, figures and statistics.

| Level | Command | Needs | Time |
|---|---|---|---|
| 1. Reproduce every number in the paper from the checkpoints | `make` | Python 3.8+ (stdlib) | < 1 min |
| 2. Rebuild the frozen experiment and re-run the heuristic benchmarks | `make setup smoke` | + curl, network for the Pharo VM | ~5 min |
| 3. Re-run the benchmarks of the 47 analysed packages (1,316) | `make setup rerun` | + Ollama ≥ 0.12.11, GPU, ~25 GB of models | days |

## Level 1: reproduce the paper's results

```bash
make            # = python3 analysis/reproduce_paper.py && python3 analysis/verify_paper.py
```

`reproduce_paper.py` validates every checkpoint with the pipeline's own validators. It then writes:
- `results/paper/*.tex`: drop-in replacements for the paper's `supplemental/` tables and figures;
- `results/analysis-stats.json`.

`verify_paper.py` exits 0 only if all three checks pass:

1. Each of the 8 generated tables and figures equals the paper's file in `expected/paper-supplemental/`. Comment lines are ignored.
2. All 546 statistics equal `expected/analysis-stats.reference.json`, the statistics file the paper was written from.
3. 90 numbers quoted in the paper's text are recomputed (MRR, Top-k, gains, package sign tests, times, corpus and observation counts). See `results/verification-report.md`.

**Matched population.** Only packages whose 28 benchmarks (2 kinds × 14 strategies) all completed are analysed. That is 47 of the 50 packages selected with seed 42 from 733 eligible packages. Three packages were excluded because their runs did not finish: Slot-Tests (18 of 28 benchmarks), Reflectivity-Tests (15) and Morphic-Widgets-Windows (18). Missing benchmarks are never filled with zeros.

## Level 2: frozen experiment and smoke test

```bash
make setup smoke EXPERIMENT_DIR=experiment
```

`rerun/setup-frozen-experiment.sh` does the following:
- extracts the exact image (SHA-256 `5af77f5f…5859`);
- installs a Pharo 14 VM for your platform;
- checks the image and source against the pinned hashes;
- checks that the image sees the same 733 eligible packages as the saved selection.

`rerun/smoke-test.sh` re-runs the deterministic heuristic benchmarks of one package with the original worker. It checks that counts, Top-k hits and reciprocal-rank sums equal the released checkpoints (Network-Mail by default; `rerun/smoke-test.sh DIR PACKAGE` for another).

## Level 3: re-run the benchmarks

```bash
make setup rerun EXPERIMENT_DIR=experiment BENCHMARK_JOBS=8
```

The re-run benchmarks the 47 packages the paper analyses (`data/experiment/analysed-packages.txt`): 47 × 28 = 1,316 benchmarks. The three packages whose runs did not finish are not in the paper, so they are not re-run. To run all 50 selected packages instead, set `BENCHMARK_PACKAGES_FILE=data/experiment/benchmark-selection.json`. The package list does not change any result: each benchmark measures its own package, and the packages left out of the list are not used by any benchmark.

`rerun/run-benchmarks.sh` runs `pipeline/pipeline-benchmarks.sh` unchanged (its `BENCHMARK_PACKAGES_FILE` option gives the package list), with the Ollama server settings of the paper's run: `OLLAMA_NUM_PARALLEL=8`, `OLLAMA_MAX_LOADED_MODELS=4`, `OLLAMA_KEEP_ALIVE=-1` and `OLLAMA_CONTEXT_LENGTH=4096`. On Linux, the pipeline downloads Ollama itself; elsewhere, install it or set `OLLAMA_BIN`. The pipeline pulls the four models `pharo-llm/Qwen2.5-Coder-SFT:{0.5B,1.5B,3b,7b}` (F16); the expected digests are in `data/provenance/ollama-tags.json`.

**GPU memory.** The defaults keep all four F16 models loaded (about 25 GB) and serve 8 benchmarks at once, as on the paper's 64 GB GPUs. With less memory, Ollama keeps evicting and reloading models, and benchmarks fail with `ConnectionTimedOut: Data receive timed out` in their `worker.log`. Lower the load instead, e.g. on a 36 GB Apple-silicon Mac: `BENCHMARK_JOBS=2 OLLAMA_MAX_LOADED_MODELS=1`. Quality metrics do not depend on these settings, only times do.

An interrupted run resumes with `BENCHMARK_RESUME_DIR=experiment/benchmark-run.XXXXXX`. Completed benchmarks are kept. Afterwards, the paper tables of the new run are in `experiment/paper-results/`, and `analysis/verify_paper.py --results experiment/paper-results` compares them with the paper.

On clusters, use `pipeline/job.oar.sh` (Grid5000/OAR), `pipeline/submit-shared.sh` (several hosts sharing one run) or `pipeline/job.fir.sh` (Slurm).

**What to expect.** Prompts and decoding are deterministic: temperature 0, seed 42, fixed beam search. Quality metrics should therefore match up to numerical differences across GPU and Ollama versions. The paper's run used AMD Instinct MI210 GPUs, 8 workers per host. Completion times depend on hardware and server load, and are not expected to match.

## Contents

| Path | What |
|---|---|
| `data/checkpoints/NNNN/benchmarks/<kind>-<strategy>/part.json` | 1,367 checkpoints: per package × kind × strategy × prefix (2–8): observations, Top-1/2/3/10 hits, reciprocal-rank sum, time, Pharo memory change, generated/valid candidates |
| `data/experiment/` | Saved package selection (50, seed 42), the 47 analysed packages, image/source pins, model tags |
| `data/provenance/` | `workers.json` (run ID, input SHA-256s), model digests, per-task timings and hosts, worker invocations, job and Ollama logs (usernames anonymized) |
| `benchmark-source/` | Frozen Smalltalk benchmark source loaded in the image |
| `frozen-image/` | The exact Pharo 14 image, changes and sources files |
| `pipeline/` | Benchmark pipeline and its 38 tests, byte-identical to the run; `workers.json` pins three of these files |
| `analysis/` | `reproduce_paper.py`, `verify_paper.py` |
| `rerun/` | Setup, smoke test and full re-run wrappers |
| `expected/` | The paper's supplemental files and reference statistics |
| `results/` | Output of `make`, as shipped |
| `docs/METHODOLOGY.md` | Protocol, metrics, execution and limitations in detail |
| `tests/` | Tests of the analysis (`make test`); pipeline tests: `make test-pipeline` |
| `SHA256SUMS` | Checksums of every shipped file (`make checksums`) |

## Strategy names

The checkpoints use internal names; the paper uses these labels:

| Checkpoint | Paper |
|---|---|
| `heuristicsBaseline` | Baseline |
| `heuristicsDependency` | Dependency |
| `llmUnvalidated{05B,15B,3B,7B}` | Unconstrained generation |
| `llm{05B,15B,3B,7B}` | Vocabulary-constrained generation |
| `hybrid{05B,15B,3B,7B}` | Dependency + CLM reranking |

`messages` = method selectors; `variables` = class names.
