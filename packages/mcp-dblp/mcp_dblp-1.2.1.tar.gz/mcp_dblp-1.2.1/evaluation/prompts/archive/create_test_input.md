# Create Test Input

## Task

Read the ground truth BibTeX file and create obfuscated/informal citation text that a researcher might naturally write.

## Input

- File: `/Users/szeider/git/mcp-dblp/evaluation/data/ground_truth.bib`

## Requirements

For each BibTeX entry, create an informal citation with difficulty matching the original selection:

- **Easy**: "Author et al. YEAR" or "Author YEAR"
- **Medium**: "Author's paper on TOPIC from YEAR" or "TOPIC paper by Author"
- **Hard**: "Author venue'YY" (e.g., "Brown neurips'20") or partial title
- **Very Hard**: "That TOPIC paper by Author" or very vague descriptions

## Output Format

Create a simple numbered list:

```
1. Vaswani et al. 2017
2. Devlin's paper on BERT from 2018
3. Brown neurips'20
...
```

Save to: `/Users/szeider/git/mcp-dblp/evaluation/data/test_input.txt`

## Important

- Do NOT include full titles, DOIs, or other identifying information that makes lookup trivial
- Make it realistic - how researchers actually cite informally in draft text
- Ensure difficulty varies as intended
