# Tables and Figures for MCP-DBLP Paper

## Table 1: Overall Performance Metrics

| Metric | Control (Web Search) | Treatment (MCP-DBLP) | Improvement |
|--------|---------------------|----------------------|-------------|
| **Coverage Rate** | 35.6% (37/104) | 75.0% (78/104) | +39.4pp (+110.7%) |
| **Quality Rate** | 8.1% (3/37) | 100.0% (78/78) | +91.9pp (+1,133%) |
| **End-to-End Success** | 2.9% (3/104) | 75.0% (78/104) | +72.1pp (+2,486%) |

*Note: Coverage = papers found / total; Quality = perfect matches / found papers; End-to-End = perfect matches / total*

---

## Table 2: Error Category Distribution

| Error Category | Description | Control | Treatment | Δ |
|----------------|-------------|---------|-----------|---|
| **NF** | Not Found | 67 (64.4%) | 26 (25.0%) | -41 |
| **WP** | Wrong Paper | 0 (0.0%) | 0 (0.0%) | 0 |
| **FP** | Fabricated Paper | 0 (0.0%) | 0 (0.0%) | 0 |
| **FM** | Fabricated Metadata | 0 (0.0%) | 0 (0.0%) | 0 |
| **CM** | Corrupted Metadata | 18 (17.3%) | 0 (0.0%) | -18 |
| **IA** | Incomplete Author | 4 (3.8%) | 0 (0.0%) | -4 |
| **IM** | Incomplete Metadata | 12 (11.5%) | 0 (0.0%) | -12 |
| **PM** | Perfect Match | 3 (2.9%) | 78 (75.0%) | +75 |
| **Total** | | 104 | 104 | |

---

## Table 3: Error Severity Breakdown

| Severity Level | Error Types | Control | Treatment | Reduction |
|----------------|-------------|---------|-----------|-----------|
| **Critical Failures** | NF, WP, FP | 67 (64.4%) | 26 (25.0%) | -39.4pp |
| **Integrity Failures** | FM, CM | 18 (17.3%) | 0 (0.0%) | -17.3pp |
| **Completeness Failures** | IA, IM | 16 (15.4%) | 0 (0.0%) | -15.4pp |
| **Success** | PM | 3 (2.9%) | 78 (75.0%) | +72.1pp |

---

## Table 4: Control Group Error Breakdown (37 Papers Found)

| Error Type | Count | % of Found | Description |
|------------|-------|------------|-------------|
| **Corrupted Metadata** | 18 | 48.6% | Wrong DOI, corrupted authors |
| **Incomplete Metadata** | 12 | 32.4% | Missing DOI/pages |
| **Incomplete Author** | 4 | 10.8% | "Author Unknown" |
| **Perfect Match** | 3 | 8.1% | Correct metadata |
| **Total Found** | 37 | 100% | |

---

## Table 5: Notable Error Examples

| Citation | Ground Truth | Control Error | Control Details | Treatment |
|----------|--------------|---------------|-----------------|-----------|
| 5 | Li's 3-path vertex paper, 2025 | CM | Wrong DOI: `10.1007/s10878...` vs `10.1007/S10586...` | PM |
| 7 | Levine's advantage paper, 2022 | CM | Author corruption (similarity: 0.43) | PM |
| 12 | CUDA optimization, 2025 | CM | DOI mismatch + author corruption (0.00) | PM |
| 98 | Mouse genome database, 2017 | IA | "Author Unknown" placeholder | PM |
| 100 | Supervised ML, Cukurova 2018 | CM | DOI case error: `jcal` vs `JCAL` | PM |

CM = Corrupted Metadata, IA = Incomplete Author, PM = Perfect Match

---

## Figure 1: Coverage Comparison (Bar Chart Data)

```
Control:  ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  35.6% (37/104)
Treatment: ████████████████████████████████████████░░░░░░░░  75.0% (78/104)
```

---

## Figure 2: Quality Rate Comparison (Bar Chart Data)

Among papers found:

```
Control:  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  8.1% (3/37)
Treatment: ████████████████████████████████████████  100% (78/78)
```

---

## Figure 3: Error Distribution Stacked Bar Chart Data

**Control Group (n=104):**
- NF: 67 (64.4%)
- CM: 18 (17.3%)
- IM: 12 (11.5%)
- IA: 4 (3.8%)
- PM: 3 (2.9%)

**Treatment Group (n=104):**
- NF: 26 (25.0%)
- PM: 78 (75.0%)
- All others: 0

---

## Statistical Test Results

### McNemar's Test for Coverage (Found vs Not Found)

|  | Treatment Found | Treatment Not Found | Total |
|--|-----------------|---------------------|-------|
| **Control Found** | 37 | 0 | 37 |
| **Control Not Found** | 41 | 26 | 67 |
| **Total** | 78 | 26 | 104 |

- **Discordant pairs:** 41 (treatment success, control failure)
- **McNemar statistic:** χ² = 41.0
- **p-value:** < 0.001 (highly significant)

### Fisher's Exact Test for Quality (PM vs Non-PM among found)

|  | Treatment | Control | Total |
|--|-----------|---------|-------|
| **Perfect Match** | 78 | 3 | 81 |
| **Non-Perfect** | 0 | 34 | 34 |
| **Total Found** | 78 | 37 | 115 |

- **p-value:** < 0.001 (highly significant)
- **Odds ratio:** ∞ (treatment has zero non-perfect matches)

---

## LaTeX Table Code

### Table 1: Performance Metrics

```latex
\begin{table}[htbp]
\centering
\caption{Overall Performance Comparison}
\label{tab:performance}
\begin{tabular}{lrrr}
\toprule
\textbf{Metric} & \textbf{Control} & \textbf{Treatment} & \textbf{Improvement} \\
\midrule
Coverage Rate & 35.6\% (37/104) & 75.0\% (78/104) & +39.4pp (+110.7\%) \\
Quality Rate & 8.1\% (3/37) & 100.0\% (78/78) & +91.9pp (+1,133\%) \\
End-to-End Success & 2.9\% (3/104) & 75.0\% (78/104) & +72.1pp (+2,486\%) \\
\bottomrule
\end{tabular}
\end{table}
```

### Table 2: Error Distribution

```latex
\begin{table}[htbp]
\centering
\caption{Error Category Distribution (N=104)}
\label{tab:errors}
\begin{tabular}{llrrr}
\toprule
\textbf{Code} & \textbf{Description} & \textbf{Control} & \textbf{Treatment} & \textbf{Δ} \\
\midrule
NF & Not Found & 67 (64.4\%) & 26 (25.0\%) & -41 \\
WP & Wrong Paper & 0 (0.0\%) & 0 (0.0\%) & 0 \\
FP & Fabricated Paper & 0 (0.0\%) & 0 (0.0\%) & 0 \\
FM & Fabricated Metadata & 0 (0.0\%) & 0 (0.0\%) & 0 \\
CM & Corrupted Metadata & 18 (17.3\%) & 0 (0.0\%) & -18 \\
IA & Incomplete Author & 4 (3.8\%) & 0 (0.0\%) & -4 \\
IM & Incomplete Metadata & 12 (11.5\%) & 0 (0.0\%) & -12 \\
PM & Perfect Match & 3 (2.9\%) & 78 (75.0\%) & +75 \\
\midrule
\textbf{Total} & & 104 & 104 & \\
\bottomrule
\end{tabular}
\end{table}
```

---

## Key Quotes for Paper

### Abstract/Introduction
> "The treatment group (MCP-DBLP) achieved 2.11× higher coverage (75.0% vs 35.6%) and 12.3× higher quality (100% vs 8.1%) compared to web search alone."

### Results Section
> "Among the 37 papers found by the control group, only 3 (8.1%) had correct metadata, while 18 (48.6%) exhibited corrupted metadata including wrong DOIs and author name corruption."

> "The treatment group achieved zero metadata errors across all 78 found papers, demonstrating the reliability of unmediated DBLP export."

### Discussion
> "The elimination of all 34 metadata quality errors (18 CM + 12 IM + 4 IA) in the treatment group validates our core hypothesis: direct BibTeX export from authoritative sources eliminates transcription and LLM-induced corruption."

### Limitations
> "The treatment group's 26 not-found cases (25.0%) primarily represent papers outside DBLP's coverage, not system failures. In contrast, the control group's 67 not-found cases (64.4%) include 41 papers that DBLP successfully indexed, indicating search strategy limitations."

---

## Data Files Reference

- Full results: `evaluation/data/full_evaluation_results.txt`
- Summary: `evaluation/data/evaluation_summary.md`
- Raw output: `evaluation/data/evaluation_output_v2.txt`
- Ground truth: `evaluation/ground_truth/ground_truth.bib`
- Mapping: `evaluation/ground_truth/ground_truth_metadata_regenerated.csv`
