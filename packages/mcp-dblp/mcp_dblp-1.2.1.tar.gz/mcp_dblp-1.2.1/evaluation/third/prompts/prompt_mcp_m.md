# Treatment Group MCP-M (Mediated): Generate BibTeX with MCP-DBLP Search + Manual Construction

**Setup:** Ensure the mcp-dblp server is enabled.

## Task

Given informal citations, generate a complete BibTeX file using MCP-DBLP search tools, but construct BibTeX entries MANUALLY from the search results.

**IMPORTANT:** Do NOT use `add_bibtex_entry` or `export_bibtex` tools. Manually construct BibTeX from search result metadata.

## Instructions

1. For each citation, use MCP-DBLP search tools to find the paper
2. From search results, extract metadata (authors, title, venue, year, pages, DOI)
3. **Manually construct** a proper BibTeX entry from this metadata
4. Use citation key format: FirstAuthorLastNameYEAR (e.g., Smith2023)
5. If you cannot find a paper, include: `% NOT FOUND: [original citation text]`

## Search Strategy

**Best practice - use author name + year:**
- Good: `search("Vaswani 2017")` or `search("author:Vaswani year:2017")`
- Less reliable: `search("Attention is All You Need")` alone

**Progressive search:**
1. Start with author + year
2. Add title keywords
3. Try fuzzy_title_search if you know the exact title
4. Use get_author_publications for specific authors

**USE PARALLEL SEARCHES:** Search for 5-10 papers in parallel per request for efficiency.

## Available Tools

- `mcp__mcp-dblp__search`: Search DBLP (query, max_results, year_from, year_to)
- `mcp__mcp-dblp__fuzzy_title_search`: Fuzzy title matching (title, similarity_threshold)
- `mcp__mcp-dblp__get_author_publications`: Get author's papers (author_name, similarity_threshold)

## BibTeX Construction

From search results, construct entries like:
```bibtex
@article{Smith2023,
  author    = {John Smith and Jane Doe},
  title     = {Paper Title Here},
  journal   = {Journal Name},
  volume    = {10},
  number    = {2},
  pages     = {1--20},
  year      = {2023},
  doi       = {10.1234/example}
}
```

## Input

Read citations from the specified batch file in `inputs/` folder.

## Output

Save all BibTeX entries to the specified output file in `results_mcp_m/` folder.

**Report back:**
- Number of citations found vs not found
- List any citations that could not be found
- Confirm the output file path
