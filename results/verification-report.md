# Paper claims recomputed from the checkpoints

| Section | Claim | Recomputed | Paper | |
|---|---|---|---|---|
| Abstract | packages analysed | 47 | 47 | ok |
| Abstract | constrained 7B MRR gain over Dependency, methods (%) | 49.7 | 49.7 | ok |
| Abstract | constrained 7B MRR gain over Dependency, classes (%) | 48.4 | 48.4 | ok |
| Abstract | 7B reranking MRR gain over Dependency, methods (%) | 26.9 | 26.9 | ok |
| Abstract | 7B reranking MRR gain over Dependency, classes (%) | 37.2 | 37.2 | ok |
| Abstract | constraints lower mean time (of 8 comparisons) | 7 | 7 | ok |
| Abstract | 7B reranker beats constrained class MRR at prefixes 5-8 | True | True | ok |
| Setup | eligible packages | 733 | 733 | ok |
| Setup | classes in matched packages | 501 | 501 | ok |
| Setup | traversed methods in matched packages | 4277 | 4277 | ok |
| Setup | method observations | 103391 | 103391 | ok |
| Setup | class observations | 12678 | 12678 | ok |
| Setup | observations per configuration | 116069 | 116069 | ok |
| Setup | packages contributing method observations | 47 | 47 | ok |
| Setup | packages contributing class observations | 37 | 37 | ok |
| Setup | observation counts match across configurations | True | True | ok |
| Setup | package comparisons in the sign-test family | 26 | 26 | ok |
| RQ1 | Baseline MRR, methods | 0.262 | 0.262 | ok |
| RQ1 | Dependency MRR, methods | 0.517 | 0.517 | ok |
| RQ1 | Baseline MRR, classes | 0.407 | 0.407 | ok |
| RQ1 | Dependency MRR, classes | 0.592 | 0.592 | ok |
| RQ1 | every CLM configuration beats both heuristics (pooled MRR) | True | True | ok |
| RQ1 | constrained 7B MRR, methods | 0.774 | 0.774 | ok |
| RQ1 | constrained 7B MRR, classes | 0.879 | 0.879 | ok |
| RQ1 | constrained 7B Top-1, methods (%) | 73.6 | 73.6 | ok |
| RQ1 | constrained 7B Top-1, classes (%) | 83.3 | 83.3 | ok |
| RQ1 | Dependency Top-1, methods (%) | 37.4 | 37.4 | ok |
| RQ1 | Dependency Top-1, classes (%) | 45.4 | 45.4 | ok |
| RQ1 | constrained 7B > Dependency, method packages (win/loss/tie) | (46, 1, 0) | (46, 1, 0) | ok |
| RQ1 |   ... p < 1e-12 | True | True | ok |
| RQ1 | constrained 7B > Dependency, class packages (win/loss/tie) | (32, 4, 1) | (32, 4, 1) | ok |
| RQ1 |   ... p < 1e-5 | True | True | ok |
| RQ1 | packages in the scatter plot (methods, classes) | (46, 34) | (46, 34) | ok |
| RQ2 | constraints improve MRR at every size and task | True | True | ok |
| RQ2 | largest within-size constraint gain is at 0.5B (both tasks) | True | True | ok |
| RQ2 | unconstrained 7B Top-1, methods (%) | 68.1 | 68.1 | ok |
| RQ2 | unconstrained 7B Top-1, classes (%) | 73.4 | 73.4 | ok |
| RQ2 | method packages favouring constraints at 0.5B/3B/7B | [47, 47, 47] | [47, 47, 47] | ok |
| RQ2 | method packages at 1.5B (win, tie) | (46, 1) | (46, 1) | ok |
| RQ2 | no class package favours unconstrained generation | True | True | ok |
| RQ2 | constrained mean list length range, methods | (4.4, 4.5) | (4.4, 4.5) | ok |
| RQ2 | constrained mean list length range, classes | (2.2, 2.8) | (2.2, 2.8) | ok |
| RQ2 | unconstrained 7B membership, methods (%) | 22.5 | 22.5 | ok |
| RQ2 | unconstrained 7B membership, classes (%) | 15.8 | 15.8 | ok |
| RQ3 | reranking improves Dependency MRR at every size | True | True | ok |
| RQ3 | 7B reranking MRR, methods | 0.656 | 0.656 | ok |
| RQ3 | 7B reranking MRR, classes | 0.813 | 0.813 | ok |
| RQ3 | 7B reranking > Dependency, method packages | 47 | 47 | ok |
| RQ3 | 7B reranking > Dependency, class packages (win, of) | (34, 37) | (34, 37) | ok |
| RQ3 |   ... class p < 1e-6 | True | True | ok |
| RQ3 | Recall@10 of reranking = Dependency, methods (%) | 81.1 | 81.1 | ok |
| RQ3 | Recall@10 of reranking = Dependency, classes (%) | 84.8 | 84.8 | ok |
| RQ3 | reranking never changes Recall@10 (package x prefix cells violating) | 0 | 0 | ok |
| RQ3 | conditional Top-1, 7B reranker, methods (%) | 70.7 | 70.7 | ok |
| RQ3 | conditional Top-1, 7B reranker, classes (%) | 92.6 | 92.6 | ok |
| RQ3 | conditional Top-1, Dependency, methods (%) | 46.1 | 46.1 | ok |
| RQ3 | conditional Top-1, Dependency, classes (%) | 53.6 | 53.6 | ok |
| RQ3 | Dependency coverage at prefix 2 (methods, classes) | (57.9, 53.4) | (57.9, 53.4) | ok |
| RQ3 | constrained 7B Top-1 at prefix 2 (methods, classes) | (67.7, 74.7) | (67.7, 74.7) | ok |
| RQ3 | class prefixes where 7B reranker Top-1 > constrained 7B | [4, 5, 6, 7, 8] | [4, 5, 6, 7, 8] | ok |
| RQ3 | class prefixes where 7B reranker MRR > constrained 7B | [5, 6, 7, 8] | [5, 6, 7, 8] | ok |
| RQ3 | class MRR at prefix 8 (reranking, constrained) | (0.923, 0.912) | (0.923, 0.912) | ok |
| RQ3 | method prefixes where 7B reranker MRR > constrained 7B | [] | [] | ok |
| RQ3 | method MRR at prefix 8, 3B (reranking, constrained) | (0.851, 0.846) | (0.851, 0.846) | ok |
| RQ3 | pooled 3B method MRR favours constrained generation | True | True | ok |
| RQ3 | method coverage at prefix 8 (Dependency, constrained 7B) | (96.7, 89.7) | (96.7, 89.7) | ok |
| RQ3 | method MRR at prefix 8 (Dependency, constrained 7B) | (0.765, 0.867) | (0.765, 0.867) | ok |
| RQ3 | constrained > reranking pooled MRR at every size | True | True | ok |
| RQ3 | method packages favouring constrained 7B over 7B reranking | 36 | 36 | ok |
| RQ3 | class packages: favour constrained 7B, favour 7B reranking | (19, 18) | (19, 18) | ok |
| RQ3 |   ... p = 1.0 | 1.0 | 1.0 | ok |
| RQ4 | pooled MRR increases with size within each CLM strategy | True | True | ok |
| RQ4 | largest adjacent-size gain is 0.5B -> 1.5B | True | True | ok |
| RQ4 | constrained 1.5B > 0.5B, method packages | 42 | 42 | ok |
| RQ4 | constrained 1.5B MRR (methods, classes) | (0.729, 0.846) | (0.729, 0.846) | ok |
| RQ4 | constrained 7B vs 1.5B, method packages (win/loss/tie) | (39, 2, 6) | (39, 2, 6) | ok |
| RQ4 | constrained 0.5B > Dependency (method packages, class packages) | (43, 25) | (43, 25) | ok |
| RQ4 |   ... class p (2 decimals) | 0.03 | 0.03 | ok |
| RQ4 |   ... class p above the Bonferroni threshold 0.05/26 | True | True | ok |
| RQ4 | neural mean time range (s) | (0.76, 5.23) | (0.76, 5.23) | ok |
| RQ4 | heuristic mean time, methods (Baseline, Dependency ms) | (105, 160) | (105, 160) | ok |
| RQ4 | heuristic mean time, classes (Baseline, Dependency ms) | (11, 26) | (11, 26) | ok |
| RQ4 | time reductions from constraints (min, max %) | (13, 60) | (13, 60) | ok |
| RQ4 | exception: 1.5B class time (unconstrained, constrained ms) | (759, 999) | (759, 999) | ok |
| RQ4 | constrained method time (0.5B, 1.5B ms) | (3354, 835) | (3354, 835) | ok |
| RQ4 | 7B reranking time (methods, classes ms) | (2168, 2318) | (2168, 2318) | ok |
| RQ4 | constrained 7B time (methods, classes ms) | (2074, 1956) | (2074, 1956) | ok |
| RQ4 | exact constrained 3B method mean (ms, label 1,699) | 1698.52 | 1698.52 | ok |
| Synthesis | class 1.5B MRR gain from constraints | 0.1 | 0.1 | ok |
| Synthesis | class MRR gain from scaling constrained 1.5B -> 7B | 0.033 | 0.033 | ok |
