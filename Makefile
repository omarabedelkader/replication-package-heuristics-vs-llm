# Replication package entry points. `make` = reproduce and verify the paper's results.
PYTHON ?= python3
EXPERIMENT_DIR ?= experiment

.PHONY: all reproduce verify test test-pipeline setup smoke rerun checksums clean

all: verify

reproduce:            ## regenerate every table, figure and statistic from the checkpoints
	$(PYTHON) analysis/reproduce_paper.py

verify: reproduce     ## compare them with the paper (exit 0 = identical)
	$(PYTHON) analysis/verify_paper.py

test:                 ## tests of the analysis
	$(PYTHON) -m unittest discover -s tests -v

test-pipeline:        ## original tests of the benchmark pipeline (about 3 min)
	cd pipeline && $(PYTHON) -m unittest discover -s tests

setup:                ## experiment directory with the frozen image (downloads the Pharo VM)
	rerun/setup-frozen-experiment.sh $(EXPERIMENT_DIR)

smoke: 	              ## re-run the heuristic benchmarks of one package; no GPU needed
	rerun/smoke-test.sh $(EXPERIMENT_DIR)

rerun:                ## the 1,316 benchmarks of the 47 analysed packages (GPU, days); then analyse them
	rerun/run-benchmarks.sh $(EXPERIMENT_DIR)

checksums:            ## check that the shipped files are the released ones
	shasum -a 256 -c SHA256SUMS

clean:
	rm -rf results/paper results/analysis-stats.json results/verification-report.md
