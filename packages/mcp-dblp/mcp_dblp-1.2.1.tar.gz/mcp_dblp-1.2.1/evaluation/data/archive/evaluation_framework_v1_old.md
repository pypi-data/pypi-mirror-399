# Bibliographic Citation Evaluation Framework

**Version**: 2.0 (GEMT-designed)
**Purpose**: Compare Control (web search + manual BibTeX) vs Treatment (MCP-DBLP unmediated export)

## Key Principle: Retrieval Accuracy vs Metadata Integrity

- **Treatment Group**: Uses DBLP API → metadata is internally consistent (ground truth for the paper it retrieved)
- **Control Group**: Manual generation → subject to hallucination AND metadata corruption

## 1. Error Taxonomy & Definitions

| Error Category | Definition | Severity |
|:---------------|:-----------|:---------|
| **A. Fabrication (Hallucination)** | Generation of specific data points (Title, Venue, DOI, Author names) that do not exist in reality | **Critical** - Applies mostly to Control. Distinguishes "lying" from "not knowing" |
| **B. Retrieval Alignment Error** | System returns a valid, real paper, but it is not the specific paper requested (e.g., wrong year, wrong author with same surname) | **Critical** - Metadata is "true" but citation is "wrong" for the context |
| **C. Incomplete Information** | System acknowledges missing data ("Author Unknown", "and others") or omits optional fields (DOI, pages) | **Acceptable/Minor** - System is honest about limitations |
| **D. Metadata Corruption** | Paper exists, but specific fields are transcribed incorrectly (typo in title, wrong volume, inventing DOI for real paper) | **Moderate** - Makes finding difficult but paper exists |
| **E. Omission (Not Found)** | System explicitly states it could not find the citation | **Neutral** - Better than hallucination |

## 2. Severity Ratings & Scoring

| Status | Label | Criteria | Points |
|:-------|:------|:---------|:-------|
| **Perfect** | `EXACT_MATCH` | Correct Paper + Full Metadata (Authors, Title, Venue, Year) | **3** |
| **Good** | `VALID_INCOMPLETE` | Correct Paper found, but missing DOI or uses "et al." / "Author Unknown" | **2** |
| **Poor** | `METADATA_ERROR` | Correct Paper found, but title/venue has typos or hallucinations | **1** |
| **Fail** | `WRONG_PAPER` | Real paper retrieved, but not the one requested | **0** |
| **Fail** | `HALLUCINATION` | Paper does not exist (Fabricated title/author) | **-1** |
| **Null** | `NOT_FOUND` | Explicit "Not Found" comment | **0** |

## 3. Field-Specific Evaluation Criteria

### A. Author Field

**Treatment (DBLP):** Always accurate *for the retrieved paper*

**Control:**
- **Acceptable Incompleteness:** "Author Unknown", "Smith et al.", "and others"
- **Fabrication:** Inventing names (e.g., "John Doe" when author is "Jane Smith")
- **Corruption:** "Waele" instead of "Wim De Waele" (Mononym usage)

### B. Title Field

**Treatment (DBLP):** Exact match to publisher data

**Control:**
- **Hallucination:** A plausible-sounding title that doesn't exist
- **Paraphrasing:** Semantically similar but not exact (Metadata Corruption)

### C. Venue (Journal/Conference)

**Treatment (DBLP):** Standardized abbreviations (e.g., "Int. J. Hum. Comput. Interact.")

**Control:**
- **Generic Mapping:** Using "IEEE" or "ACM" as publisher instead of specific conference
- **Hallucination:** Citing a venue the paper never appeared in

### D. Identifiers (DOI/URL)

**Treatment (DBLP):** Usually provides `doi` or `url`

**Control:**
- **Missing:** Acceptable
- **Dead/Fake Link:** Critical Fabrication

## 4. The "Findability" Test

**Question:** Can a reader locate the correct document in <60 seconds using the provided metadata?

### Harmful (Fail)
- **Fabrication:** User searches for title that doesn't exist. Wastes time.
- **Wrong Paper:** User downloads wrong PDF because system retrieved a 2022 paper by "Chen" instead of requested 2025 paper
- **Fake DOI:** User clicks link that 404s

### Acceptable (Pass)
- **"Author Unknown":** User searches Title. Finds paper. (Honest incompleteness)
- **Missing DOI:** User searches Title + Year. Finds paper.
- **"et al." usage:** Standard academic practice

## 5. Comparison Metrics

### Precision Score
```
Sum of Points / Total Citations Attempted (excluding Not Found)
```
**Measures:** How trustworthy is the information when it *is* provided?

### Recall Score
```
Count of (Exact + Valid) / Total Citation Slots (104)
```
**Measures:** How many citations were successfully retrieved?

### Hallucination Rate
```
Count of Hallucinations / Total Output Entries
```
**Measures:** Safety. Treatment should theoretically be 0% (unless API returns garbage)

## 6. Expected Patterns

### Control Group Warning Signs
- `author = {Author Unknown}` → Score 2 (Valid Incomplete) if paper exists
- `note = {Citation not found...}` → Score 0 (Not Found)
- `author = {Xin Wang and Huang}` → Score 1 (Metadata Error) - missing first name

### Treatment Group Warning Signs
- `% NOT FOUND: ... (DBLP key... 404 error)` → Score 0 (Not Found) - tool tried, failed
- Retrieved paper doesn't match request → Score 0 (Wrong Paper)

## 7. Comparison Outcome

**Treatment (MCP-DBLP) wins if it:**
- Maximizes **Exact Matches**
- Eliminates **Hallucinations**
- Even if it has higher **Not Found** rate (preferring silence over lying)

**Key Insight:** Treatment errors are retrieval/alignment errors (wrong paper selected). Control errors include both retrieval failures AND metadata corruption/fabrication.
