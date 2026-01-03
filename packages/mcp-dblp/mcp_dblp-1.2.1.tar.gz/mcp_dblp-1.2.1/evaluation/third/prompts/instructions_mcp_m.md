# DBLP Citation Processor Instructions (MCP-M: Mediated)

You are given a list of informal citations. Your task is to find each paper on DBLP and manually construct BibTeX entries from the search results.

## Your Task

1. Search for each citation using MCP-DBLP tools to get its DBLP entry
2. From the search results, extract the metadata (authors, title, venue, year, pages, DOI, etc.)
3. **Manually construct** a proper BibTeX entry from this metadata
4. Save all entries to the output file

## Important Requirements

- Use ONLY the MCP-DBLP search tools to find entries
- **USE BATCH/PARALLEL CALLS FOR SEARCHES**: When you have multiple citations to search, make parallel search calls in a SINGLE request. This is much more efficient.
  - Example: Search for 5-10 different papers in one request with parallel search calls
- From the search results, **manually construct** BibTeX entries with proper formatting
- Use citation key format: FirstAuthorLastNameYEAR (e.g., Smith2023)
- Ensure all keys remain unique
- If you cannot find a paper, include: `% NOT FOUND: [original citation]`

## Search Strategy

### Best Practices for Finding Papers

**For most reliable results, use author name + year in your query:**
- Good: `search("Vaswani 2017")` or `search("author:Vaswani year:2017")`
- Good: `search("Attention is All You Need Vaswani")`
- Less reliable: `search("Attention is All You Need")` (may return derivative papers first)

**Why this matters:** DBLP's search ranking doesn't always prioritize the original paper when searching by title alone. Adding author name or year dramatically improves result quality.

### Progressive Search Strategy

When searching for citations, use this progression:

1. **Start with author + year**: `search("Smith 2023")` or `search("author:Smith year:2023")`
2. **Add title keywords**: `search("Smith transformer 2023")`
3. **Try fuzzy_title_search**: If you know the exact title, use `fuzzy_title_search("Attention is All You Need", similarity_threshold=0.7)`
4. **Use get_author_publications**: For specific authors, `get_author_publications("Yoshua Bengio", similarity_threshold=0.8)`
5. **Try different name formats**: Try full name, last name only, or name variations

### Tool Selection Guide

- **search()**: Best for author+year, keywords, or general queries. Supports boolean operators (AND, OR)
- **fuzzy_title_search()**: Use when you have the exact title
- **get_author_publications()**: Best for retrieving all papers by a specific author

### When to Give Up

Only mark a citation as NOT FOUND after attempting at least 2-3 different search queries with varying levels of specificity.

## Available Tools

1. **search**: Search DBLP for publications using boolean queries
   - Parameters: query (required), max_results, year_from, year_to, venue_filter
2. **fuzzy_title_search**: Search publications with fuzzy title matching
   - Parameters: title (required), similarity_threshold (required), max_results, year_from, year_to
3. **get_author_publications**: Retrieve publications for a specific author
   - Parameters: author_name (required), similarity_threshold (required), max_results

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

@inproceedings{Jones2024,
  author    = {Bob Jones},
  title     = {Conference Paper Title},
  booktitle = {Proceedings of Conference},
  pages     = {100--110},
  year      = {2024}
}
```

## Efficiency: Use Parallel Search Calls

**IMPORTANT**: Batch multiple search calls in a single request for efficiency.

**DO THIS** (Efficient):
```
Batch your searches in one request:
- search(query="author:Smith year:2023")
- search(query="author:Jones year:2022")
- search(query="author:Lee year:2024")
All execute simultaneously and return together
```

**DON'T DO THIS** (Inefficient):
```
Sequential searches (slow):
1. search(query="author:Smith year:2023"), wait for response
2. search(query="author:Jones year:2022"), wait for response
3. search(query="author:Lee year:2024"), wait for response
```
