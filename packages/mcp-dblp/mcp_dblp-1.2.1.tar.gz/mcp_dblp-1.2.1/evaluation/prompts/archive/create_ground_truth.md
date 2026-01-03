# Create Ground Truth

## Task

Use MCP-DBLP to systematically sample 50 verified BibTeX entries from DBLP using deterministic, reproducible queries.

## Systematic Sampling Strategy

**CRITICAL: DO NOT choose papers based on your memory or familiarity. Use systematic sampling from specific DBLP queries.**

**NOTE: Venue-specific searches are unreliable in DBLP. Instead, use topic-based searches with year filters and take systematic result indices.**

Execute the following queries and take specific result indices (this ensures reproducibility and removes LLM bias):

### Temporal Distribution Strategy

To avoid recency bias and test realistic citation patterns, sample across 20 years (2005-2024):
- **2022-2024** (recent): 10 papers
- **2019-2021** (mid-recent): 10 papers
- **2016-2018** (mid-range): 10 papers
- **2013-2015** (older): 10 papers
- **2010-2012** (classic): 10 papers
- **2005-2009** (older classic): 10 papers

### Topic-Based Queries (60 papers total)

**Period 1: 2022-2024 (10 papers)**
1. Search "machine learning year:2024", take results #1, #10, #20
2. Search "neural networks year:2023", take results #5, #15, #25
3. Search "satisfiability year:2022", take results #3, #8, #12, #18

**Period 2: 2019-2021 (10 papers)**
4. Search "deep learning year:2021", take results #2, #12, #22
5. Search "constraint programming year:2020", take results #4, #14
6. Search "automated reasoning year:2019", take results #1, #6, #11, #16, #21

**Period 3: 2016-2018 (10 papers)**
7. Search "artificial intelligence year:2018", take results #3, #13, #23
8. Search "logic year:2017", take results #5, #15, #25
9. Search "optimization year:2016", take results #2, #7, #12, #17

**Period 4: 2013-2015 (10 papers)**
10. Search "theorem proving year:2015", take results #1, #9, #18
11. Search "algorithms year:2014", take results #4, #14, #24
12. Search "verification year:2013", take results #2, #6, #10, #14

**Period 5: 2010-2012 (10 papers)**
13. Search "knowledge representation year:2012", take results #3, #13, #23
14. Search "planning year:2011", take results #5, #15, #25
15. Search "search year:2010", take results #1, #8, #16, #21

**Period 6: 2005-2009 (10 papers)**
16. Search "reasoning year:2009", take results #2, #12, #22
17. Search "SAT solver year:2008", take results #4, #14, #24
18. Search "model checking year:2007", take results #1, #6, #11
19. Search "heuristics year:2006", take results #3, #13

## Requirements

- Use `mcp__mcp-dblp__search` with exact venue and year filters
- Use `mcp__mcp-dblp__export_bibtex` to get verified BibTeX entries
- Take the EXACT result indices specified (e.g., #1 = first result, #5 = fifth result)
- If a query returns fewer results than needed, skip those indices and note it
- Use parallel/batch tool calls for efficiency
- Save output to: `/Users/szeider/git/mcp-dblp/evaluation/data/ground_truth.bib`

## Output

A single .bib file containing up to 50 BibTeX entries with citation keys in format: FirstAuthorSurname2023 (first author surname + year).

**Also create a metadata file** `/Users/szeider/git/mcp-dblp/evaluation/data/ground_truth_metadata.txt` listing:
- Which query each paper came from
- The result index used
- Total papers successfully retrieved

---

# MCP-DBLP Instructions

You have access to MCP-DBLP tools. Follow these guidelines:

## Search Strategy

**For most reliable results, use author name + year in your query:**
- ✅ Good: `search("Vaswani 2017")` or `search("author:Vaswani year:2017")`
- ✅ Good: `search("Attention is All You Need Vaswani")`

## Available Tools

1. **search**: Search DBLP for publications using boolean queries
   - Parameters: query (required), max_results, year_from, year_to, venue_filter, include_bibtex
2. **fuzzy_title_search**: Search publications with fuzzy title matching
   - Parameters: title (required), similarity_threshold (required), max_results, year_from, year_to, venue_filter, include_bibtex
3. **get_author_publications**: Retrieve publications for a specific author
   - Parameters: author_name (required), similarity_threshold (required), max_results, include_bibtex
4. **export_bibtex**: Export BibTeX entries from HTML links into a file
   - Parameters: links (required) - HTML string containing `<a href=biburl>key</a>` links
   - Returns the path to the saved .bib file

## Efficiency: Use Parallel Tool Calls

✅ **DO THIS** (Efficient - Single Request):
Make parallel calls in one request:
- search(query="author:Smith year:2023")
- search(query="author:Jones year:2022")
- get_author_publications(author_name="McKay", similarity_threshold=0.8)

❌ **DON'T DO THIS** (Inefficient):
Make sequential calls one at a time.
