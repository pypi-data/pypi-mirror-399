# Evaluate Results: LLM as Judge

## Task

Compare control and treatment BibTeX outputs against ground truth and produce an evaluation report.

## Inputs

- Ground truth: `/Users/szeider/git/mcp-dblp/evaluation/data/ground_truth.bib`
- Control output: `/Users/szeider/git/mcp-dblp/evaluation/data/control_output.bib`
- Treatment output: `/Users/szeider/git/mcp-dblp/evaluation/data/treatment_output.bib`

## Evaluation Criteria

For each entry, compare against ground truth on:

1. **Authors**: Exact match (all authors, correct order, correct spelling)
2. **Title**: Exact match (ignoring case)
3. **Venue**: Correct venue/journal name
4. **Year**: Correct year
5. **DOI**: Correct DOI (if present)

## Scoring

For each criterion:
- **Correct**: Exact match with ground truth
- **Minor error**: Small differences (e.g., venue abbreviation, author initials vs full names)
- **Major error**: Wrong value (wrong year, wrong author, etc.)
- **Missing**: Field not present
- **Fabrication**: Entry doesn't match any ground truth entry

## Output Format

Create a detailed markdown report saved to: `/Users/szeider/git/mcp-dblp/evaluation/data/evaluation_results.md`

Include:

1. **Summary Table**: Accuracy by criterion (Control vs Treatment)
2. **Per-Entry Analysis**: Detailed breakdown for each of the 10 citations
3. **Error Analysis**: Categorize and count error types
4. **Conclusion**: Which approach performed better and why

## Important

- Be objective and precise
- Show specific examples of errors
- Calculate accuracy percentages
- Identify patterns in errors (e.g., does control group fabricate more?)
