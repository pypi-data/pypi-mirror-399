# Experiment Prompts

This directory contains the prompts used for the MCP-DBLP evaluation experiment.

## Active Prompts

### `control_group.md`
Instructions for generating BibTeX using only web search (no MCP-DBLP tools).
Simulates a researcher using an LLM without MCP-DBLP access.

### `treatment_group.md`
Instructions for generating BibTeX using MCP-DBLP tools.
**IMPORTANT**: This prompt instructs the agent to read the official MCP-DBLP instructions from the MCP server resource (`dblp://instructions`) before starting work.

### `evaluate_v2.md`
Two-stage evaluation methodology:
- Stage 1: Paper matching accuracy
- Stage 2: Metadata fidelity (for correctly matched papers)

## Archived Prompts

The `archive/` directory contains prompts used for setup steps (ground truth collection, test input creation) and old evaluation versions.

## Usage

When launching subagents for the experiment:

**Control Group (Batch N):**
```
Use Task tool with:
- Prompt: Contents of control_group.md + specific citations + output file path
- Constraint: NO mcp__mcp-dblp__* tools
```

**Treatment Group (Batch N):**
```
Use Task tool with:
- Prompt: Contents of treatment_group.md + specific citations + output file path
- The subagent will read dblp://instructions resource as instructed
```

## Reproducibility

All prompts are version-controlled markdown files that can be referenced in the paper's methodology section. The treatment group's reliance on the official MCP-DBLP instructions resource ensures that the experiment reflects real-world usage patterns.
