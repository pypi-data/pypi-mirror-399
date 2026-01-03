# Supplementary Materials: MCP-DBLP Evaluation

## Overview

This folder contains complete, self-contained data for replicating the MCP-DBLP evaluation experiment comparing three bibliography retrieval methods:

- **Web**: Web search baseline (MCP-DBLP disabled)
- **MCP-M**: MCP-DBLP search + manual BibTeX construction
- **MCP-U**: MCP-DBLP search + direct BibTeX export (unmediated)

**Experiments:** 3 independent runs
**Citations per experiment:** 104

---

## Directory Structure

```
SUPP/
├── README.md
├── ground_truth/
│   └── ground_truth.bib
├── inputs/
│   ├── batch1.txt
│   ├── batch2.txt
│   └── batch3.txt
├── results/
│   ├── exp1/{web,mcp_m,mcp_u}/batch{1,2,3}.bib
│   ├── exp2/{web,mcp_m,mcp_u}/batch{1,2,3}.bib
│   └── exp3/{web,mcp_m,mcp_u}/batch{1,2,3}.bib
└── classifications/
    ├── exp1.csv
    ├── exp2.csv
    ├── exp3.csv
    └── averaged.csv
```

---

## Summary (Averaged Across 3 Experiments)

| Category | Web | MCP-M | MCP-U |
|----------|-----|-------|-------|
| PM | 29.3 | 49.0 | 86.0 |
| WP | 19.3 | 15.7 | 16.3 |
| NF | 31.3 | 1.3 | 1.7 |
| IM | 12.3 | 38.0 | 0.0 |
| IA | 4.7 | 0.0 | 0.0 |
| CM | 7.0 | 0.0 | 0.0 |

---

## Individual Experiment Results

### Experiment 1

| Category | Web | MCP-M | MCP-U |
|----------|-----|-------|-------|
| PM | 26 | 36 | 83 |
| WP | 7 | 20 | 18 |
| NF | 46 | 2 | 3 |
| IM | 17 | 46 | 0 |
| IA | 5 | 0 | 0 |
| CM | 3 | 0 | 0 |

### Experiment 2

| Category | Web | MCP-M | MCP-U |
|----------|-----|-------|-------|
| PM | 36 | 76 | 89 |
| WP | 25 | 10 | 15 |
| NF | 24 | 1 | 0 |
| IM | 10 | 17 | 0 |
| IA | 1 | 0 | 0 |
| CM | 8 | 0 | 0 |

### Experiment 3

| Category | Web | MCP-M | MCP-U |
|----------|-----|-------|-------|
| PM | 26 | 35 | 86 |
| WP | 26 | 17 | 16 |
| NF | 24 | 1 | 2 |
| IM | 10 | 51 | 0 |
| IA | 8 | 0 | 0 |
| CM | 10 | 0 | 0 |

---

## Classification Criteria

| Code | Definition |
|------|------------|
| PM | Perfect Match - correct paper, all core fields correct |
| WP | Wrong Paper - different paper than ground truth |
| NF | Not Found - entry missing or marked NOT FOUND |
| IM | Incomplete Metadata - missing doi/pages/volume or abbreviated names |
| IA | Incomplete Authors - truncated author list |
| CM | Corrupted Metadata - wrong values (not missing) |

---

## Methodology

1. **Ground Truth:** 104 papers sampled from DBLP with stratified sampling (50% 2020-2025, 25% 2015-2019, 25% 2010-2014)

2. **Input Generation:** Obfuscated citations with varying difficulty levels

3. **Execution:** Claude agent (Sonnet 4.5) for each method

4. **MCP-DPLP version:** 1.2.0
