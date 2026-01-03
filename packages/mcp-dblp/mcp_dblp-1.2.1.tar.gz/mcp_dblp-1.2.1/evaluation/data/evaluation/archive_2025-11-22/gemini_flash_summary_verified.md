# Verified Evaluation Results

**Date:** 2025-11-22
**Model:** google/gemini-2.5-flash (think mode for control)
**Total citations:** 104
**Methodology:** Control group re-analyzed with explicit criteria and manual verification

## Final Verified Results

| Category | Control | V2 (Mediated) | V3 (Unmediated) |
|----------|---------|---------------|-----------------|
| **PM** | 6 (5.8%) | 81 (77.9%) | 82 (78.8%) |
| **WP** | 12 (11.5%) | 17 (16.3%) | 18 (17.3%) |
| **NF** | 46 (44.2%) | 4 (3.8%) | 4 (3.8%) |
| **IM** | 24 (23.1%) | 2 (1.9%) | 0 (0%) |
| **IA** | 10 (9.6%) | 0 (0%) | 0 (0%) |
| **CM** | 6 (5.8%) | 0 (0%) | 0 (0%) |

## Classification Criteria (Strict)

| Code | Definition | Examples |
|------|------------|----------|
| **PM** | Same paper, all core fields match | Title, full author names, year, venue, volume, pages |
| **WP** | Different paper | Different title, different primary authors, different venue type |
| **NF** | Not found | Explicit "NOT FOUND" marker or entry missing |
| **IM** | Same paper, missing fields | Missing DOI, URL, pages; abbreviated author names (J. Smith) |
| **IA** | Same paper, author problems | "Author Unknown", "and others", missing authors |
| **CM** | Same paper, wrong values | Wrong year, wrong DOI, wrong journal name, wrong pages |

## Control Group CM Details (6 citations)

| Citation | Issue | GT Value | Control Value |
|----------|-------|----------|---------------|
| 5 | Wrong DOI | s10586-025-05713-2 | s10878-025-01285-4 |
| 38 | Wrong pages | 18-28 | 545-557 |
| 49 | Wrong journal | Intelligent Decision Tech | J. Supercomputing |
| 66 | Wrong year | 2024 | 2025 |
| 67 | Wrong issue number | 2 | CoLIS |
| 94 | Wrong DOI | 3172789 | 3172801 |

## Key Findings

1. **MCP-DBLP vs Web Search:** 13x improvement in perfect matches (81-82 vs 6)
2. **NF Reduction:** 91% fewer not-found errors (4 vs 46)
3. **Metadata Quality:**
   - Control: 6 CM (5.8%) - corrupted metadata
   - MCP-DBLP: 0 CM (0%) - no corruption
4. **Author Issues:**
   - Control: 10 IA (9.6%) - truncated/missing authors
   - MCP-DBLP: 0 IA (0%) - complete author lists

## Files

- `control_group_verified.csv` - Control group with reasons (104 rows)
- `gemini_flash_analysis_consolidated.csv` - Three-way comparison
- This file - Verified summary

## Verification Process

1. Ran Gemini Flash with explicit classification rules
2. Manually verified all CM classifications against source BibTeX
3. Manually verified all PM classifications
4. Confirmed WP by comparing titles/authors
5. NF verified by "NOT FOUND" markers in control output
