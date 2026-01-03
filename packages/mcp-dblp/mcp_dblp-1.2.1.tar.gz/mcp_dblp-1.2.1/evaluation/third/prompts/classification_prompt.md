# BibTeX Classification Criteria v2

## Categories

### PM (Perfect Match)
Correct paper with accurate metadata. Minor formatting differences are acceptable.

**PM Examples:**
- Journal abbreviation differs: `J. Comput. Assist. Learn.` vs `Journal of Computer Assisted Learning` → **PM**
- Diacritic variation: `Niklas Kühl` vs `Niklas Kuhl` → **PM**
- Missing DBLP-specific fields (`timestamp`, `biburl`, `bibsource`) → **PM**
- Missing `url` when `doi` is present → **PM**
- Page format differs: `pages = {8}` (article number) vs `pages = {953--979}` (page range) for same paper → **PM**
- DOI case differs: `10.3390/A18070444` vs `10.3390/a18070444` → **PM**

### WP (Wrong Paper)
Different paper than ground truth - different title, different work entirely.

**WP Examples:**
- GT: "A Comparison of Energy Consumption..." vs Output: "A Multi-Objective Bio-Inspired Optimization..." → **WP** (completely different titles)
- Same author but different paper by that author → **WP**
- Similar topic but different specific work → **WP**

**WP vs CM distinction:**
- If the TITLE is different → **WP** (wrong paper)
- If the title matches but metadata values are wrong → **CM**

### NF (Not Found)
Entry is missing or explicitly marked as not found.

**NF Examples:**
- `% NOT FOUND: citation text` → **NF**
- Entry missing entirely → **NF**

### IM (Incomplete Metadata)
Correct paper but missing important fields OR abbreviated author names.

**IM Examples:**
- Missing `doi` field when GT has one → **IM**
- Missing `pages` field when GT has one → **IM**
- Missing `volume` or `number` field → **IM**
- Abbreviated first name: `J. Smith` instead of `John Smith` → **IM**
- Initials only: `Smith, J. and Doe, A.` → **IM**

### IA (Incomplete Author)
Correct paper but author list is truncated or has placeholder.

**IA Examples:**
- `and others` at end of author list → **IA**
- `Author Unknown` → **IA**
- GT has 5 authors, Output has only 2 → **IA**

### CM (Corrupted Metadata)
Correct paper (same title) but with WRONG values - not missing, but incorrect.

**CM Examples - WRONG AUTHOR NAMES:**
- `Ma'mon Abu Hammad` vs `Manal Abu Hammad` → **CM** (different first name)
- `Aleksander Dabek` vs `Aleksandra Dabek` → **CM** (wrong gender/spelling)
- `Duo Zhao` vs `Dingyi Zhao` → **CM** (completely different first name)
- `Giacomo Dabisias` vs `Erico Landolfi` → **CM** (completely wrong author)

**CM Examples - WRONG FIELD VALUES:**
- GT: `year = {2024}` vs Output: `year = {2025}` → **CM**
- GT: `pages = {100--110}` vs Output: `pages = {200--210}` → **CM**
- GT: `doi = {10.17705/1CAIS.04845}` vs Output: `doi = {10.17705/1CAIS.04846}` → **CM** (wrong digit)
- GT: `volume = {18}` vs Output: `volume = {17}` → **CM**

**NOT CM (these are IM or PM):**
- `J. Smith` vs `John Smith` → **IM** (abbreviated, not wrong)
- Missing DOI → **IM** (missing, not wrong)
- Different page format (article# vs page range) for same paper → **PM**

### UK (Unknown - needs manual check)
Use when classification is genuinely ambiguous and requires human verification.

**UK Examples:**
- Cannot determine if it's the same paper or a different one
- Author names differ in ways that could be typos or different people
- Conflicting signals (e.g., same title but very different metadata)

## Classification Rules

1. **Check title FIRST**: If title is clearly different → **WP** (stop, don't check metadata)
2. **Check if found**: If entry missing or "NOT FOUND" → **NF** (stop)
3. **For same paper**: Check metadata quality in this order:
   - Wrong values (names, year, DOI digits, pages) → **CM**
   - Truncated/placeholder authors → **IA**
   - Missing fields or abbreviated names → **IM**
   - Complete and accurate → **PM**
4. **Severity hierarchy**: WP > NF > CM > IA > IM > PM (report most severe)
5. **When uncertain**: Use **UK** rather than guessing

## Real Examples from This Dataset

### CM Case #1:
- GT: `author = {Ma'mon Abu Hammad and Imane Zouak and Adel Ouannas and Giuseppe Grassi}`
- Output: `author = {Manal Abu Hammad and Imane Zouak and Adel Ouannas and Giuseppe Grassi}`
- **CM**: First author's first name is wrong (Ma'mon ≠ Manal)

### CM Case #26:
- GT: `author = {Duo Zhao and Qichao Tang and Lei Ma and Yongkui Sun and Jieyu Lei}`
- Output: `author = {Dingyi Zhao and Qiao Tang and Li Ma and Yu Sun and Jie Lei}`
- **CM**: All five author first names are wrong

### CM Case #82:
- GT: `doi = {10.17705/1CAIS.04845}`
- Output: `doi = {10.17705/1CAIS.04846}`
- **CM**: DOI differs by one digit (45 vs 46)

### WP Case #16:
- GT title: "A Comparison of Energy Consumption and Quality of Solutions in Evolutionary Algorithms"
- Output title: "A Multi-Objective Bio-Inspired Optimization for Voice Disorders Detection"
- **WP**: Completely different papers (same co-author García-Sánchez, but different work)

### PM Case #14:
- GT: `pages = {8}` (article number in JAIS)
- Output: `pages = {953--979}` (page range)
- **PM**: Same paper, different page representation format
