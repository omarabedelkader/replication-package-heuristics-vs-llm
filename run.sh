#!/usr/bin/env bash
# The single entry point of the replication package.
#
#   ./run.sh           Regenerate every table and figure of the paper from the released
#                      checkpoints (results/paper/) and check them against the paper.
#                      Needs bash and Python 3.8+ (Linux or macOS; on Windows, use WSL); takes seconds.
#
#   ./run.sh --rerun   Re-run all 1,034 benchmarks of the 47 packages from scratch (frozen
#                      Pharo image, benchmark source in lib/, the three models through Ollama),
#                      then regenerate the tables from the new checkpoints and check them
#                      (completion times depend on the hardware, so those checks will differ).
#                      Needs curl, Ollama >= 0.12.11 (0.40.5, as in the paper, is downloaded on Linux), a GPU and ~25 GB
#                      for the models; takes days. Optional settings:
#                        EXPERIMENT_DIR        working directory (default: experiment)
#                        BENCHMARK_JOBS        simultaneous benchmarks (default 8, as in the paper)
#                        BENCHMARK_RESUME_DIR  continue an interrupted EXPERIMENT_DIR/benchmark-run.*
#                        BENCHMARK_PACKAGES_FILE  run only the packages listed in this file (one
#                                              per line), e.g. one small package to test the setup
#                        OLLAMA_BIN, OLLAMA_MODELS_DIR  see pipeline/pipeline-benchmarks.sh --help
#                      With less GPU memory: BENCHMARK_JOBS=2 OLLAMA_MAX_LOADED_MODELS=1.

set -euo pipefail
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PACKAGE_DIR"
PYTHON="${PIPELINE_PYTHON:-python3}"
# The packages of --rerun: the paper's 47, or your own list (a path relative to where you call run.sh).
if [[ -n "${BENCHMARK_PACKAGES_FILE:-}" ]]; then
    BENCHMARK_PACKAGES_FILE="$(cd "$OLDPWD" 2>/dev/null; cd "$(dirname "$BENCHMARK_PACKAGES_FILE")" && pwd -P)/$(basename "$BENCHMARK_PACKAGES_FILE")"
fi
export BENCHMARK_PACKAGES_FILE="${BENCHMARK_PACKAGES_FILE:-$PACKAGE_DIR/data/experiment/analysed-packages.txt}"

tables() {
    # $1: checkpoints directory, $2: a re-run's workers.json (empty for the released
    # checkpoints, whose packages are data/experiment/analysed-packages.txt), $3: output directory
    echo "== Regenerating the paper's tables and figures from the checkpoints"
    "$PYTHON" analysis/reproduce_paper.py --checkpoints "$1" ${2:+--workers "$2"} --out "$3"
    echo
    echo "== Checking them against the paper"
    local status=0
    "$PYTHON" analysis/verify_paper.py --results "$3" || status=$?
    cat <<EOF

== Paper tables and figures ($3/paper/)
  Table I    MRR by prefix length                         tab-mrr-by-prefix.tex
  Table II   Names returned by (un)constrained generation tab-vocabulary-constraints.tex
  Table III  Coverage and ranking by prefix length        tab-reranking-coverage.tex
  Figure 3   Mean completion time per observation         fig-quality-and-time.tex
  Figure 4   MRR against completion time                  fig-summary.tex
  Supplementary: tab-top-k-accuracy.tex, tab-name-validity-by-prefix.tex,
                 tab-prefix-policies.tex, fig-package-mrr.tex
  (Figures 1 and 2 are method diagrams and contain no results.)
EOF
    return "$status"
}

prepare_experiment() {
    # The frozen image (checked against its pinned SHA-256), the benchmark source of lib/
    # and the model list. Only the Pharo VM is downloaded, for the current platform.
    local dir="$1"
    if [[ -f "$dir/image-source.json" && -d "$dir/repository" ]]; then
        return 0
    fi
    if [[ -e "$dir" && -n "$(ls -A "$dir" 2>/dev/null)" ]]; then
        echo "$dir exists and is not an experiment prepared by ./run.sh --rerun; choose another EXPERIMENT_DIR." >&2
        exit 1
    fi
    mkdir -p "$dir/image"
    echo "== Extracting the frozen Pharo image"
    tar -xzf frozen-image/pharo14-frozen-image.tar.gz -C "$dir/image"
    echo "== Installing the Pharo 14 VM for $(uname -s)/$(uname -m)"
    (cd "$dir/image" && curl -fsSL "${PHARO_VM_URL:-https://get.pharo.org/64/vm140}" | bash > /dev/null)
    [[ -x "$dir/image/pharo" ]] || { echo "The VM installation did not create $dir/image/pharo" >&2; exit 1; }
    cp -R lib/HeuristicCompletion-Benchmarks-Multiples "$dir/repository"
    cp data/experiment/image-source.json data/experiment/llm-models.json "$dir/"
    # 0: image and lib/ are exactly the run's; 5: the image is the run's, but lib/ differs
    # from the source it holds (only in code for models the paper does not use), so the
    # pipeline loads lib/ into the image before the first benchmark.
    local status=0
    "$PYTHON" pipeline/scripts/benchmark_source.py check-image \
        --repository "$dir/repository" --image "$dir/image/Pharo.image" --pin "$dir/image-source.json" || status=$?
    case "$status" in
        0) echo "Image and source match the pinned SHA-256 of the paper's run." ;;
        5) echo "Image matches the pinned SHA-256 of the paper's run; lib/ will be loaded into it." ;;
        *) exit "$status" ;;
    esac
    (cd "$dir/image" && ./pharo --headless Pharo.image eval "
| names missing |
names := ((OSEnvironment current at: 'BENCHMARK_PACKAGES_FILE') asFileReference contents lines
    collect: [ :each | (each copyUpTo: \$#) trim ]) reject: [ :each | each isEmpty ].
missing := names reject: [ :each | CooBenchRunner eligiblePackageNames includes: each ].
missing ifNotEmpty: [ Error signal: 'Packages missing from the image: ', (', ' join: missing) ].
names size printString, ' packages found in the image'")
}

rerun() {
    mkdir -p "${EXPERIMENT_DIR:=experiment}"
    export EXPERIMENT_DIR="$(cd "$EXPERIMENT_DIR" && pwd -P)"
    prepare_experiment "$EXPERIMENT_DIR"
    export BENCHMARK_REPO_DIR="$PACKAGE_DIR/lib/HeuristicCompletion-Benchmarks-Multiples"
    export RESULTS_DIR="${RESULTS_DIR:-$EXPERIMENT_DIR/results}"
    export BENCHMARK_JOBS="${BENCHMARK_JOBS:-8}"
    # Ollama server settings of the paper's run. Every request sets num_ctx = 8,192 and
    # keep_alive = 5m itself (CooLLMClient), which override OLLAMA_CONTEXT_LENGTH and
    # OLLAMA_KEEP_ALIVE for the benchmark requests.
    export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-$BENCHMARK_JOBS}"
    export OLLAMA_MAX_LOADED_MODELS="${OLLAMA_MAX_LOADED_MODELS:-4}"
    export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:--1}"
    export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-4096}"

    echo "== Running the benchmarks of $(grep -cvE '^[[:space:]]*(#|$)' "$BENCHMARK_PACKAGES_FILE") packages (after an interruption, continue with the"
    echo "   BENCHMARK_RESUME_DIR the pipeline prints: completed benchmarks are kept)"
    local status=0
    bash pipeline/pipeline-benchmarks.sh --foreground || status=$?

    # Analyse what is complete, even after an interruption (unfinished packages are skipped):
    # the resumed run, or else the run directory this call created (the most recent one).
    local run="${BENCHMARK_RESUME_DIR:-$(ls -dt "$EXPERIMENT_DIR"/benchmark-run.* 2>/dev/null | head -n 1)}"
    if [[ -z "$run" ]]; then
        echo "No benchmark run directory in $EXPERIMENT_DIR: nothing to analyse." >&2
        return 1
    fi
    tables "$run/packages" "$run/workers.json" "$EXPERIMENT_DIR/paper-results" || status=$?
    return "$status"
}

case "${1:-}" in
    "")
        tables data/checkpoints "" results ;;
    --rerun)
        rerun ;;
    -h|--help)
        sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//' ;;
    *)
        echo "Unknown option: $1 (see ./run.sh --help)" >&2
        exit 2 ;;
esac
