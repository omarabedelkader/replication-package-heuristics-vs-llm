#!/usr/bin/env bash
# Quick check of a prepared experiment, without GPU or models: re-run the deterministic
# heuristic benchmarks (Baseline, Dependency; methods and classes) of one package with the
# original worker script, and compare their counts, hits and reciprocal-rank sums with the
# released checkpoints. Times and memory are machine-dependent and not compared.
#
# Usage: rerun/smoke-test.sh EXPERIMENT_DIR [PACKAGE]   (default package: Network-Mail)

set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -lt 1 || "$1" == -h || "$1" == --help ]]; then
    sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
    exit $(( $# < 1 ))
fi
EXPERIMENT_DIR="$(cd "$1" && pwd -P)"
PACKAGE="${2:-Network-Mail}"
PYTHON="${PIPELINE_PYTHON:-python3}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/smoke.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

index="$("$PYTHON" -c 'import json, sys
print(json.load(open(sys.argv[1]))["packages"].index(sys.argv[2]) + 1)' \
    "$PACKAGE_DIR/data/provenance/workers.json" "$PACKAGE")"
reference="$PACKAGE_DIR/data/checkpoints/$(printf '%04d' "$index")/benchmarks"
run_id="$("$PYTHON" -c 'import json, sys; print(json.load(open(sys.argv[1]))["runId"])' "$PACKAGE_DIR/data/provenance/workers.json")"

failed=0
for kind in messages variables; do
    for strategy in heuristicsBaseline heuristicsDependency; do
        output="$WORK/$kind-$strategy.json"
        (cd "$EXPERIMENT_DIR/image" && BENCHMARK_PACKAGE="$PACKAGE" BENCHMARK_KIND="$kind" \
            BENCHMARK_STRATEGY="$strategy" BENCHMARK_RUN_ID="$run_id" BENCHMARK_OUTPUT="$output" \
            BENCHMARK_RUN_SELECTION="$PACKAGE_DIR/data/provenance/selection.json" \
            ./pharo --headless Pharo.image --no-default-preferences eval \
            "$(cat "$PACKAGE_DIR/pipeline/scripts/benchmark-package.st")" > "$WORK/log" 2>&1) || {
            cat "$WORK/log" >&2; exit 1; }
        "$PYTHON" - "$output" "$reference/$kind-$strategy/part.json" "$PACKAGE $kind $strategy" <<'EOF' || failed=1
import json, sys
new, old = (json.load(open(path)) for path in sys.argv[1:3])
fields = ("count", "top1", "top2", "top3", "top10")
rows = lambda part: {r["prefix"]: r for r in part["rows"]}
same = new["corpus"] == old["corpus"] and all(
    all(rows(new)[p][f] == rows(old)[p][f] for f in fields)
    and abs(rows(new)[p]["reciprocalRankSum"] - rows(old)[p]["reciprocalRankSum"]) < 1e-6
    for p in range(2, 9))
print(("  ok  " if same else "  DIFFERENT  ") + sys.argv[3]
      + f"  ({sum(r['count'] for r in new['rows'])} observations)")
sys.exit(0 if same else 1)
EOF
    done
done
if [[ "$failed" != 0 ]]; then
    echo "Smoke test FAILED: the heuristic results differ from the released checkpoints." >&2
    exit 1
fi
echo "Smoke test passed: the heuristic benchmarks reproduce the released checkpoints exactly."
