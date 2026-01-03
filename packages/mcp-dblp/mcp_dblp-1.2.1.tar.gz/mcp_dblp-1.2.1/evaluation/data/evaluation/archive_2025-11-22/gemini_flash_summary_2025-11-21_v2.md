# Gemini Flash 3x3 Evaluation Results

**Date:** 2025-11-21 (Run 2)
**Model:** google/gemini-2.5-flash (mid mode)
**Total citations:** 104

## Summary Statistics

| Category | Control | V2 (Mediated) | V3 (Unmediated) |
|----------|---------|---------------|-----------------|
| **PM** | 5 (4.8%) | 81 (77.9%) | **82 (78.8%)** |
| **WP** | 13 (12.5%) | 17 (16.3%) | 18 (17.3%) |
| **NF** | 45 (43.3%) | 4 (3.8%) | 4 (3.8%) |
| **IM** | 35 (33.7%) | 2 (1.9%) | **0 (0%)** |
| **IA** | 4 (3.8%) | 0 (0%) | 0 (0%) |
| **CM** | 2 (1.9%) | **0 (0%)** | **0 (0%)** |

## Key Findings

1. **MCP-DBLP vs Web Search:** 16x improvement in perfect matches (81-82 vs 5)
2. **NF Reduction:** 91% fewer not-found errors (4 vs 45)
3. **Metadata Quality:** Both V2 and V3 have **0 CM** (corrupted metadata)
4. **V3 vs V2:** V3 slightly better (+1 PM, -2 IM) but +1 WP

## Category Definitions

| Code | Category | Definition |
|------|----------|------------|
| PM | Perfect Match | Correct paper with complete metadata |
| WP | Wrong Paper | Different paper than ground truth |
| NF | Not Found | Entry missing or explicit NOT FOUND |
| IM | Incomplete Metadata | Correct paper, missing DOI/pages/venue |
| IA | Incomplete Author | Correct paper, truncated/unknown authors |
| CM | Corrupted Metadata | Correct paper, wrong values (typos, wrong DOI) |

## Methodology

- 9 parallel analyses (3 groups x 3 batches)
- Each batch analyzed by Gemini Flash with ground truth BibTeX
- Per-citation classifications stored in CSV
- Raw counts verified with awk

## Data Files

- `gemini_flash_analysis_2025-11-21_v2.csv` - Per-citation classifications (104 rows)
- This file - Summary with methodology
