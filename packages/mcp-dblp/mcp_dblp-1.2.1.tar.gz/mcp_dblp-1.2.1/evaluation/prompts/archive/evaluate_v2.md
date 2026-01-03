# Evaluate Results (v2): LLM as Judge - Separating Search vs Export Errors

## Task

Compare control and treatment BibTeX outputs against ground truth with **explicit separation of two error types**:
1. **Paper Matching Errors** (search/selection): Did we retrieve the intended paper?
2. **Metadata Export Errors** (serialization/fabrication): Is the BibTeX accurate for the retrieved paper?

## Inputs

- Ground truth: `/Users/szeider/git/mcp-dblp/evaluation/data/ground_truth.bib`
- Control output: `/Users/szeider/git/mcp-dblp/evaluation/data/control_output.bib`
- Treatment output: `/Users/szeider/git/mcp-dblp/evaluation/data/treatment_output.bib`

## Critical Distinction

**MCP-DBLP (Treatment) uses unmediated `export_bibtex`:**
- When Treatment retrieves the wrong paper, the exported BibTeX is still 100% accurate for that (wrong) paper
- Treatment errors are **search/matching errors** only, not export/metadata errors

**WebSearch (Control) generates BibTeX via LLM:**
- Even when finding the correct paper, Control may fabricate or corrupt metadata
- Control errors include both **search errors** AND **metadata fabrication errors**

## Evaluation Criteria

### Stage 1: Paper Matching (Work Selection)

For each entry, determine if the correct paper was retrieved:

1. Compare identifiers (DOI, DBLP key, title+authors+year combination)
2. Classify as:
   - **Correct Match**: Retrieved the intended paper
   - **Wrong-but-Real**: Retrieved a different real paper (not intended)
   - **Fabricated**: Retrieved a non-existent paper (invented details)
   - **Missing**: No entry provided

### Stage 2: Metadata Fidelity (Export Quality)

For entries where a paper was retrieved, evaluate metadata accuracy:

**For Treatment (MCP-DBLP):**
- Compare exported BibTeX against actual DBLP entry for the retrieved paper
- Check if export is exact (100% fidelity expected due to unmediated export)

**For Control (WebSearch):**
- Compare generated BibTeX against ground truth
- Check field-by-field: authors, title, venue, year, DOI, diacritics, formatting

Classify metadata quality:
- **Perfect Fidelity**: Exact match to DBLP
- **Minor Corruption**: Small differences (missing diacritics, venue abbreviations)
- **Major Corruption**: Wrong values (fabricated authors, wrong year)
- **Hallucination**: Invented data not in source

## Output Format

Create a detailed markdown report saved to: `/Users/szeider/git/mcp-dblp/evaluation/data/evaluation_results_v2.md`

### Required Sections

#### 1. Executive Summary
- Key finding: Treatment achieves 100% metadata fidelity vs Control's corruption rate
- Clear statement about error type separation

#### 2. Two-Stage Results

**Table 1: Paper Matching Accuracy (Stage 1)**

| Status | Control | Treatment |
|--------|---------|-----------|
| Correct Match | X/52 | X/52 |
| Wrong-but-Real | X/52 | X/52 |
| Fabricated | X/52 | 0/52 |
| Missing | X/52 | X/52 |

**Table 2: Metadata Fidelity (Stage 2 - Given Paper Retrieved)**

| Metric | Control | Treatment |
|--------|---------|-----------|
| **Perfect Fidelity (all fields exact)** | X% | 100% |
| **Author Accuracy** | X% | 100% |
| **Title Accuracy** | X% | 100% |
| **Venue Accuracy** | X% | 100% |
| **Year Accuracy** | X% | 100% |
| **DOI Accuracy** | X% | 100% |
| **Hallucination/Fabrication Rate** | X% | 0% |

#### 3. Error Type Analysis

**Treatment Errors:**
- List all cases where wrong paper was retrieved
- For each, verify that exported BibTeX is perfect for that (wrong) paper
- State: "Treatment errors are exclusively search/matching failures with 100% export fidelity"

**Control Errors:**
- Separate into:
  - Paper matching errors (wrong/fabricated papers)
  - Metadata corruption errors (right paper, wrong metadata)
- Count hallucinations (fabricated authors, venues, etc.)

#### 4. Safe Failure Analysis

Explain the difference:
- **Treatment's "safe failure"**: Wrong but verifiable entry (real DOI, real DBLP record)
- **Control's "unsafe failure"**: Subtle fabrications (invented author names, corrupted details)

#### 5. Detailed Examples

Show 5-10 examples demonstrating:
- Treatment: Wrong paper retrieved, perfect metadata for that paper
- Control: Right paper found, corrupted metadata (fabricated authors)
- Both correct
- Both failed

#### 6. Conclusion

- Emphasize: MCP-DBLP's unmediated export = 0% metadata corruption
- Treatment's only errors are search/matching (fixable with better queries)
- Control's errors include insidious fabrications (hard to detect)

## Important

- Be objective and precise
- Always verify Treatment's "wrong papers" are real DBLP entries with perfect exports
- Calculate percentages to 1 decimal place
- Use matter-of-fact language (no superlatives)
- Make the two-stage distinction crystal clear throughout
