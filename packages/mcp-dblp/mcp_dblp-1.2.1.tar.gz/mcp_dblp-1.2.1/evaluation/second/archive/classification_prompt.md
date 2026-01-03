# BibTeX Classification Criteria with Examples

## Categories

### PM (Perfect Match)
Correct paper with complete, accurate metadata. Minor formatting differences are OK.

**Examples of PM:**
- GT: `journal = {J. Comput. Assist. Learn.}` vs Output: `journal = {Journal of Computer Assisted Learning}` → **PM** (same journal, different abbreviation)
- GT: `author = {Niklas Kühl}` vs Output: `author = {Niklas Kuhl}` → **PM** (diacritic variation acceptable)
- Missing `timestamp`, `biburl`, `bibsource` fields → **PM** (these are DBLP-specific, not essential)
- Missing `url` field when `doi` is present → **PM** (DOI is sufficient)

### WP (Wrong Paper)
Different paper than ground truth - different title, different DOI, different work entirely.

**Examples of WP:**
- GT title: "Attention Is All You Need" vs Output title: "BERT: Pre-training..." → **WP**
- Same author but different paper by that author → **WP**
- GT DOI: `10.1145/3529399.3529400` vs Output DOI: `10.1145/3529399.3529401` → **WP** (different paper)

### NF (Not Found)
Entry is missing or explicitly marked as not found.

**Examples of NF:**
- `% NOT FOUND: citation text` → **NF**
- Entry simply missing (no BibTeX for that citation number) → **NF**

### IM (Incomplete Metadata)
Correct paper but missing important fields OR abbreviated author names.

**Examples of IM:**
- Missing `doi` field (when GT has one) → **IM**
- Missing `pages` field (when GT has one) → **IM**
- Missing `volume` or `number` field → **IM**
- `author = {J. Smith}` when GT has `author = {John Smith}` → **IM** (abbreviated first name)
- `author = {Smith, J. and Doe, A.}` → **IM** (initials instead of full names)

### IA (Incomplete Author)
Correct paper but author list is truncated or has placeholder.

**Examples of IA:**
- `author = {Smith, John and others}` → **IA** (truncated with "and others")
- `author = {Author Unknown}` → **IA**
- GT has 5 authors, Output has only 2 → **IA** (truncated list)

### CM (Corrupted Metadata)
Correct paper but with WRONG values - not missing, but incorrect.

**Examples of CM:**
- GT: `author = {Ma'mon Abu Hammad}` vs Output: `author = {Manal Abu Hammad}` → **CM** (wrong first name)
- GT: `year = {2024}` vs Output: `year = {2025}` → **CM** (wrong year)
- GT: `pages = {100--110}` vs Output: `pages = {200--210}` → **CM** (wrong pages)
- GT: `doi = {10.3390/a18070444}` vs Output: `doi = {10.3390/a18070445}` → **CM** (wrong DOI digit)
- GT: `author = {Aleksander Dabek}` vs Output: `author = {Aleksandra Dabek}` → **CM** (wrong gender/spelling)
- GT has author "Giacomo Dabisias" vs Output has "Erico Landolfi" → **CM** (completely wrong author)

## Classification Rules

1. **Hierarchy**: If NF or WP → stop, don't check metadata quality
2. **Severity**: CM > IA > IM (if multiple issues, report most severe)
3. **Focus on essential fields**: author, title, year, venue/journal, pages, doi
4. **Formatting tolerance**: Abbreviations, spacing, capitalization differences are OK for PM
