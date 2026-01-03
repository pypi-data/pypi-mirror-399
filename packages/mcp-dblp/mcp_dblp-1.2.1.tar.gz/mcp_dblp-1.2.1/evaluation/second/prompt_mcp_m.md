# Treatment Group MCP-M: Generate BibTeX with MCP-DBLP (Mediated)

**Setup:** Ensure the mcp-dblp server is enabled.

**Important:** Before starting, read the MCP resource `dblp://instructions` from the mcp-dblp server which contains detailed guidance on using the DBLP tools.

## Task

Given informal citations, generate a complete BibTeX file using MCP-DBLP search tools, but construct BibTeX entries manually.

## Instructions

1. Read the MCP resource `dblp://instructions` first
2. For each citation, use MCP-DBLP search tools to find the paper
3. From search results, extract metadata and **manually construct** BibTeX entries
4. **Do NOT use add_bibtex_entry or export_bibtex tools** - write BibTeX yourself
5. Use citation key format: FirstAuthorLastNameYEAR
6. If not found: `% NOT FOUND: [citation]`

## Output

Report:
- Number of citations found vs not found
- List any citations that could not be found
- Confirm the output file path
