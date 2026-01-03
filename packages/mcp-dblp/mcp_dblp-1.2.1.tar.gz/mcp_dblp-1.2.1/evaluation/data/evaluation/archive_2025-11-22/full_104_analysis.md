# Full 104-Citation Analysis Results

**Date:** 2025-11-21
**Analyst:** Claude Sonnet 4.5 via consult7
**Method:** Line-by-line comparison of all output BibTeX files against ground_truth.bib

## Input Files Analyzed

**Ground Truth:**
- `/evaluation/ground_truth/ground_truth.bib` (104 entries)

**Control Group (Web-Search):**
- `results_control/control_output_v2_batch1.bib`
- `results_control/control_output_v2_batch2.bib`
- `results_control/control_output_v2_batch3.bib`

**Treatment V2 (MCP-DBLP-M, mediated export):**
- `results_treatment_v2/treatment_output_v2_batch1.bib`
- `results_treatment_v2/treatment_output_v2_batch2.bib`
- `results_treatment_v2/treatment_output_v2_batch3.bib`

**Treatment V3 (MCP-DBLP-U, unmediated export):**
- `results_treatment_v3/treatment_output_v3_batch1.bib`
- `results_treatment_v3/treatment_output_v3_batch2.bib`
- `results_treatment_v3/treatment_output_v3_batch3.bib`

## Error Classification Framework

| Code | Category | Definition |
|------|----------|------------|
| PM | Perfect Match | Entry matches ground truth exactly (same paper, complete metadata) |
| WP | Wrong Paper | Found a different paper than ground truth |
| NF | Not Found | Entry missing or has "NOT FOUND" comment |
| IM | Incomplete Metadata | Correct paper but missing DOI/pages/venue |
| IA | Incomplete Author | Correct paper but "Author Unknown" or truncated authors |
| CM | Corrupted Metadata | Correct paper but wrong DOI/pages/venue values |
| FP | Fabricated Paper | Paper doesn't exist |
| FM | Fabricated Metadata | Invented fields |

## Results Summary (All 104 Citations)

| Category | Web-Search | MCP-DBLP-M | MCP-DBLP-U | Description |
|----------|------------|------------|------------|-------------|
| **PM** | 42 | 95 | 92 | Perfect match with ground truth |
| **WP** | 9 | 5 | 8 | Valid paper, ambiguous query |
| **NF** | 47 | 4 | 4 | Failed to locate |
| **IM/IA** | 6 | 0 | 0 | Incomplete metadata or authors |
| **CM/FP/FM** | 0 | 0 | 0 | Corruption or fabrication |
| **Total** | 104 | 104 | 104 | |

## Key Metrics

### Perfect Match Rate
- Web-Search: 42/104 = **40.4%**
- MCP-DBLP-M: 95/104 = **91.3%**
- MCP-DBLP-U: 92/104 = **88.5%**

### Not Found Rate
- Web-Search: 47/104 = **45.2%**
- MCP-DBLP-M: 4/104 = **3.8%**
- MCP-DBLP-U: 4/104 = **3.8%**

### Metadata Corruption Rate (IM + IA + CM + FM)
- Web-Search: 6/104 = **5.8%**
- MCP-DBLP-M: 0/104 = **0%**
- MCP-DBLP-U: 0/104 = **0%**

### Improvement Ratios
- PM improvement: 92/42 = **2.19x** (MCP-DBLP-U vs Web-Search)
- NF reduction: 47 → 4 = **91.5%** reduction
- Metadata corruption elimination: 6 → 0 = **100%** reduction

## Key Findings

1. **MCP-DBLP achieves 2.2x better perfect match rate** (88-91% vs 40%)
2. **Zero metadata corruption** in MCP-DBLP groups vs 6 errors in Web-Search
3. **91% reduction in Not Found errors** (47 to 4)
4. **All MCP-DBLP errors are search failures** (WP, NF), never metadata quality issues
5. **MCP-DBLP-M slightly outperforms MCP-DBLP-U** on perfect matches (95 vs 92), but both eliminate metadata corruption

## Notable Patterns

### Control Group (Web-Search) Errors
- 47 citations not found (45%)
- 6 entries with incomplete metadata (missing authors, "Author Unknown" placeholders)
- 9 wrong papers retrieved (similar author names caused confusion)

### MCP-DBLP Shared Issues
- Citations 12, 13, 15, 23 consistently not found in DBLP
- Some citations retrieved wrong paper due to ambiguous author names

### MCP-DBLP Advantage
- 2.2x better match rate than manual web search
- Eliminated ALL incomplete metadata issues
- More consistent author name handling
- Direct DBLP fetch guarantees metadata accuracy

## Verification

All counts verified by:
1. Comparing each BibTeX entry against ground_truth.bib
2. Checking title, authors, venue, year, DOI for matches
3. Counting NOT FOUND comments in output files
4. Cross-checking totals (each group = 104 citations)

---

**Generated:** 2025-11-21
**Source:** consult7 analysis with anthropic/claude-sonnet-4.5 (thinking mode)
