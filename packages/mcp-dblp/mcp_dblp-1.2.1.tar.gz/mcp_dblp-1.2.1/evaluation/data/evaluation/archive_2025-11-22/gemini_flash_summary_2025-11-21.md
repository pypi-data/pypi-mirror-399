# Gemini Flash Analysis Summary

**Date:** 2025-11-21
**Analyst:** google/gemini-2.5-flash via consult7 (mid mode)
**Method:** 9 parallel runs (3 groups × 3 batches), per-citation classification

## Source Files

**Ground Truth:**
- `ground_truth/ground_truth.bib` (104 entries)

**Control Group (Web Search):**
- `data/results_control/control_output_v2_batch1.bib` (citations 1-35)
- `data/results_control/control_output_v2_batch2.bib` (citations 36-70)
- `data/results_control/control_output_v2_batch3.bib` (citations 71-104)

**Treatment V2 (MCP-DBLP Mediated):**
- `data/results_treatment_v2/treatment_output_v2_batch1.bib`
- `data/results_treatment_v2/treatment_output_v2_batch2.bib`
- `data/results_treatment_v2/treatment_output_v2_batch3.bib`

**Treatment V3 (MCP-DBLP Unmediated):**
- `data/results_treatment_v3/treatment_output_v3_batch1.bib`
- `data/results_treatment_v3/treatment_output_v3_batch2.bib`
- `data/results_treatment_v3/treatment_output_v3_batch3.bib`

## Error Categories

| Code | Category | Definition |
|------|----------|------------|
| PM | Perfect Match | Correct paper with complete metadata |
| WP | Wrong Paper | Different paper than ground truth |
| NF | Not Found | Entry missing or explicit NOT FOUND |
| IM | Incomplete Metadata | Correct paper, missing DOI/pages/venue |
| IA | Incomplete Author | Correct paper, truncated/unknown authors |
| CM | Corrupted Metadata | Correct paper, wrong values (typos, wrong DOI) |

## Results by Batch

### Control Group
| Batch | PM | WP | NF | IM | IA | CM | Total |
|-------|----|----|----|----|----|----|-------|
| 1 (1-35) | 1 | 4 | 13 | 9 | 7 | 1 | 35 |
| 2 (36-70) | 8 | 1 | 20 | 4 | 1 | 1 | 35 |
| 3 (71-104) | 1 | 5 | 16 | 9 | 2 | 1 | 34 |
| **Total** | **10** | **10** | **49** | **22** | **10** | **3** | **104** |

### Treatment V2 (Mediated)
| Batch | PM | WP | NF | IM | IA | CM | Total |
|-------|----|----|----|----|----|----|-------|
| 1 (1-35) | 25 | 4 | 4 | 2 | 0 | 0 | 35 |
| 2 (36-70) | 31 | 4 | 0 | 0 | 0 | 0 | 35 |
| 3 (71-104) | 25 | 9 | 0 | 0 | 0 | 0 | 34 |
| **Total** | **81** | **17** | **4** | **2** | **0** | **0** | **104** |

### Treatment V3 (Unmediated)
| Batch | PM | WP | NF | IM | IA | CM | Total |
|-------|----|----|----|----|----|----|-------|
| 1 (1-35) | 26 | 6 | 3 | 0 | 0 | 0 | 35 |
| 2 (36-70) | 31 | 3 | 1 | 0 | 0 | 0 | 35 |
| 3 (71-104) | 30 | 4 | 0 | 0 | 0 | 0 | 34 |
| **Total** | **87** | **13** | **4** | **0** | **0** | **0** | **104** |

## Summary Comparison (from CSV)

| Category | Control | V2 (Mediated) | V3 (Unmediated) |
|----------|---------|---------------|-----------------|
| **PM** | 9 (8.7%) | 81 (77.9%) | 87 (83.7%) |
| **WP** | 11 (10.6%) | 17 (16.3%) | 13 (12.5%) |
| **NF** | 46 (44.2%) | 4 (3.8%) | 4 (3.8%) |
| **IM** | 24 (23.1%) | 2 (1.9%) | 0 (0%) |
| **IA** | 11 (10.6%) | 0 (0%) | 0 (0%) |
| **CM** | 3 (2.9%) | 0 (0%) | 0 (0%) |

## Key Findings

1. **MCP-DBLP vs Web Search:** 9x improvement in perfect matches (81-87 vs 9)
2. **NF Reduction:** 91% fewer not-found errors (4 vs 46)
3. **Metadata Quality:** Both V2 and V3 have 0 CM (corrupted metadata)
4. **V3 vs V2:** V3 slightly better (+6 PM, -4 WP, -2 IM)

## V2 vs V3 Detailed Comparison

| Metric | V2 | V3 | Δ (V3-V2) |
|--------|----|----|-----------|
| PM | 81 | 87 | +6 |
| WP | 17 | 13 | -4 |
| NF | 4 | 4 | 0 |
| IM | 2 | 0 | -2 |
| CM | 0 | 0 | 0 |

**Conclusion:** V3 (unmediated) is slightly better than V2 (mediated), with +6 more perfect matches and 2 fewer incomplete metadata errors. Both have 0 corrupted metadata.

## Data File

Per-citation classifications: `gemini_flash_analysis_2025-11-21.csv`

## Reproducibility

To verify these results:
1. Load the CSV file
2. Count categories per group
3. Compare against source BibTeX files

```bash
# Verify counts
awk -F',' 'NR>1 {print $4}' gemini_flash_analysis_2025-11-21.csv | sort | uniq -c  # Control
awk -F',' 'NR>1 {print $6}' gemini_flash_analysis_2025-11-21.csv | sort | uniq -c  # V2
awk -F',' 'NR>1 {print $8}' gemini_flash_analysis_2025-11-21.csv | sort | uniq -c  # V3
```
