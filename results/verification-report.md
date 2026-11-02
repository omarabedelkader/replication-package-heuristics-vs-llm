# Paper claims recomputed from the checkpoints

| Section | Claim | Recomputed | Paper | |
|---|---|---|---|---|
| Abstract | packages | 47 | 47 | ok |
| Abstract | more than 100K completions | True | True | ok |
| Abstract | constrained (7B) MRR gain over Dependency, methods / classes (%) | (49.7, 48.4) | (49.7, 48.4) | ok |
| Introduction | experimental configurations (2 + 3 x 3) | 11 | 11 | ok |
| IV-A Corpus | packages | 47 | 47 | ok |
| IV-A Corpus | classes | 501 | 501 | ok |
| IV-A Corpus | methods | 4277 | 4277 | ok |
| IV-A Corpus | method-selector observations | 103391 | 103391 | ok |
| IV-A Corpus | class-name observations | 12678 | 12678 | ok |
| IV-A Corpus | observations per approach | 116069 | 116069 | ok |
| IV-A Corpus | same observations for every configuration | True | True | ok |
| IV-C Environment | more than 100 hours of computation (summed completion time, all benchmarks) | True | True | ok |
| IV-B Completion time | constrained 3B, methods: total ms | 175612087 | 175612087 | ok |
| IV-B Completion time | constrained 3B, methods: observations | 103391 | 103391 | ok |
| IV-B Completion time | constrained 3B, methods: mean ms | 1698.5 | 1698.5 | ok |
| RQ1 | Baseline -> Dependency MRR, methods | (0.262, 0.517) | (0.262, 0.517) | ok |
| RQ1 | Baseline -> Dependency MRR, classes | (0.407, 0.592) | (0.407, 0.592) | ok |
| RQ1 | every CLM configuration has higher MRR than Dependency | True | True | ok |
| RQ1 | unconstrained 1.5B MRR, methods / classes | (0.668, 0.746) | (0.668, 0.746) | ok |
| RQ1 | unconstrained 3B / 7B MRR, methods / classes | ((0.698, 0.764), (0.722, 0.791)) | ((0.698, 0.764), (0.722, 0.791)) | ok |
| RQ1 | unconstrained gap over Dependency increases with size, both tasks | True | True | ok |
| RQ1 | constrained has the highest MRR at every size, both tasks | True | True | ok |
| RQ1 | constrained 7B MRR, methods / classes | (0.774, 0.879) | (0.774, 0.879) | ok |
| RQ1 | constrained 7B gain over Dependency, methods / classes (%) | (49.7, 48.4) | (49.7, 48.4) | ok |
| RQ1 | constrained 7B has the highest MRR of all configurations (both tasks) | True | True | ok |
| RQ2 | constraints improve MRR at every size, both tasks | True | True | ok |
| RQ2 | 1.5B unconstrained -> constrained MRR, methods | (0.668, 0.729) | (0.668, 0.729) | ok |
| RQ2 | 1.5B unconstrained -> constrained MRR, classes | (0.746, 0.846) | (0.746, 0.846) | ok |
| RQ2 | 7B unconstrained -> constrained MRR, methods | (0.722, 0.774) | (0.722, 0.774) | ok |
| RQ2 | 7B unconstrained -> constrained MRR, classes | (0.791, 0.879) | (0.791, 0.879) | ok |
| RQ2 | 7B unconstrained -> constrained Top-1, methods (%) | (68.1, 73.6) | (68.1, 73.6) | ok |
| RQ2 | 7B unconstrained -> constrained Top-1, classes (%) | (73.4, 83.3) | (73.4, 83.3) | ok |
| RQ2 | unconstrained 7B names in the runtime, methods / classes (%) | (22.5, 15.8) | (22.5, 15.8) | ok |
| RQ2 | all constrained names in the runtime (%) | 100.0 | 100.0 | ok |
| RQ2 | unconstrained mean list length, close to ten | 10 | 10 | ok |
| RQ2 | constrained mean list length range, methods | (4.4, 4.5) | (4.4, 4.5) | ok |
| RQ2 answer | the MRR gains of constraints are larger for smaller models (1.5B > 3B > 7B), both tasks | True | True | ok |
| RQ2 | constrained mean list length range, classes | (2.4, 2.8) | (2.4, 2.8) | ok |
| RQ3 | reranking improves Dependency MRR at every size, both tasks | True | True | ok |
| RQ3 | Dependency -> 7B reranking MRR, methods | (0.517, 0.656) | (0.517, 0.656) | ok |
| RQ3 | Dependency -> 7B reranking MRR, classes | (0.592, 0.813) | (0.592, 0.813) | ok |
| RQ3 | Recall@10 of Dependency = of reranking (every size), methods / classes (%) | (81.1, 84.8) | (81.1, 84.8) | ok |
| RQ3 | reranking never changes Recall@10 (package x prefix cells violating) | 0 | 0 | ok |
| RQ3 | conditional Top-1, 7B reranker, methods / classes (%) | (70.7, 92.6) | (70.7, 92.6) | ok |
| RQ3 | conditional Top-1, Dependency, methods / classes (%) | (46.1, 53.6) | (46.1, 53.6) | ok |
| RQ3 | Dependency Recall@10 at prefix 2, methods / classes (%) | (57.9, 53.4) | (57.9, 53.4) | ok |
| RQ3 | constrained 7B Top-1 at prefix 2, methods / classes (%) | (67.7, 74.7) | (67.7, 74.7) | ok |
| RQ3 | class prefixes where 7B reranker Top-1 > constrained 7B | [4, 5, 6, 7, 8] | [4, 5, 6, 7, 8] | ok |
| RQ3 | class prefixes where 7B reranker MRR > constrained 7B | [5, 6, 7, 8] | [5, 6, 7, 8] | ok |
| RQ3 | class MRR at prefix 8, 7B reranking / constrained 7B | (0.923, 0.912) | (0.923, 0.912) | ok |
| RQ3 | Dependency Recall@10 at class prefix 8 (%) | 95.1 | 95.1 | ok |
| RQ3 | method prefixes where constrained 7B MRR > 7B reranker | [2, 3, 4, 5, 6, 7, 8] | [2, 3, 4, 5, 6, 7, 8] | ok |
| RQ3 | Recall@10 at method prefix 8, Dependency / constrained 7B (%) | (96.7, 89.7) | (96.7, 89.7) | ok |
| RQ3 | method MRR at prefix 8, 7B reranking / constrained 7B | (0.863, 0.867) | (0.863, 0.867) | ok |
| RQ3 | constrained > reranking MRR at every size, both tasks | True | True | ok |
| RQ4 | MRR increases with size for each CLM approach, both tasks | True | True | ok |
| RQ4 | constrained 1.5B / 3B / 7B MRR, methods | (0.729, 0.754, 0.774) | (0.729, 0.754, 0.774) | ok |
| RQ4 | constrained 1.5B / 3B / 7B MRR, classes | (0.846, 0.861, 0.879) | (0.846, 0.861, 0.879) | ok |
| RQ4 | constrained 7B MRR, methods / classes | (0.774, 0.879) | (0.774, 0.879) | ok |
| RQ4 | constrained 1.5B MRR > Dependency, both tasks | True | True | ok |
| RQ4 | CLM mean time range (ms) | (759, 3947) | (759, 3947) | ok |
| RQ4 | Baseline / Dependency mean time, methods (ms) | (105, 160) | (105, 160) | ok |
| RQ4 | Baseline / Dependency mean time, classes (ms) | (11, 26) | (11, 26) | ok |
| RQ4 | constraints faster (of 6 size x task combinations) | 5 | 5 | ok |
| RQ4 | 7B unconstrained -> constrained time, methods (ms) | (3947, 2074) | (3947, 2074) | ok |
| RQ4 | 7B unconstrained -> constrained time, classes (ms) | (3802, 1956) | (3802, 1956) | ok |
| RQ4 | the exception is 1.5B classes | [('variables', '15B')] | [('variables', '15B')] | ok |
| RQ4 | 1.5B class time, constrained / unconstrained (ms) | (999, 759) | (999, 759) | ok |
| RQ4 | constrained method time, 1.5B / 3B / 7B (ms) | (835, 1699, 2074) | (835, 1699, 2074) | ok |
| RQ4 | time increases with size except reranking classes 3B -> 7B | [('variables', 'hybrid', '3B')] | [('variables', 'hybrid', '3B')] | ok |
| RQ4 | reranking class time, 3B / 7B (ms) | (2368, 2318) | (2368, 2318) | ok |
| RQ4 | 7B reranking time, methods / classes (ms) | (2168, 2318) | (2168, 2318) | ok |
| RQ4 | constrained 7B time, methods / classes (ms) | (2074, 1956) | (2074, 1956) | ok |
| VI Discussion | constraints improve Top-1 at every size, both tasks | True | True | ok |
| VI Discussion | constrained 1.5B vs unconstrained 7B MRR, methods | (0.729, 0.722) | (0.729, 0.722) | ok |
| VI Discussion | constrained 1.5B vs unconstrained 7B MRR, classes | (0.846, 0.791) | (0.846, 0.791) | ok |
| VI Discussion | Dependency Recall@10 at prefix 2, methods / classes (%) | (57.9, 53.4) | (57.9, 53.4) | ok |
| VI Discussion | class MRR at prefix 8, 7B reranking / constrained 7B | (0.923, 0.912) | (0.923, 0.912) | ok |
| VI Discussion | no 7B reversal for method MRR at any prefix | False | False | ok |
| VI Discussion | CLM mean time range (ms) | (759, 3947) | (759, 3947) | ok |
| VII Conclusion | constrained 7B gain over Dependency, methods / classes (%) | (49.7, 48.4) | (49.7, 48.4) | ok |
| III-A Observations | typed prefixes k = 2 .. min(L, 8) | ('2', '8') | ('2', '8') | ok |
| III-A Observations | class-name prefixes k = 2 .. min(L, 8) | ('2', '8') | ('2', '8') | ok |
| III-A Observations | prefix lengths present in the checkpoints | [2, 3, 4, 5, 6, 7, 8] | [2, 3, 4, 5, 6, 7, 8] | ok |
| III-A Observations | OrderedCollection gives prefixes Or ... OrderedC (seven observations) | ['Or', 'OrderedC', 7] | ['Or', 'OrderedC', 7] | ok |
| IV-A Corpus | application code, tools, tests and baseline packages | (True, True) | (True, True) | ok |
| IV-A Models | three Pharo-specialized Qwen2.5-Coder models, 1.5B / 3B / 7B | ['1.5B', '3B', '7B'] | ['1.5B', '3B', '7B'] | ok |
| IV-A Inference | temperature / seed | ('0', '42') | ('0', '42') | ok |
| IV-A Inference | context window (tokens) | 8192 | 8192 | ok |
| IV-A Inference | one token per request | 1 | 1 | ok |
| IV-A Inference | next-token alternatives per request | 20 | 20 | ok |
| IV-A Inference | beam width | 10 | 10 | ok |
| IV-A Inference | maximum search steps | 12 | 12 | ok |
| III-C Reranking | reranking: next-token alternatives / step limit | ('20', '12') | ('20', '12') | ok |
| IV-A Inference | suggestions returned | 10 | 10 | ok |
| IV-C Environment | request timeout (s) | 120 | 120 | ok |
| IV-C Environment | benchmark workers per node (job.oar.sh) | 8 | 8 | ok |
| IV-C Environment | Ollama release (job.oar.sh) | 0.40.5 | 0.40.5 | ok |
| IV-C Environment | F16 weights for every model | ['F16'] | ['F16'] | ok |
| IV-C Environment | frozen image is the pinned image of the run | True | True | ok |
| IV-C Environment | Pharo 14.0 64-bit image, sources 74f3a1b | ['Pharo14.0-64bit-74f3a1b.sources'] | ['Pharo14.0-64bit-74f3a1b.sources'] | ok |
