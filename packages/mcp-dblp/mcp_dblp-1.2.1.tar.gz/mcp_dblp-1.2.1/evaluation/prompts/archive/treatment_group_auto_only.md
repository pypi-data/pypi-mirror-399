# Treatment Group: Generate BibTeX with MCP-DBLP (Auto-Export Only)

**Setup:** Ensure the mcp-dblp server is enabled (use `/mcp` command if needed).

**Note:** This prompt should be executed using the `general-purpose` subagent type.

**Important:** Before starting, read the MCP resource `dblp://instructions` from the mcp-dblp server which contains detailed guidance on using the DBLP tools, including how to use the `export_bibtex` tool with HTML links.

## Task

Given informal citations, find papers using MCP-DBLP tools and export them using the export_bibtex tool.

## Input

Read citations from: `/Users/szeider/git/mcp-dblp/evaluation/data/test_input_v2_batch1.txt`

## Instructions

For each citation:
1. Use MCP-DBLP search tools to find the paper
2. **CRITICAL:** Record the DBLP key EXACTLY as returned by the search (e.g., `journals/algorithms/HammadZOG25`)
   - Copy the key character-by-character from the search result
   - Do NOT modify, abbreviate, or reconstruct the key
   - Even small typos will cause export to fail

After searching all citations:
3. Use `mcp__mcp-dblp__export_bibtex` tool to export ALL found papers at once
   - Construct HTML links using the EXACT DBLP keys you recorded
   - Format: `<a href=https://dblp.org/rec/{EXACT_KEY}.bib>CitationKey</a>`
   - Double-check each key before calling export_bibtex
4. Report which citations were not found

## Output

The `export_bibtex` tool will automatically create a timestamped .bib file in the export directory.

Report to the user:
- How many papers were found
- Which citations were NOT FOUND
- The path to the exported file
