# Treatment Group A: Generate BibTeX with MCP-DBLP (Manual Save)

**Setup:** Ensure the mcp-dblp server is enabled (use `/mcp` command if needed).

**Note:** This prompt should be executed using the `general-purpose` subagent type.

## Task

Given informal citations, generate a complete BibTeX file using MCP-DBLP tools and manually save to file.

## Input

Read citations from: `/Users/szeider/git/mcp-dblp/evaluation/data/test_input_v2.txt`

## Instructions

For each citation:
1. Use MCP-DBLP search tools to find the paper
2. Find publication details (authors, title, venue, year, DOI, etc.)
3. Collect DBLP URLs for all found papers
4. Use `mcp__mcp-dblp__export_bibtex` to generate BibTeX entries (returns BibTeX as text)
5. Manually save the returned BibTeX entries to the output file
6. If you cannot find a paper, include a comment: `% NOT FOUND: [citation]`

## Output

Save all BibTeX entries to: `/Users/szeider/git/mcp-dblp/evaluation/data/treatment_output_v2_manual.bib`
