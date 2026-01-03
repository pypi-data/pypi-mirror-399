# Control Group (Web): Generate BibTeX without MCP-DBLP

**Setup:** Before running, disable the mcp-dblp server using `/mcp` command.

## Task

Given informal citations, generate a complete BibTeX file by searching the web for paper information. Do NOT use any MCP-DBLP tools.

## Instructions

For each citation:
1. Use web search to find the paper on DBLP (dblp.org) or other academic sources
2. Extract publication details: authors (FULL names), title, venue/journal, year, pages, DOI
3. Construct a proper BibTeX entry (@article, @inproceedings, etc.)
4. Use citation key format: FirstAuthorLastNameYEAR (e.g., Smith2023)
5. Include DOI field if available
6. If you cannot find a paper, include: `% NOT FOUND: [original citation text]`

## Important Notes

- Use FULL author names (e.g., "John Smith" not "J. Smith")
- Verify metadata accuracy - don't guess or fabricate values
- If uncertain about a value, omit it rather than guess

## Input

Read citations from the specified batch file in `inputs/` folder.

## Output

Save all BibTeX entries to the specified output file in `results_control/` folder.

**Report back:**
- Number of citations found vs not found
- List any citations that could not be found
- Confirm the output file path
