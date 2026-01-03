# Control Group: Generate BibTeX without MCP-DBLP

**Setup:** Before running this task, disable the mcp-dblp server using `/mcp` command.

**Note:** This prompt should be executed using the `general-purpose` subagent type.

## Task

Given informal citations, generate a complete BibTeX file by searching DBLP for paper information.

## Input

Read citations from: `/Users/szeider/git/mcp-dblp/evaluation/data/test_input.txt`

## Instructions

For each citation:
1. Search DBLP to find the paper
2. Find publication details (authors, title, venue, year, DOI, etc.)
3. Construct a BibTeX entry from the found information
4. Use citation keys in format: FirstAuthorLastNameYEAR (e.g., Smith2023)
5. Include DOI field if available
6. If you cannot find a paper, include a comment: `% NOT FOUND: [citation]`

## Output

Save all BibTeX entries to: `/Users/szeider/git/mcp-dblp/evaluation/data/control_output_v2.bib`
