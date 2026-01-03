# Treatment Group MCP-U (Unmediated): Generate BibTeX with MCP-DBLP Direct Export

**Setup:** Ensure the mcp-dblp server is enabled.

**Important:** Before starting, read the MCP resource `dblp://instructions` from the mcp-dblp server. It contains detailed guidance on the search strategy and export workflow.

## Task

Given informal citations, generate a complete BibTeX file using MCP-DBLP tools with UNMEDIATED export. This means using `add_bibtex_entry` and `export_bibtex` to get BibTeX directly from DBLP without LLM modification.

## Instructions

1. **First:** Read the MCP resource `dblp://instructions`
2. Follow the workflow described there exactly:
   - Search in parallel (5-10 papers per request)
   - Add entries IMMEDIATELY after each search batch returns
   - Export once at the end
3. If a paper is not found, note it in your report

## Critical Workflow

The `dblp://instructions` resource explains this in detail, but the key points are:

```
1. Search for 5-10 papers in parallel
2. IMMEDIATELY add each result:
   add_bibtex_entry(dblp_key="journals/...", citation_key="Smith2023")
3. Search next batch
4. IMMEDIATELY add those results
5. Repeat until done
6. Call export_bibtex() ONCE at the end
```

## Available Tools

- `mcp__mcp-dblp__search`: Search DBLP
- `mcp__mcp-dblp__fuzzy_title_search`: Fuzzy title matching
- `mcp__mcp-dblp__get_author_publications`: Get author's papers
- `mcp__mcp-dblp__add_bibtex_entry`: Add entry to collection (dblp_key, citation_key)
- `mcp__mcp-dblp__export_bibtex`: Export all collected entries to .bib file

## Input

Read citations from the specified batch file in `inputs/` folder.

## Output

After `export_bibtex` creates the .bib file, copy it to the specified output file in `results_mcp_u/` folder.

**Report back:**
- Number of citations found vs not found
- The filepath of the exported .bib file
- List any citations that could not be found
