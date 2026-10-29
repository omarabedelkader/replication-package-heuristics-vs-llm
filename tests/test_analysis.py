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

    def test_matched_population(self):
        extra = self.stats["extra"]
        self.assertEqual(len(extra["complete_packages"]), 47)
        self.assertEqual(set(extra["incomplete_packages"]),
                         {"Slot-Tests", "Reflectivity-Tests", "Morphic-Widgets-Windows"})
        self.assertEqual(self.stats["tasks_done"], 1367)

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
    """A package missing a benchmark is excluded, never filled with zeros."""

    def test_incomplete_package_is_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "packages"
            shutil.copytree(CHECKPOINTS / "0001", copy / "0001")
            shutil.copytree(CHECKPOINTS / "0002", copy / "0002")
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
            shutil.copytree(CHECKPOINTS / "0043", copy / "0043")  # BaselineOfReflectionMirrors
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
