#!/usr/bin/env bash
# Re-run the benchmarks of the 47 packages analysed in the paper (47 x 2 kinds x 14
# strategies = 1,316 benchmarks) in an experiment prepared by setup-frozen-experiment.sh,
# with the original pipeline (pipeline/, unchanged) and the Ollama settings of the paper's
# run, then regenerate the paper's tables from the new checkpoints.
#
# Usage: rerun/run-benchmarks.sh EXPERIMENT_DIR
#   BENCHMARK_PACKAGES_FILE  packages to run (default data/experiment/analysed-packages.txt;
#                            data/experiment/benchmark-selection.json for all 50 selected)
#   BENCHMARK_JOBS         simultaneous benchmarks (default 8, as in the paper's run)
#   BENCHMARK_RESUME_DIR   continue an interrupted EXPERIMENT_DIR/benchmark-run.* directory
#   OLLAMA_BIN, OLLAMA_MODELS_DIR, BENCHMARK_OLLAMA_HOST  see pipeline/pipeline-benchmarks.sh --help
# Needs Ollama >= 0.12.11 (on Linux the pipeline downloads it) and about 25 GB for the models.

set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 1 || "$1" == -h || "$1" == --help ]]; then
    sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
    exit $(( $# != 1 ))
fi
export EXPERIMENT_DIR="$(cd "$1" && pwd -P)"
if [[ ! -f "$EXPERIMENT_DIR/image-source.json" || ! -d "$EXPERIMENT_DIR/repository" ]]; then
    echo "$EXPERIMENT_DIR is not prepared; run rerun/setup-frozen-experiment.sh first." >&2
    exit 1
fi
export BENCHMARK_REPO_DIR="$PACKAGE_DIR/lib/HeuristicCompletion-Benchmarks-Multiples"
export BENCHMARK_PACKAGES_FILE="${BENCHMARK_PACKAGES_FILE:-$PACKAGE_DIR/data/experiment/analysed-packages.txt}"
export RESULTS_DIR="${RESULTS_DIR:-$EXPERIMENT_DIR/results}"
export BENCHMARK_JOBS="${BENCHMARK_JOBS:-8}"
# Server settings of the paper's run (pipeline/job.oar.sh).
export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-$BENCHMARK_JOBS}"
export OLLAMA_MAX_LOADED_MODELS="${OLLAMA_MAX_LOADED_MODELS:-4}"
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:--1}"
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-4096}"

status=0
bash "$PACKAGE_DIR/pipeline/pipeline-benchmarks.sh" --foreground || status=$?

# Analyse what is complete, even after an interruption (incomplete packages are excluded).
runs=("$EXPERIMENT_DIR"/benchmark-run.*/)
run="${BENCHMARK_RESUME_DIR:-${runs[${#runs[@]}-1]%/}}"
"${PIPELINE_PYTHON:-python3}" "$PACKAGE_DIR/analysis/reproduce_paper.py" \
    --checkpoints "$run/packages" --workers "$run/workers.json" \
    --selection "$EXPERIMENT_DIR/benchmark-selection.json" --out "$EXPERIMENT_DIR/paper-results" || true
echo "Paper tables from this run: $EXPERIMENT_DIR/paper-results"
echo "Compare with the paper: python3 $PACKAGE_DIR/analysis/verify_paper.py --results $EXPERIMENT_DIR/paper-results"
exit "$status"
