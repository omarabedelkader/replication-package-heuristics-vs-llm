#!/usr/bin/env bash
# Create an experiment directory that holds exactly the inputs of the paper's run:
# the frozen Pharo image (checked against its pinned SHA-256), the frozen benchmark
# source and the model list; the image is checked against the saved package selection.
# Only the Pharo VM is downloaded, for the current platform (it is not a pinned input).
#
# Usage: rerun/setup-frozen-experiment.sh EXPERIMENT_DIR
#   PHARO_VM_URL  zeroconf script that installs the VM (default https://get.pharo.org/64/vm140)

set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 1 || "$1" == -h || "$1" == --help ]]; then
    sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
    exit $(( $# != 1 ))
fi
EXPERIMENT_DIR="$1"
if [[ -e "$EXPERIMENT_DIR" && -n "$(ls -A "$EXPERIMENT_DIR" 2>/dev/null)" ]]; then
    echo "$EXPERIMENT_DIR exists and is not empty; choose a new directory." >&2
    exit 1
fi
mkdir -p "$EXPERIMENT_DIR/image"
EXPERIMENT_DIR="$(cd "$EXPERIMENT_DIR" && pwd -P)"
PYTHON="${PIPELINE_PYTHON:-python3}"

echo "Extracting the frozen Pharo image"
tar -xzf "$PACKAGE_DIR/frozen-image/pharo14-frozen-image.tar.gz" -C "$EXPERIMENT_DIR/image"

echo "Installing the Pharo 14 VM for $(uname -s)/$(uname -m)"
(cd "$EXPERIMENT_DIR/image" && curl -fsSL "${PHARO_VM_URL:-https://get.pharo.org/64/vm140}" | bash > /dev/null)
if [[ ! -x "$EXPERIMENT_DIR/image/pharo" ]]; then
    echo "The VM installation did not create image/pharo" >&2
    exit 1
fi

cp -R "$PACKAGE_DIR/lib/HeuristicCompletion-Benchmarks-Multiples" "$EXPERIMENT_DIR/repository"
# No benchmark-selection.json: the pipeline saves the experiment's selection from the package
# list of the run (rerun/run-benchmarks.sh: the 47 analysed packages by default).
cp "$PACKAGE_DIR"/data/experiment/{image-source.json,llm-models.json} "$EXPERIMENT_DIR/"

# Exit 0: the image is the pinned one and it holds the frozen source.
"$PYTHON" "$PACKAGE_DIR/pipeline/scripts/benchmark_source.py" check-image \
    --repository "$EXPERIMENT_DIR/repository" \
    --image "$EXPERIMENT_DIR/image/Pharo.image" --pin "$EXPERIMENT_DIR/image-source.json"
echo "Image and source match the pinned SHA-256 of the paper's run."

# The image must see the same 733 eligible packages as the saved selection.
(cd "$EXPERIMENT_DIR/image" && BENCHMARK_SELECTION_FILE="$PACKAGE_DIR/data/experiment/benchmark-selection.json" \
    ./pharo --headless Pharo.image eval "
| split |
split := CooBenchmarkSplit readFrom: (OSEnvironment current at: 'BENCHMARK_SELECTION_FILE') asFileReference.
split validateAgainst: CooBenchRunner eligiblePackageNames.
'Selection valid: ', split benchmarkPackageNames size printString, ' benchmark packages of ',
    CooBenchRunner eligiblePackageNames size printString, ' eligible'")
echo "Experiment ready: $EXPERIMENT_DIR"
echo "Next: rerun/run-benchmarks.sh $EXPERIMENT_DIR"
