# Consolidated Gemini Flash 3x3 Evaluation Results

**Date:** 2025-11-22
**Model:** google/gemini-2.5-flash (mid mode)
**Total citations:** 104
**Methodology:** Two independent runs compared, discrepancies resolved by manual inspection of BibTeX entries

## Summary Statistics

| Category | Control | V2 (Mediated) | V3 (Unmediated) |
|----------|---------|---------------|-----------------|
| **PM** | 4 (3.8%) | 81 (77.9%) | **82 (78.8%)** |
| **WP** | 12 (11.5%) | 17 (16.3%) | 18 (17.3%) |
| **NF** | 46 (44.2%) | 4 (3.8%) | 4 (3.8%) |
| **IM** | 31 (29.8%) | 2 (1.9%) | **0 (0%)** |
| **IA** | 8 (7.7%) | 0 (0%) | 0 (0%) |
| **CM** | 3 (2.9%) | **0 (0%)** | **0 (0%)** |

## Key Findings

1. **MCP-DBLP vs Web Search:** ~20x improvement in perfect matches (81-82 vs 4)
2. **NF Reduction:** 91% fewer not-found errors (4 vs 46)
3. **Metadata Quality:** Both V2 and V3 have **0 CM** (corrupted metadata)
4. **V3 vs V2:** V3 slightly better (+1 PM, -2 IM) but +1 WP
5. **Control metadata issues:** 39 citations with metadata problems (IM+IA) vs 2 for V2, 0 for V3

## Reconciliation Process

Two independent Gemini Flash runs produced 26 citation discrepancies. Each was resolved by manual inspection:

### Control Discrepancies Resolved (21 citations)
- **IA vs IM decisions:** Based on whether authors were missing/truncated (IA) vs other metadata incomplete (IM)
- **CM identification:** Wrong year (citations 22, 66), wrong journal (citation 49)
- **WP identification:** ArXiv vs published (citation 86), different papers (multiple)

### V3 Discrepancies Resolved (5 citations)
All 5 were confirmed as WP (Wrong Paper):
- Citation 62: Found different Vakili paper (IoT vs geotechnical)
- Citation 74: Found proceedings volume, not specific paper
- Citation 89: Found different Mallet (steganalysis vs rain nowcasting)
- Citation 102: Found different Necci/Tosatto paper (PhytoTypeDB vs sequence-feature)
- Citation 103: Found different Doppa paper (Manycore vs Bayesian Optimization)

## Category Definitions

| Code | Category | Definition |
|------|----------|------------|
| PM | Perfect Match | Correct paper with complete metadata |
| WP | Wrong Paper | Different paper than ground truth |
| NF | Not Found | Entry missing or explicit NOT FOUND |
| IM | Incomplete Metadata | Correct paper, missing DOI/pages/venue/URL |
| IA | Incomplete Author | Correct paper, truncated/unknown authors |
| CM | Corrupted Metadata | Correct paper, wrong values (year, journal, DOI) |

## Data Files

- `gemini_flash_analysis_consolidated.csv` - Final per-citation classifications (104 rows)
- `gemini_flash_analysis_2025-11-21.csv` - Run 1 raw results
- `gemini_flash_analysis_2025-11-21_v2.csv` - Run 2 raw results
- This file - Consolidated summary

## Comparison with Previous Runs

| Metric | Run 1 | Run 2 | Consolidated |
|--------|-------|-------|--------------|
| Control PM | 9 | 5 | **4** |
| Control WP | 11 | 13 | **12** |
| Control NF | 46 | 45 | **46** |
| Control IM | 24 | 35 | **31** |
| Control IA | 11 | 4 | **8** |
| Control CM | 3 | 2 | **3** |
| V3 PM | 87 | 82 | **82** |
| V3 WP | 13 | 18 | **18** |

The consolidated results are more accurate because ambiguous cases were resolved by examining actual BibTeX content.
