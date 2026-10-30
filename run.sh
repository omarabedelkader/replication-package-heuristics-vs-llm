#!/usr/bin/env bash
# Regenerate every table and figure of the paper from the benchmark checkpoints,
# then check that they are identical to the paper's.
#
# Usage: ./run.sh [CHECKPOINTS_DIR]
#   CHECKPOINTS_DIR  checkpoints of a re-run (default: the released data/checkpoints)
# Needs only Python 3.8+ (standard library). Outputs go to results/paper/.

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PYTHON="${PYTHON:-python3}"

if [[ "${1:-}" == -h || "${1:-}" == --help ]]; then
    sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
fi
args=()
if [[ $# -ge 1 ]]; then
    args=(--checkpoints "$1")
fi

echo "== Regenerating the paper's tables and figures from the checkpoints"
"$PYTHON" analysis/reproduce_paper.py ${args[@]+"${args[@]}"}

echo
echo "== Checking them against the paper"
status=0
"$PYTHON" analysis/verify_paper.py || status=$?

cat <<'EOF'

== Paper tables and figures (results/paper/)
  Table I    MRR by prefix length                        tab-mrr-by-prefix.tex
  Table II   Names returned by (un)constrained generation tab-vocabulary-constraints.tex
  Table III  Coverage and ranking by prefix length        tab-reranking-coverage.tex
  Figure 3   Mean completion time per observation        fig-quality-and-time.tex
  Supplementary: tab-top-k-accuracy.tex, tab-name-validity-by-prefix.tex,
                 tab-prefix-policies.tex, fig-package-mrr.tex
  (Figures 1 and 2 are method diagrams and contain no results.)
EOF
exit "$status"
