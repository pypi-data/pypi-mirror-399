# Treatment Group: Generate BibTeX with MCP-DBLP

**Setup:** Ensure the mcp-dblp server is enabled (use `/mcp` command if needed).

**Note:** This prompt should be executed using the `general-purpose` subagent type.

**Important:** Before starting, read the MCP resource `dblp://instructions` from the mcp-dblp server which contains detailed guidance on using the DBLP tools.

## Task

Given informal citations, generate a complete BibTeX file using MCP-DBLP tools.

## Input

Read citations from: `/Users/szeider/git/mcp-dblp/evaluation/data/test_input_v2_batch1.txt`

## Instructions

1. For each citation, use MCP-DBLP search tools to find the paper on DBLP
2. For each found paper, use `add_bibtex_entry` to add it to the collection
3. After processing all citations, use `export_bibtex` to export the collection

## Output

Report:
- How many citations were found vs not found
- The filepath of the exported .bib file
- List any citations that could not be found on DBLP
