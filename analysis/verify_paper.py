#!/usr/bin/env python3
"""Check that the regenerated results are exactly the ones reported in the paper.

Run after reproduce_paper.py:
    python3 analysis/verify_paper.py [--results DIR]

Three checks:
 1. every generated table/figure equals the paper's supplemental file (comment lines ignored);
 2. every statistic equals the reference analysis-stats.json used to write the paper;
 3. every number quoted in the paper's text is recomputed and compared.
Exit status 0 only if all checks pass.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = ROOT / "expected"
DEP = "heuristicsDependency"
SIZES = ("05B", "15B", "3B", "7B")


def strip_comments(path):
    return [line for line in path.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("%")]


def check_files(results):
    failures = []
    for expected in sorted((EXPECTED / "paper-supplemental").glob("*.tex")):
        generated = results / "paper" / expected.name
        if not generated.exists():
            failures.append(f"missing {generated}")
        elif strip_comments(expected) != strip_comments(generated):
            failures.append(f"{expected.name} differs from the paper (diff expected/paper-supplemental/{expected.name} {generated})")
        else:
            print(f"  ok  {expected.name}")
    return failures


def check_stats(stats):
    reference = json.loads((EXPECTED / "analysis-stats.reference.json").read_text())
    failures = [f"statistic {k}: {stats.get(k)!r} != {v!r}" for k, v in reference.items() if stats.get(k) != v]
    if not failures:
        print(f"  ok  {len(reference)} statistics identical to expected/analysis-stats.reference.json")
    return failures


def claims(st):
    """(section, claim, computed value, value printed in the paper)."""
    x = st["extra"]
    mrr = lambda k, s, p="avg": st[f"mrr/{k}/{s}/{p}"]
    gain = lambda k, s: round(100 * (mrr(k, s) / mrr(k, DEP) - 1), 1)
    sign = lambda k, a, b: st[f"sign/{k}/{a}>{b}"]
    r3 = lambda v: round(v, 3)
    r1 = lambda v: round(v, 1)
    ms = lambda k, s: st[f"ms/{k}/{s}"]
    hyb = lambda k, m: st[f"hyb/{k}/{m}"]
    PREF = list(range(2, 9))
    time_pairs = [(k, s) for k in ("messages", "variables") for s in SIZES]
    lower = [ms(k, f"llm{s}") < ms(k, f"llmUnvalidated{s}") for k, s in time_pairs]
    reductions = [100 * (1 - ms(k, f"llm{s}") / ms(k, f"llmUnvalidated{s}")) for (k, s), ok in zip(time_pairs, lower) if ok]
    neural = [ms(k, f"{f}{s}") for k in ("messages", "variables") for f in ("llmUnvalidated", "llm", "hybrid") for s in SIZES]
    out = [
        ("Abstract", "packages analysed", st["corpus_matched"]["packages"], 47),
        ("Abstract", "constrained 7B MRR gain over Dependency, methods (%)", gain("messages", "llm7B"), 49.7),
        ("Abstract", "constrained 7B MRR gain over Dependency, classes (%)", gain("variables", "llm7B"), 48.4),
        ("Abstract", "7B reranking MRR gain over Dependency, methods (%)", gain("messages", "hybrid7B"), 26.9),
        ("Abstract", "7B reranking MRR gain over Dependency, classes (%)", gain("variables", "hybrid7B"), 37.2),
        ("Abstract", "constraints lower mean time (of 8 comparisons)", sum(lower), 7),
        ("Abstract", "7B reranker beats constrained class MRR at prefixes 5-8",
         all(mrr("variables", "hybrid7B", p) > mrr("variables", "llm7B", p) for p in range(5, 9)), True),
        ("Setup", "eligible packages", x["eligible_packages"], 733),
        ("Setup", "classes in matched packages", st["corpus_matched"]["classes"], 501),
        ("Setup", "traversed methods in matched packages", st["corpus_matched"]["methods"], 4277),
        ("Setup", "method observations", st["obs_matched"]["messages"], 103391),
        ("Setup", "class observations", st["obs_matched"]["variables"], 12678),
        ("Setup", "observations per configuration", x["observations_total"], 116069),
        ("Setup", "packages contributing method observations", x["packages_with_observations"]["messages"], 47),
        ("Setup", "packages contributing class observations", x["packages_with_observations"]["variables"], 37),
        ("Setup", "observation counts match across configurations",
         x["counts_match/messages"] and x["counts_match/variables"], True),
        ("Setup", "package comparisons in the sign-test family", sum(1 for k in st if k.startswith("sign/")), 26),
        ("RQ1", "Baseline MRR, methods", r3(mrr("messages", "heuristicsBaseline")), 0.262),
        ("RQ1", "Dependency MRR, methods", r3(mrr("messages", DEP)), 0.517),
        ("RQ1", "Baseline MRR, classes", r3(mrr("variables", "heuristicsBaseline")), 0.407),
        ("RQ1", "Dependency MRR, classes", r3(mrr("variables", DEP)), 0.592),
        ("RQ1", "every CLM configuration beats both heuristics (pooled MRR)",
         all(mrr(k, f"{f}{s}") > max(mrr(k, DEP), mrr(k, "heuristicsBaseline"))
             for k in ("messages", "variables") for f in ("llmUnvalidated", "llm", "hybrid") for s in SIZES), True),
        ("RQ1", "constrained 7B MRR, methods", r3(mrr("messages", "llm7B")), 0.774),
        ("RQ1", "constrained 7B MRR, classes", r3(mrr("variables", "llm7B")), 0.879),
        ("RQ1", "constrained 7B Top-1, methods (%)", r1(st["top1/messages/llm7B"]), 73.6),
        ("RQ1", "constrained 7B Top-1, classes (%)", r1(st["top1/variables/llm7B"]), 83.3),
        ("RQ1", "Dependency Top-1, methods (%)", r1(x[f"top1_exact/messages/{DEP}"]), 37.4),
        ("RQ1", "Dependency Top-1, classes (%)", r1(x[f"top1_exact/variables/{DEP}"]), 45.4),
        ("RQ1", "constrained 7B > Dependency, method packages (win/loss/tie)",
         tuple(sign("messages", "llm7B", DEP)[f] for f in ("win", "loss", "tie")), (46, 1, 0)),
        ("RQ1", "  ... p < 1e-12", sign("messages", "llm7B", DEP)["p"] < 1e-12, True),
        ("RQ1", "constrained 7B > Dependency, class packages (win/loss/tie)",
         tuple(sign("variables", "llm7B", DEP)[f] for f in ("win", "loss", "tie")), (32, 4, 1)),
        ("RQ1", "  ... p < 1e-5", sign("variables", "llm7B", DEP)["p"] < 1e-5, True),
        ("RQ1", "packages in the scatter plot (methods, classes)",
         (st["per_package_points"]["messages/llm7B"], st["per_package_points"]["variables/llm7B"]), (46, 34)),
        ("RQ2", "constraints improve MRR at every size and task",
         all(mrr(k, f"llm{s}") > mrr(k, f"llmUnvalidated{s}") for k in ("messages", "variables") for s in SIZES), True),
        ("RQ2", "largest within-size constraint gain is at 0.5B (both tasks)",
         all(max(SIZES, key=lambda s: mrr(k, f"llm{s}") - mrr(k, f"llmUnvalidated{s}")) == "05B"
             for k in ("messages", "variables")), True),
        ("RQ2", "unconstrained 7B Top-1, methods (%)", r1(st["top1/messages/llmUnvalidated7B"]), 68.1),
        ("RQ2", "unconstrained 7B Top-1, classes (%)", r1(st["top1/variables/llmUnvalidated7B"]), 73.4),
        ("RQ2", "method packages favouring constraints at 0.5B/3B/7B",
         [sign("messages", f"llm{s}", f"llmUnvalidated{s}")["win"] for s in ("05B", "3B", "7B")], [47, 47, 47]),
        ("RQ2", "method packages at 1.5B (win, tie)",
         (sign("messages", "llm15B", "llmUnvalidated15B")["win"], sign("messages", "llm15B", "llmUnvalidated15B")["tie"]), (46, 1)),
        ("RQ2", "no class package favours unconstrained generation",
         all(sign("variables", f"llm{s}", f"llmUnvalidated{s}")["loss"] == 0 for s in ("05B", "15B", "3B", "7B")), True),
        ("RQ2", "constrained mean list length range, methods",
         (r1(min(st[f"val/messages/{s}/cand_after"] for s in SIZES)), r1(max(st[f"val/messages/{s}/cand_after"] for s in SIZES))), (4.4, 4.5)),
        ("RQ2", "constrained mean list length range, classes",
         (r1(min(st[f"val/variables/{s}/cand_after"] for s in SIZES)), r1(max(st[f"val/variables/{s}/cand_after"] for s in SIZES))), (2.2, 2.8)),
        ("RQ2", "unconstrained 7B membership, methods (%)", r1(st["val/messages/7B/valid_before"]), 22.5),
        ("RQ2", "unconstrained 7B membership, classes (%)", r1(st["val/variables/7B/valid_before"]), 15.8),
        ("RQ3", "reranking improves Dependency MRR at every size",
         all(mrr(k, f"hybrid{s}") > mrr(k, DEP) for k in ("messages", "variables") for s in SIZES), True),
        ("RQ3", "7B reranking MRR, methods", r3(mrr("messages", "hybrid7B")), 0.656),
        ("RQ3", "7B reranking MRR, classes", r3(mrr("variables", "hybrid7B")), 0.813),
        ("RQ3", "7B reranking > Dependency, method packages", sign("messages", "hybrid7B", DEP)["win"], 47),
        ("RQ3", "7B reranking > Dependency, class packages (win, of)",
         (sign("variables", "hybrid7B", DEP)["win"], 37), (34, 37)),
        ("RQ3", "  ... class p < 1e-6", sign("variables", "hybrid7B", DEP)["p"] < 1e-6, True),
        ("RQ3", "Recall@10 of reranking = Dependency, methods (%)", r1(st["top10/messages/hybrid7B"]), 81.1),
        ("RQ3", "Recall@10 of reranking = Dependency, classes (%)", r1(st["top10/variables/hybrid7B"]), 84.8),
        ("RQ3", "reranking never changes Recall@10 (package x prefix cells violating)", st["hybrid_invariant"]["violations"], 0),
        ("RQ3", "conditional Top-1, 7B reranker, methods (%)", r1(x["cond_top1_pooled/messages/hybrid7B"]), 70.7),
        ("RQ3", "conditional Top-1, 7B reranker, classes (%)", r1(x["cond_top1_pooled/variables/hybrid7B"]), 92.6),
        ("RQ3", "conditional Top-1, Dependency, methods (%)", r1(x[f"cond_top1_pooled/messages/{DEP}"]), 46.1),
        ("RQ3", "conditional Top-1, Dependency, classes (%)", r1(x[f"cond_top1_pooled/variables/{DEP}"]), 53.6),
        ("RQ3", "Dependency coverage at prefix 2 (methods, classes)",
         (hyb("messages", "Cov (Dep)")[0], hyb("variables", "Cov (Dep)")[0]), (57.9, 53.4)),
        ("RQ3", "constrained 7B Top-1 at prefix 2 (methods, classes)",
         (hyb("messages", "T1 LM")[0], hyb("variables", "T1 LM")[0]), (67.7, 74.7)),
        ("RQ3", "class prefixes where 7B reranker Top-1 > constrained 7B",
         [p for i, p in enumerate(PREF) if hyb("variables", "T1 Hyb")[i] > hyb("variables", "T1 LM")[i]], [4, 5, 6, 7, 8]),
        ("RQ3", "class prefixes where 7B reranker MRR > constrained 7B",
         [p for p in PREF if mrr("variables", "hybrid7B", p) > mrr("variables", "llm7B", p)], [5, 6, 7, 8]),
        ("RQ3", "class MRR at prefix 8 (reranking, constrained)",
         (r3(mrr("variables", "hybrid7B", 8)), r3(mrr("variables", "llm7B", 8))), (0.923, 0.912)),
        ("RQ3", "method prefixes where 7B reranker MRR > constrained 7B",
         [p for p in PREF if mrr("messages", "hybrid7B", p) > mrr("messages", "llm7B", p)], []),
        ("RQ3", "method MRR at prefix 8, 3B (reranking, constrained)",
         (r3(mrr("messages", "hybrid3B", 8)), r3(mrr("messages", "llm3B", 8))), (0.851, 0.846)),
        ("RQ3", "pooled 3B method MRR favours constrained generation", mrr("messages", "llm3B") > mrr("messages", "hybrid3B"), True),
        ("RQ3", "method coverage at prefix 8 (Dependency, constrained 7B)",
         (hyb("messages", "Cov (Dep)")[6], hyb("messages", "Cov (LM)")[6]), (96.7, 89.7)),
        ("RQ3", "method MRR at prefix 8 (Dependency, constrained 7B)",
         (r3(mrr("messages", DEP, 8)), r3(mrr("messages", "llm7B", 8))), (0.765, 0.867)),
        ("RQ3", "constrained > reranking pooled MRR at every size",
         all(mrr(k, f"llm{s}") > mrr(k, f"hybrid{s}") for k in ("messages", "variables") for s in SIZES), True),
        ("RQ3", "method packages favouring constrained 7B over 7B reranking", sign("messages", "llm7B", "hybrid7B")["win"], 36),
        ("RQ3", "class packages: favour constrained 7B, favour 7B reranking",
         (sign("variables", "llm7B", "hybrid7B")["win"], sign("variables", "llm7B", "hybrid7B")["loss"]), (19, 18)),
        ("RQ3", "  ... p = 1.0", sign("variables", "llm7B", "hybrid7B")["p"], 1.0),
        ("RQ4", "pooled MRR increases with size within each CLM strategy",
         all(mrr(k, f"{f}{a}") < mrr(k, f"{f}{b}") for k in ("messages", "variables")
             for f in ("llmUnvalidated", "llm", "hybrid") for a, b in zip(SIZES, SIZES[1:])), True),
        ("RQ4", "largest adjacent-size gain is 0.5B -> 1.5B",
         all(max(zip(SIZES, SIZES[1:]), key=lambda ab: mrr(k, f"{f}{ab[1]}") - mrr(k, f"{f}{ab[0]}"))[0] == "05B"
             for k in ("messages", "variables") for f in ("llmUnvalidated", "llm", "hybrid")), True),
        ("RQ4", "constrained 1.5B > 0.5B, method packages", sign("messages", "llm15B", "llm05B")["win"], 42),
        ("RQ4", "constrained 1.5B MRR (methods, classes)", (r3(mrr("messages", "llm15B")), r3(mrr("variables", "llm15B"))), (0.729, 0.846)),
        ("RQ4", "constrained 7B vs 1.5B, method packages (win/loss/tie)",
         tuple(sign("messages", "llm7B", "llm15B")[f] for f in ("win", "loss", "tie")), (39, 2, 6)),
        ("RQ4", "constrained 0.5B > Dependency (method packages, class packages)",
         (sign("messages", "llm05B", DEP)["win"], sign("variables", "llm05B", DEP)["win"]), (43, 25)),
        ("RQ4", "  ... class p (2 decimals)", round(sign("variables", "llm05B", DEP)["p"], 2), 0.03),
        ("RQ4", "  ... class p above the Bonferroni threshold 0.05/26", sign("variables", "llm05B", DEP)["p"] > 0.05 / 26, True),
        ("RQ4", "neural mean time range (s)", (round(min(neural) / 1000, 2), round(max(neural) / 1000, 2)), (0.76, 5.23)),
        ("RQ4", "heuristic mean time, methods (Baseline, Dependency ms)",
         (round(ms("messages", "heuristicsBaseline")), round(ms("messages", DEP))), (105, 160)),
        ("RQ4", "heuristic mean time, classes (Baseline, Dependency ms)",
         (round(ms("variables", "heuristicsBaseline")), round(ms("variables", DEP))), (11, 26)),
        ("RQ4", "time reductions from constraints (min, max %)", (round(min(reductions)), round(max(reductions))), (13, 60)),
        ("RQ4", "exception: 1.5B class time (unconstrained, constrained ms)",
         (round(ms("variables", "llmUnvalidated15B")), round(ms("variables", "llm15B"))), (759, 999)),
        ("RQ4", "constrained method time (0.5B, 1.5B ms)", (round(ms("messages", "llm05B")), round(ms("messages", "llm15B"))), (3354, 835)),
        ("RQ4", "7B reranking time (methods, classes ms)", (round(ms("messages", "hybrid7B")), round(ms("variables", "hybrid7B"))), (2168, 2318)),
        ("RQ4", "constrained 7B time (methods, classes ms)", (round(ms("messages", "llm7B")), round(ms("variables", "llm7B"))), (2074, 1956)),
        ("RQ4", "exact constrained 3B method mean (ms, label 1,699)", round(x["ms_exact/messages/llm3B"], 2), 1698.52),
        ("Synthesis", "class 1.5B MRR gain from constraints",
         round(mrr("variables", "llm15B") - mrr("variables", "llmUnvalidated15B"), 3), 0.100),
        ("Synthesis", "class MRR gain from scaling constrained 1.5B -> 7B",
         round(mrr("variables", "llm7B") - mrr("variables", "llm15B"), 3), 0.033),
    ]
    return out


def normalise(value):
    return list(value) if isinstance(value, tuple) else value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", default=str(ROOT / "results"))
    parser.add_argument("--report", default=None, help="Markdown report path (default: RESULTS/verification-report.md)")
    args = parser.parse_args(argv)
    results = Path(args.results)
    st = json.loads((results / "analysis-stats.json").read_text())

    print("1. Tables and figures")
    failures = check_files(results)
    print("2. Statistics")
    failures += check_stats(st)
    print("3. Numbers quoted in the paper text")
    report = ["# Paper claims recomputed from the checkpoints", "",
              "| Section | Claim | Recomputed | Paper | |", "|---|---|---|---|---|"]
    passed, checked = 0, claims(st)
    for section, claim, computed, paper in checked:
        ok = normalise(computed) == normalise(paper)
        passed += ok
        report.append(f"| {section} | {claim} | {computed} | {paper} | {'ok' if ok else 'MISMATCH'} |")
        if not ok:
            failures.append(f"{section}: {claim}: recomputed {computed}, paper {paper}")
    print(f"  {passed} of {len(checked)} claims match")
    report_path = Path(args.report) if args.report else results / "verification-report.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"  report: {report_path}")
    if failures:
        print("\nFAILED:")
        for failure in failures:
            print("  - " + failure)
        return 1
    print("\nAll checks passed: the checkpoints reproduce every result reported in the paper.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
