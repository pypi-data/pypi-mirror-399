# Frequency-Based Error Topology Framework

**Version**: 3.0 (GEMT-designed, frequency-based)
**Purpose**: Count occurrences of specific error types rather than linear scoring

## Key Principle: Character over Quality

This framework moves from "how *good* is this citation" to "what exactly is *wrong* with this citation."

Distinguishes between:
- **Lazy** (incomplete data)
- **Hallucinating** (fabricated data)
- **Misaligned** (wrong paper with perfect metadata)

---

## 1. Error Taxonomy (Discrete Categories)

Every entry is classified into **exactly one** category using the **Hierarchy of Severity** (top = most severe).

### A. Critical Failures (Unusable or misleading)

| Code | Category | Definition | Nature | Harm Level |
|:-----|:---------|:-----------|:-------|:-----------|
| **NF** | **NOT FOUND** | System explicitly states it could not find the paper or returns empty/comment-only entry | Omission | Low (User knows it failed) |
| **WP** | **WRONG PAPER** | System retrieves a *real* paper, but not the paper requested (wrong year, same author different title, etc.) | Misidentification | Medium (User directed to wrong resource) |
| **FP** | **FABRICATED PAPER** | Paper title and author combination does not exist in reality | Hallucination | High (Wild goose chase) |

### B. Integrity Failures (Paper correct, data flawed)

| Code | Category | Definition | Nature | Harm Level |
|:-----|:---------|:-----------|:-------|:-----------|
| **FM** | **FABRICATED METADATA** | Paper identity correct, but specific fields are invented (fake author names, invented pages/venue) | Fabrication | High (Pollutes database) |
| **CM** | **CORRUPTED METADATA** | Data is "messy" but likely derived from real source (typos in titles, wrong volume/issue, author names misspelled) | Corruption | Medium (Requires cleaning) |

### C. Completeness Failures (Paper correct, data true but missing)

| Code | Category | Definition | Nature | Harm Level |
|:-----|:---------|:-----------|:-------|:-----------|
| **IA** | **INCOMPLETE AUTHOR** | Author list truncated or generic ("Author Unknown", "and others", "et al", missing first author) | Incompleteness | Low (Requires lookup) |
| **IM** | **INCOMPLETE METADATA** | Missing standard fields (DOI, Venue, Pages, Year) | Incompleteness | Low (Inconvenient) |

### D. Success

| Code | Category | Definition | Nature |
|:-----|:---------|:-----------|:-------|
| **PM** | **PERFECT MATCH** | Entry matches Ground Truth in all critical fields (Title, Author, Venue, Year) with DBLP-level quality | Success |

---

## 2. Classification Rules

### The "Stop at Failure" Rule
1. If entry is **NOT FOUND**, stop. Do not check for metadata errors.
2. If entry is **WRONG PAPER**, classify as WP. Do not grade metadata of wrong paper.
3. If entry is **FABRICATED PAPER**, classify as FP.

### The "Most Severe Error" Rule
If a citation has multiple errors, use the most harmful:
- Example: "Author Unknown" + fake DOI → Classify as **FM** (Fabricated Metadata)
- Example: Wrong paper with perfect metadata → Classify as **WP** (Wrong Paper)

### Verifiability Check
- **Control Group:** Is error a parsing failure (Incomplete) or generative guess (Fabricated)?
- **Treatment Group:** Does error stem from API returning nothing (Not Found) or LLM misinterpreting JSON (Corrupted)?

---

## 3. Comparison Strategy (Frequency Distributions)

Generate distribution table showing the *character* of each tool.

### Expected Patterns

**Control (Web Search):**
- High **Incomplete Author** (scraping difficulties)
- High **Wrong Paper** (disambiguation failures)
- Some **Fabricated Metadata** (LLM guessing)

**Treatment (MCP-DBLP):**
- Higher **Not Found** (strict API matching)
- Very high **Perfect Match** when found
- Zero **Fabricated Metadata** (unmediated export)

### Comparison Table Template

| Error Category | Control (n) | Control (%) | Treatment (n) | Treatment (%) | Delta (T-C) |
|:---------------|:-----------:|:-----------:|:-------------:|:-------------:|:-----------:|
| NOT FOUND | 35 | 33.6% | 23 | 22.1% | -11.5% |
| WRONG PAPER | 10 | 9.6% | 2 | 1.9% | -7.7% |
| FABRICATED PAPER | 5 | 4.8% | 0 | 0.0% | -4.8% |
| FABRICATED METADATA | 2 | 1.9% | 0 | 0.0% | -1.9% |
| CORRUPTED METADATA | 8 | 7.7% | 1 | 0.9% | -6.8% |
| INCOMPLETE AUTHOR | 15 | 14.4% | 0 | 0.0% | -14.4% |
| INCOMPLETE METADATA | 20 | 19.2% | 5 | 4.8% | -14.4% |
| **PERFECT MATCH** | **9** | **8.6%** | **73** | **70.2%** | **+61.6%** |
| **TOTAL** | **104** | **100%** | **104** | **100%** | |

---

## 4. Example Classifications

### Control Group Examples

1. **Entry:** `GreinerHormann2025` with `author = {Author Unknown}`
   - **Ground Truth:** `ZuoFLLZZ25` (Jiwei Zuo et al.)
   - **Analysis:** Title matches GT exactly. Author is missing.
   - **Classification:** **IA** (Incomplete Author) - NOT fabrication

2. **Entry:** `Wang2025` - Model-assisted estimators
   - **Ground Truth:** `WangLS23` - Machine Learning Feature Based Job Scheduling
   - **Analysis:** Real paper by "Wang" in 2025, but completely different paper
   - **Classification:** **WP** (Wrong Paper)

3. **Entry:** `Waele2025` with `note = {Citation not found...}`
   - **Analysis:** Explicit failure
   - **Classification:** **NF** (Not Found)

4. **Entry:** `PAMA2025` with `author = {Author Unknown}`
   - **Ground Truth:** `KarousosPVV25` (Nikos Karousos et al.)
   - **Analysis:** Title matches GT. Author missing.
   - **Classification:** **IA** (Incomplete Author)

### Treatment Group Examples

1. **Entry:** `Grassi2025` - Complete metadata
   - **Ground Truth:** `HammadZOG25`
   - **Analysis:** Exact match
   - **Classification:** **PM** (Perfect Match)

2. **Entry:** `% NOT FOUND: Stodden2024... (404 error)`
   - **Analysis:** API failed to retrieve
   - **Classification:** **NF** (Not Found)

3. **Entry:** `Wallace2023` - Testing a New "Decrypted" Algorithm
   - **Ground Truth:** `Wallace23`
   - **Analysis:** Matches GT
   - **Classification:** **PM** (Perfect Match)

---

## 5. Benefits of This Approach

1. **Forgives Honesty:** "Author Unknown" (Incomplete) penalized less than inventing "John Smith" (Fabricated)

2. **Exposes Hallucination:** "Wrong Paper" vs "Perfect Match" becomes primary reliability metric

3. **Actionable Insights:**
   - High Treatment "Not Found" → Fix search query generation
   - High Control "Wrong Paper" → Web search unreliable for disambiguation
   - High Control "Incomplete Author" → Scraping difficulties
   - Any "Fabricated Metadata" → Critical safety issue

4. **Fair Comparison:** Treatment's unmediated export should show 0% fabrication, even if it has more "Not Found" entries
