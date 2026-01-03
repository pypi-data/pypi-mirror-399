# Third Experiment: MCP-DBLP Evaluation

This folder contains all materials needed to run the third evaluation experiment.

## Directory Structure

```
third/
├── README.md                          # This file
├── inputs/                            # Citation input files
│   ├── test_input_v2_batch1.txt       # Citations 1-35
│   ├── test_input_v2_batch2.txt       # Citations 36-70
│   └── test_input_v2_batch3.txt       # Citations 71-104
├── prompts/                           # All prompts
│   ├── prompt_web.md                  # Control group (web search only)
│   ├── prompt_mcp_m.md                # MCP-M (mediated - manual BibTeX)
│   ├── prompt_mcp_u.md                # MCP-U (unmediated - direct export)
│   ├── instructions_mcp_m.md          # Detailed instructions for MCP-M
│   └── classification_prompt.md       # Classification criteria with examples
├── results_control/                   # Web group outputs (batch1.bib, batch2.bib, batch3.bib)
├── results_mcp_m/                     # MCP-M outputs
└── results_mcp_u/                     # MCP-U outputs
```

## Experiment Procedure

### Phase 1: Control Group (Web Search Only)

**Setup:** Disable mcp-dblp using `/mcp` command

Run 3 batches SERIALLY (one at a time):

```
Batch 1:
- Input: inputs/test_input_v2_batch1.txt (citations 1-35)
- Output: results_control/batch1.bib
- Prompt: prompts/prompt_web.md

Batch 2:
- Input: inputs/test_input_v2_batch2.txt (citations 36-70)
- Output: results_control/batch2.bib

Batch 3:
- Input: inputs/test_input_v2_batch3.txt (citations 71-104)
- Output: results_control/batch3.bib
```

### Phase 2: MCP-M Group (Mediated)

**Setup:** Enable mcp-dblp using `/mcp` command

Run 3 batches SERIALLY:

```
Batch 1:
- Input: inputs/test_input_v2_batch1.txt
- Output: results_mcp_m/batch1.bib
- Prompt: prompts/prompt_mcp_m.md
- Instructions: Include prompts/instructions_mcp_m.md in the prompt

Batch 2:
- Input: inputs/test_input_v2_batch2.txt
- Output: results_mcp_m/batch2.bib

Batch 3:
- Input: inputs/test_input_v2_batch3.txt
- Output: results_mcp_m/batch3.bib
```

### Phase 3: MCP-U Group (Unmediated)

**Setup:** mcp-dblp must be enabled

Run 3 batches SERIALLY:

```
Batch 1:
- Input: inputs/test_input_v2_batch1.txt
- Output: results_mcp_u/batch1.bib
- Prompt: prompts/prompt_mcp_u.md
- Note: Agent should read dblp://instructions MCP resource

Batch 2:
- Input: inputs/test_input_v2_batch2.txt
- Output: results_mcp_u/batch2.bib

Batch 3:
- Input: inputs/test_input_v2_batch3.txt
- Output: results_mcp_u/batch3.bib
```

### Phase 4: Classification

Compare all outputs against ground truth using Gemini Flash with the classification prompt.

**Ground truth location:** `/Users/szeider/git/mcp-dblp/evaluation/ground_truth/ground_truth.bib`

Run classification TWICE in parallel for consistency check, then consolidate any differences.

```
Files to analyze:
- ground_truth/ground_truth.bib
- results_control/batch1.bib, batch2.bib, batch3.bib
- results_mcp_m/batch1.bib, batch2.bib, batch3.bib
- results_mcp_u/batch1.bib, batch2.bib, batch3.bib

Classification prompt: prompts/classification_prompt.md
```

## Subagent Prompts

### For Control (Web) Batches:

```
# Control Group Batch N: Generate BibTeX using Web Search Only

**IMPORTANT: Do NOT use any mcp-dblp tools. They are disabled. Use web search only.**

Read the prompt from: /Users/szeider/git/mcp-dblp/evaluation/third/prompts/prompt_web.md

## Input
Read citations from: /Users/szeider/git/mcp-dblp/evaluation/third/inputs/test_input_v2_batchN.txt

## Output
Save ALL BibTeX entries to: /Users/szeider/git/mcp-dblp/evaluation/third/results_control/batchN.bib

Report: found vs not found count, list not found citations, confirm output path
```

### For MCP-M Batches:

```
# MCP-M Batch N: Generate BibTeX using MCP-DBLP Search + Manual Construction

Read the instructions from: /Users/szeider/git/mcp-dblp/evaluation/third/prompts/instructions_mcp_m.md

**IMPORTANT:** Use MCP-DBLP search tools, but construct BibTeX MANUALLY. Do NOT use add_bibtex_entry or export_bibtex.

## Input
Read citations from: /Users/szeider/git/mcp-dblp/evaluation/third/inputs/test_input_v2_batchN.txt

## Output
Save ALL BibTeX entries to: /Users/szeider/git/mcp-dblp/evaluation/third/results_mcp_m/batchN.bib

Report: found vs not found count, list not found citations, confirm output path
```

### For MCP-U Batches:

```
# MCP-U Batch N: Generate BibTeX with Unmediated Export

**Important:** Before starting, read the MCP resource `dblp://instructions` from the mcp-dblp server.

## Task
Use MCP-DBLP tools with unmediated export (add_bibtex_entry + export_bibtex).

## Instructions
1. Read the MCP resource `dblp://instructions`
2. Follow the workflow described there exactly
3. If a paper is not found, note it in your report

## Input
Read citations from: /Users/szeider/git/mcp-dblp/evaluation/third/inputs/test_input_v2_batchN.txt

## Output
After export_bibtex creates the .bib file, copy it to:
/Users/szeider/git/mcp-dblp/evaluation/third/results_mcp_u/batchN.bib

Report: found vs not found count, exported file path, list not found citations
```

## Classification Categories

| Code | Category | Definition |
|------|----------|------------|
| PM | Perfect Match | Correct paper with complete metadata |
| WP | Wrong Paper | Different paper than ground truth |
| NF | Not Found | Entry missing or explicit NOT FOUND |
| IM | Incomplete Metadata | Correct paper, missing fields or abbreviated names |
| IA | Incomplete Author | Correct paper, truncated author list |
| CM | Corrupted Metadata | Correct paper, WRONG values (name, year, DOI, pages) |
| UK | Unknown | Needs manual verification |

See `prompts/classification_prompt.md` for detailed examples and edge cases.

## Expected Results (from Second Experiment)

| Category | Web | MCP-M | MCP-U |
|----------|-----|-------|-------|
| PM | ~24% | ~77% | ~84% |
| WP | ~24% | ~19% | ~14% |
| NF | ~22% | ~3% | ~0% |
| IM | ~21% | ~1% | ~2% |
| IA | ~3% | 0% | 0% |
| CM | ~6% | 0% | 0% |
