"""Tests of the paper analysis (python3 -m unittest discover -s tests)."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import reproduce_paper  # noqa: E402
import verify_paper  # noqa: E402

CHECKPOINTS = ROOT / "data" / "checkpoints"


class ReleasedCheckpoints(unittest.TestCase):
    """The released checkpoints reproduce the paper exactly."""

    @classmethod
    def setUpClass(cls):
        cls.out = Path(tempfile.mkdtemp())
        assert reproduce_paper.main(["--out", str(cls.out)]) == 0
        cls.stats = json.loads((cls.out / "analysis-stats.json").read_text())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out)

    def test_verification_passes(self):
        self.assertEqual(verify_paper.main(["--results", str(self.out)]), 0)

    def test_packages(self):
        names = [line.split("#", 1)[0].strip()
                 for line in (ROOT / "data" / "experiment" / "analysed-packages.txt").read_text().splitlines()]
        self.assertEqual(self.stats["extra"]["packages"], [name for name in names if name])
        self.assertEqual(len(self.stats["extra"]["packages"]), 47)
        self.assertEqual(self.stats["tasks_done"], 47 * 28)

    def test_one_directory_per_paper_package(self):
        names = [line.split("#", 1)[0].strip()
                 for line in (ROOT / "data" / "experiment" / "analysed-packages.txt").read_text().splitlines()]
        self.assertEqual(sorted(p.name for p in CHECKPOINTS.iterdir() if p.is_dir()), sorted(n for n in names if n))

    def test_reranking_keeps_recall(self):
        self.assertEqual(self.stats["hybrid_invariant"]["violations"], 0)


class Helpers(unittest.TestCase):
    def test_sign_test(self):
        self.assertEqual(reproduce_paper.sign_test(19, 18), 1.0)
        self.assertAlmostEqual(reproduce_paper.sign_test(47, 0), 2 / 2 ** 47)
        self.assertEqual(reproduce_paper.sign_test(0, 0), 1.0)

    def test_formatting(self):
        self.assertEqual(reproduce_paper.f3(0.2624), ".262")
        self.assertEqual(reproduce_paper.f3(1.0), "1.000")
        self.assertEqual(reproduce_paper.half_up(1698.5), 1699)
        self.assertEqual(reproduce_paper.thousands(3837.4), "3{,}837")
        self.assertEqual(reproduce_paper.gain(0.262, 0.517), r"\textsuperscript{$-$49.3\%}")

    def test_bold_best_marks_ties(self):
        self.assertEqual(reproduce_paper.bold_best([[".5", ".7", ".7"]]),
                         [[".5", r"\textbf{.7}", r"\textbf{.7}"]])


class IncompleteRun(unittest.TestCase):
    """In an unfinished re-run, a package missing a benchmark is skipped, never filled with zeros."""

    def test_unfinished_package_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "packages"
            shutil.copytree(CHECKPOINTS / "Network-Mail", copy / "0001")
            shutil.copytree(CHECKPOINTS / "Spec2-ListView", copy / "0002")
            (copy / "0002" / "benchmarks" / "messages-llm7B" / "part.json").unlink()
            workers = ROOT / "data" / "provenance" / "workers.json"
            manifest, parts, complete, incomplete = reproduce_paper.load(str(copy), workers)
            self.assertEqual(complete, ["Network-Mail"])
            self.assertEqual(incomplete["Spec2-ListView"], 27)
            self.assertEqual(reproduce_paper.main(["--checkpoints", str(copy), "--workers", str(workers),
                                                   "--out", str(Path(tmp) / "out")]), 0)

    def test_run_without_class_observations(self):
        """A small rerun (one package, no class completions) is analysed; empty cells print as --."""
        with tempfile.TemporaryDirectory() as tmp:
            copy, out = Path(tmp) / "packages", Path(tmp) / "out"
            shutil.copytree(CHECKPOINTS / "BaselineOfReflectionMirrors", copy / "BaselineOfReflectionMirrors")
            workers = ROOT / "data" / "provenance" / "workers.json"
            self.assertEqual(reproduce_paper.main(["--checkpoints", str(copy), "--workers", str(workers),
                                                   "--out", str(out)]), 0)
            stats = json.loads((out / "analysis-stats.json").read_text())
            self.assertEqual(stats["obs_matched"], {"messages": 13, "variables": 0})
            self.assertIsNone(stats["mrr/variables/llm7B/avg"])
            self.assertIn("& -- &", (out / "paper" / "tab-top-k-accuracy.tex").read_text())
            self.assertEqual(verify_paper.main(["--results", str(out)]), 1)


if __name__ == "__main__":
    unittest.main()
