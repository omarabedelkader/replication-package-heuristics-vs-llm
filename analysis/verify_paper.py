#!/usr/bin/env python3
"""Check that the regenerated results are exactly the ones reported in the paper.

Run after reproduce_paper.py:
    python3 analysis/verify_paper.py [--results DIR]

Three checks:
 1. every generated table/figure equals the paper's supplemental file (comment lines ignored);
 2. every statistic equals the reference analysis-stats.json used to write the paper;
 3. every number and comparison stated in the paper's text is recomputed and compared.
Exit status 0 only if all checks pass.
"""
import argparse
import json
import math
import re
import sys
import tarfile
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
    """(section, claim, computed value, value printed in the paper), in the order of the paper's text.
    Values are recomputed from unrounded aggregates and rounded as printed."""
    x = st["extra"]
    E = lambda k, s, p="avg": x["exact"][f"{k}/{s}/{p}"]
    mrr = lambda k, s, p="avg": E(k, s, p)["mrr"]
    top1 = lambda k, s, p="avg": E(k, s, p)["top1"]
    rec = lambda k, s, p="avg": E(k, s, p)["top10"]
    ms = lambda k, s: E(k, s)["ms"]
    gain = lambda k, s: round(100 * (mrr(k, s) / mrr(k, DEP) - 1), 1)
    r3 = lambda v: round(v, 3)
    r1 = lambda v: round(v, 1)
    msr = lambda v: int(math.floor(v + 0.5))
    K = ("messages", "variables")
    FAM = ("llmUnvalidated", "llm", "hybrid")
    PREF = range(2, 9)
    both = lambda f: tuple(f(k) for k in K)
    neural = [ms(k, f"{f}{s}") for k in K for f in FAM for s in SIZES]
    strategies = {key.split("/")[2] for key in st if key.startswith("mrr/")}
    pairs = [(k, s) for k in K for s in SIZES]
    faster = [(k, s) for k, s in pairs if ms(k, f"llm{s}") < ms(k, f"llmUnvalidated{s}")]
    return [
        ("Abstract", "packages", st["corpus_matched"]["packages"], 47),
        ("Abstract", "more than 100K completions", x["observations_total"] > 100000, True),
        ("Abstract", "constrained (7B) MRR gain over Dependency, methods / classes (%)",
         both(lambda k: gain(k, "llm7B")), (49.7, 48.4)),
        ("Introduction", "experimental configurations (2 + 3 x 4)", len(strategies), 14),
        ("IV-A Corpus", "packages", st["corpus_matched"]["packages"], 47),
        ("IV-A Corpus", "classes", st["corpus_matched"]["classes"], 501),
        ("IV-A Corpus", "methods", st["corpus_matched"]["methods"], 4277),
        ("IV-A Corpus", "method-selector observations", st["obs_matched"]["messages"], 103391),
        ("IV-A Corpus", "class-name observations", st["obs_matched"]["variables"], 12678),
        ("IV-A Corpus", "observations per approach", x["observations_total"], 116069),
        ("IV-A Corpus", "same observations for every configuration",
         x["counts_match/messages"] and x["counts_match/variables"], True),
        ("IV-B Completion time", "constrained 3B, methods: total ms",
         int(E("messages", "llm3B")["timeMs"]), 175612087),
        ("IV-B Completion time", "constrained 3B, methods: observations", int(E("messages", "llm3B")["count"]), 103391),
        ("IV-B Completion time", "constrained 3B, methods: mean ms", r1(ms("messages", "llm3B")), 1698.5),
        ("RQ1", "Baseline -> Dependency MRR, methods", (r3(mrr("messages", "heuristicsBaseline")), r3(mrr("messages", DEP))), (0.262, 0.517)),
        ("RQ1", "Baseline -> Dependency MRR, classes", (r3(mrr("variables", "heuristicsBaseline")), r3(mrr("variables", DEP))), (0.407, 0.592)),
        ("RQ1", "every CLM configuration has higher MRR than Dependency",
         all(mrr(k, f"{f}{s}") > mrr(k, DEP) for k in K for f in FAM for s in SIZES), True),
        ("RQ1", "unconstrained 0.5B MRR, methods / classes", both(lambda k: r3(mrr(k, "llmUnvalidated05B"))), (0.593, 0.658)),
        ("RQ1", "constrained 7B MRR, methods / classes", both(lambda k: r3(mrr(k, "llm7B"))), (0.774, 0.879)),
        ("RQ1", "constrained 7B gain over Dependency, methods / classes (%)", both(lambda k: gain(k, "llm7B")), (49.7, 48.4)),
        ("RQ1", "constrained 7B has the highest MRR of all configurations (both tasks)",
         all(max(strategies, key=lambda s: mrr(k, s)) == "llm7B" for k in K), True),
        ("RQ2", "constraints improve MRR at every size, both tasks",
         all(mrr(k, f"llm{s}") > mrr(k, f"llmUnvalidated{s}") for k, s in pairs), True),
        ("RQ2", "0.5B unconstrained -> constrained MRR, methods",
         (r3(mrr("messages", "llmUnvalidated05B")), r3(mrr("messages", "llm05B"))), (0.593, 0.675)),
        ("RQ2", "0.5B unconstrained -> constrained MRR, classes",
         (r3(mrr("variables", "llmUnvalidated05B")), r3(mrr("variables", "llm05B"))), (0.658, 0.786)),
        ("RQ2", "7B unconstrained -> constrained MRR, methods",
         (r3(mrr("messages", "llmUnvalidated7B")), r3(mrr("messages", "llm7B"))), (0.722, 0.774)),
        ("RQ2", "7B unconstrained -> constrained MRR, classes",
         (r3(mrr("variables", "llmUnvalidated7B")), r3(mrr("variables", "llm7B"))), (0.791, 0.879)),
        ("RQ2", "7B unconstrained -> constrained Top-1, methods (%)",
         (r1(top1("messages", "llmUnvalidated7B")), r1(top1("messages", "llm7B"))), (68.1, 73.6)),
        ("RQ2", "7B unconstrained -> constrained Top-1, classes (%)",
         (r1(top1("variables", "llmUnvalidated7B")), r1(top1("variables", "llm7B"))), (73.4, 83.3)),
        ("RQ2", "unconstrained 7B names in the runtime, methods / classes (%)",
         both(lambda k: r1(st[f"val/{k}/7B/valid_before"])), (22.5, 15.8)),
        ("RQ2", "all constrained names in the runtime (%)",
         min(st[f"val/{k}/{s}/valid_after"] for k, s in pairs), 100.0),
        ("RQ2", "unconstrained mean list length, close to ten",
         round(min(st[f"val/{k}/{s}/cand_before"] for k, s in pairs)), 10),
        ("RQ2", "constrained mean list length range, methods",
         (r1(min(st[f"val/messages/{s}/cand_after"] for s in SIZES)), r1(max(st[f"val/messages/{s}/cand_after"] for s in SIZES))), (4.4, 4.5)),
        ("RQ2", "constrained mean list length range, classes",
         (r1(min(st[f"val/variables/{s}/cand_after"] for s in SIZES)), r1(max(st[f"val/variables/{s}/cand_after"] for s in SIZES))), (2.2, 2.8)),
        ("RQ3", "reranking improves Dependency MRR at every size, both tasks",
         all(mrr(k, f"hybrid{s}") > mrr(k, DEP) for k, s in pairs), True),
        ("RQ3", "Dependency -> 7B reranking MRR, methods", (r3(mrr("messages", DEP)), r3(mrr("messages", "hybrid7B"))), (0.517, 0.656)),
        ("RQ3", "Dependency -> 7B reranking MRR, classes", (r3(mrr("variables", DEP)), r3(mrr("variables", "hybrid7B"))), (0.592, 0.813)),
        ("RQ3", "Recall@10 of Dependency = of reranking (every size), methods / classes (%)",
         both(lambda k: r1(rec(k, DEP)) if all(rec(k, f"hybrid{s}") == rec(k, DEP) for s in SIZES) else None), (81.1, 84.8)),
        ("RQ3", "reranking never changes Recall@10 (package x prefix cells violating)", st["hybrid_invariant"]["violations"], 0),
        ("RQ3", "conditional Top-1, 7B reranker, methods / classes (%)",
         both(lambda k: r1(x[f"cond_top1_pooled/{k}/hybrid7B"])), (70.7, 92.6)),
        ("RQ3", "conditional Top-1, Dependency, methods / classes (%)",
         both(lambda k: r1(x[f"cond_top1_pooled/{k}/{DEP}"])), (46.1, 53.6)),
        ("RQ3", "Dependency Recall@10 at prefix 2, methods / classes (%)", both(lambda k: r1(rec(k, DEP, 2))), (57.9, 53.4)),
        ("RQ3", "constrained 7B Top-1 at prefix 2, methods / classes (%)", both(lambda k: r1(top1(k, "llm7B", 2))), (67.7, 74.7)),
        ("RQ3", "class prefixes where 7B reranker Top-1 > constrained 7B",
         [p for p in PREF if top1("variables", "hybrid7B", p) > top1("variables", "llm7B", p)], [4, 5, 6, 7, 8]),
        ("RQ3", "class prefixes where 7B reranker MRR > constrained 7B",
         [p for p in PREF if mrr("variables", "hybrid7B", p) > mrr("variables", "llm7B", p)], [5, 6, 7, 8]),
        ("RQ3", "class MRR at prefix 8, 7B reranking / constrained 7B",
         (r3(mrr("variables", "hybrid7B", 8)), r3(mrr("variables", "llm7B", 8))), (0.923, 0.912)),
        ("RQ3", "Dependency Recall@10 at class prefix 8 (%)", r1(rec("variables", DEP, 8)), 95.1),
        ("RQ3", "method prefixes where constrained 7B MRR > 7B reranker",
         [p for p in PREF if mrr("messages", "llm7B", p) > mrr("messages", "hybrid7B", p)], list(PREF)),
        ("RQ3", "Recall@10 at method prefix 8, Dependency / constrained 7B (%)",
         (r1(rec("messages", DEP, 8)), r1(rec("messages", "llm7B", 8))), (96.7, 89.7)),
        ("RQ3", "method MRR at prefix 8, 7B reranking / constrained 7B",
         (r3(mrr("messages", "hybrid7B", 8)), r3(mrr("messages", "llm7B", 8))), (0.863, 0.867)),
        ("RQ3", "constrained > reranking MRR at every size, both tasks",
         all(mrr(k, f"llm{s}") > mrr(k, f"hybrid{s}") for k, s in pairs), True),
        ("RQ4", "MRR increases with size for each CLM approach, both tasks",
         all(mrr(k, f"{f}{a}") < mrr(k, f"{f}{b}") for k in K for f in FAM for a, b in zip(SIZES, SIZES[1:])), True),
        ("RQ4", "largest adjacent-size gain is 0.5B -> 1.5B (every approach and task)",
         all(max(zip(SIZES, SIZES[1:]), key=lambda ab: mrr(k, f"{f}{ab[1]}") - mrr(k, f"{f}{ab[0]}"))[0] == "05B"
             for k in K for f in FAM), True),
        ("RQ4", "constrained 0.5B -> 1.5B MRR, methods", (r3(mrr("messages", "llm05B")), r3(mrr("messages", "llm15B"))), (0.675, 0.729)),
        ("RQ4", "constrained 0.5B -> 1.5B MRR, classes", (r3(mrr("variables", "llm05B")), r3(mrr("variables", "llm15B"))), (0.786, 0.846)),
        ("RQ4", "constrained 7B MRR, methods / classes", both(lambda k: r3(mrr(k, "llm7B"))), (0.774, 0.879)),
        ("RQ4", "constrained 0.5B MRR > Dependency, both tasks", all(mrr(k, "llm05B") > mrr(k, DEP) for k in K), True),
        ("RQ4", "CLM mean time range (ms)", (msr(min(neural)), msr(max(neural))), (759, 5230)),
        ("RQ4", "Baseline / Dependency mean time, methods (ms)",
         (msr(ms("messages", "heuristicsBaseline")), msr(ms("messages", DEP))), (105, 160)),
        ("RQ4", "Baseline / Dependency mean time, classes (ms)",
         (msr(ms("variables", "heuristicsBaseline")), msr(ms("variables", DEP))), (11, 26)),
        ("RQ4", "constraints faster (of 8 size x task combinations)", len(faster), 7),
        ("RQ4", "7B unconstrained -> constrained time, methods (ms)",
         (msr(ms("messages", "llmUnvalidated7B")), msr(ms("messages", "llm7B"))), (3947, 2074)),
        ("RQ4", "7B unconstrained -> constrained time, classes (ms)",
         (msr(ms("variables", "llmUnvalidated7B")), msr(ms("variables", "llm7B"))), (3802, 1956)),
        ("RQ4", "the exception is 1.5B classes", [(k, s) for k, s in pairs if (k, s) not in faster], [("variables", "15B")]),
        ("RQ4", "1.5B class time, constrained / unconstrained (ms)",
         (msr(ms("variables", "llm15B")), msr(ms("variables", "llmUnvalidated15B"))), (999, 759)),
        ("RQ4", "constrained method time, 0.5B / 1.5B (ms)", (msr(ms("messages", "llm05B")), msr(ms("messages", "llm15B"))), (3354, 835)),
        ("RQ4", "7B reranking time, methods / classes (ms)", both(lambda k: msr(ms(k, "hybrid7B"))), (2168, 2318)),
        ("RQ4", "constrained 7B time, methods / classes (ms)", both(lambda k: msr(ms(k, "llm7B"))), (2074, 1956)),
        ("VI Discussion", "constraints improve Top-1 at every size, both tasks",
         all(top1(k, f"llm{s}") > top1(k, f"llmUnvalidated{s}") for k, s in pairs), True),
        ("VI Discussion", "constrained 1.5B vs unconstrained 7B MRR, methods",
         (r3(mrr("messages", "llm15B")), r3(mrr("messages", "llmUnvalidated7B"))), (0.729, 0.722)),
        ("VI Discussion", "constrained 1.5B vs unconstrained 7B MRR, classes",
         (r3(mrr("variables", "llm15B")), r3(mrr("variables", "llmUnvalidated7B"))), (0.846, 0.791)),
        ("VI Discussion", "Dependency Recall@10 at prefix 2, methods / classes (%)", both(lambda k: r1(rec(k, DEP, 2))), (57.9, 53.4)),
        ("VI Discussion", "class MRR at prefix 8, 7B reranking / constrained 7B",
         (r3(mrr("variables", "hybrid7B", 8)), r3(mrr("variables", "llm7B", 8))), (0.923, 0.912)),
        ("VI Discussion", "no 7B reversal for method MRR at any prefix",
         any(mrr("messages", "hybrid7B", p) > mrr("messages", "llm7B", p) for p in PREF), False),
        ("VI Discussion", "CLM mean time range (ms)", (msr(min(neural)), msr(max(neural))), (759, 5230)),
        ("VII Conclusion", "constrained 7B gain over Dependency, methods / classes (%)",
         both(lambda k: gain(k, "llm7B")), (49.7, 48.4)),
    ]


def settings():
    """Settings stated in the paper, read from the shipped benchmark source, image and run provenance."""
    src = ROOT / "lib" / "HeuristicCompletion-Benchmarks-Multiples" / "src" / "ExtendedHeuristicCompletion-Benchmarks"
    beam = (src / "CooLLMBeamCompleter.class.st").read_text(encoding="utf-8")
    client = (src / "CooLLMClient.class.st").read_text(encoding="utf-8")
    prov = ROOT / "data" / "provenance"
    logs = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in sorted((prov / "logs").glob("*")))
    setting = lambda text, pattern: (lambda m: m.group(1) if m else None)(re.search(pattern, text))
    jobs = sorted({json.loads(line)["jobs"] for line in (prov / "worker-invocations.jsonl").read_text().splitlines() if line})
    tags = json.loads((prov / "ollama-tags.json").read_text())["models"]
    with tarfile.open(ROOT / "frozen-image" / "pharo14-frozen-image.tar.gz") as archive:
        sources = [n for n in archive.getnames() if n.endswith(".sources")]
    models = json.loads((ROOT / "data" / "experiment" / "llm-models.json").read_text())
    analysed = [line.split("#", 1)[0].strip() for line in
                (ROOT / "data" / "experiment" / "analysed-packages.txt").read_text().splitlines()]
    analysed = {name for name in analysed if name}
    timings = [json.loads(line) for f in sorted(prov.glob("task-timings*.jsonl"))
               for line in f.read_text().splitlines() if line]
    hours = sum(t["seconds"] for t in timings if t["package"] in analysed) / 3600
    # Benchmarks started on Grid5000 (job logs); the others ran on the Mac.
    started = {m.groups() for f in sorted((prov / "logs").glob("heuristic-completion.*.out"))
               for m in re.finditer(r"Started (\S+) \[(\w+) (\w+)\]", f.read_text(encoding="utf-8", errors="replace"))
               if m.group(1) in analysed}
    grid_heuristics = sum(1 for _, _, s in started if s.startswith("heuristics"))
    grid_05b = sum(1 for _, _, s in started if s.endswith("05B"))
    return [
        ("III-A Observations", "OrderedCollection gives prefixes Or ... OrderedC (seven observations)",
         ["OrderedCollection"[:k] for k in range(2, min(len("OrderedCollection"), 8) + 1)][::6] + [min(len("OrderedCollection"), 8) - 1],
         ["Or", "OrderedC", 7]),
        ("IV-A Corpus", "application code, tools, tests and baseline packages",
         (any(p.startswith("BaselineOf") for p in analysed), any(p.endswith("-Tests") for p in analysed)), (True, True)),
        ("IV-A Models", "four Pharo-specialized Qwen2.5-Coder models, 0.5B / 1.5B / 3B / 7B",
         [m.split(":")[1].upper() for m in models if "Qwen2.5-Coder" in m], ["0.5B", "1.5B", "3B", "7B"]),
        ("IV-A Inference", "temperature / seed", (setting(client, r"payloadFor: snapshot temperature: (\d+) seed"),
                                                   setting(client, r"payloadFor: snapshot temperature: \d+ seed: (\d+)")), ("0", "42")),
        ("IV-A Inference", "context window (tokens)", setting(client, r"'num_ctx' -> (\d+)"), "8192"),
        ("IV-A Inference", "one token per request", setting(client, r"'num_predict' -> (\d+)"), "1"),
        ("IV-A Inference", "next-token alternatives per request", setting(beam, r"topTokens := (\d+)"), "20"),
        ("IV-A Inference", "beam width", setting(beam, r"beamWidth := (\d+)"), "10"),
        ("IV-A Inference", "maximum search steps", setting(beam, r"maxSteps := (\d+)"), "12"),
        ("IV-A Inference", "suggestions returned", setting(beam, r"candidateCount := (\d+)"), "10"),
        ("IV-D Environment", "request timeout (s)", setting(client, r"timeout := (\d+)"), "120"),
        ("IV-D Environment", "Grid5000 GPU", "AMD Instinct MI210" in logs, True),
        ("IV-D Environment", "Grid5000 Ollama version", setting(logs, r"\(Ollama (0\.40\.5)\)"), "0.40.5"),
        ("IV-D Environment", "Apple M4 Max machine", "Apple M4 Max" in logs, True),
        ("IV-D Environment", "Mac Ollama version", setting(logs, r"\(version (0\.40\.7)\)"), "0.40.7"),
        ("IV-D Environment", "benchmark workers (Mac, Grid5000 node)", jobs, [2, 8]),
        ("IV-D Environment", "F16 weights for the four models", sorted({m["details"]["quantization_level"] for m in tags}) + [len(tags)], ["F16", 4]),
        ("IV-D Environment", "Pharo 14.0 64-bit image, sources 74f3a1b", sources, ["Pharo14.0-64bit-74f3a1b.sources"]),
        ("IV-D Environment", "more than 100 hours of computation (recorded benchmark time)", hours > 100, True),
        ("IV-D Environment", "heuristics not run on Grid5000 (benchmarks started there)", grid_heuristics, 0),
        ("IV-D Environment", "most 0.5B benchmarks not run on Grid5000 (of 6 x 47)", grid_05b < 6 * len(analysed) / 2, True),
    ]


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
    try:
        checked = claims(st)
    except (TypeError, KeyError, ZeroDivisionError) as error:
        # A partial run (e.g. a few packages, no class observations) lacks numbers the text uses.
        checked = []
        failures.append(f"the paper's text claims cannot be recomputed from these results ({error!r})")
    try:
        checked += settings()
    except (OSError, KeyError, ValueError) as error:
        failures.append(f"the paper's settings cannot be checked ({error!r})")
    passed = 0
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
