#!/usr/bin/env python3
"""
Classify Control and Treatment group entries against Ground Truth
using the frequency-based evaluation framework (v3.0).
"""

import re
from collections import Counter
from pathlib import Path
import bibtexparser
from bibtexparser.bparser import BibTexParser


# Error category codes
NF = "NF"  # Not Found
WP = "WP"  # Wrong Paper
FP = "FP"  # Fabricated Paper
FM = "FM"  # Fabricated Metadata
CM = "CM"  # Corrupted Metadata
IA = "IA"  # Incomplete Author
IM = "IM"  # Incomplete Metadata
PM = "PM"  # Perfect Match


def normalize_title(title):
    """Normalize title for comparison (lowercase, no punctuation)."""
    # Remove LaTeX commands
    title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
    title = re.sub(r'[{}]', '', title)
    # Lowercase and remove punctuation
    title = title.lower()
    title = re.sub(r'[^\w\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def normalize_authors(authors):
    """Extract last names from author string."""
    if not authors or authors.lower() in ['author unknown', 'unknown authors', '']:
        return set()
    # Split by 'and'
    author_list = re.split(r'\s+and\s+', authors)
    last_names = set()
    for author in author_list:
        # Skip "and others", "et al"
        if 'others' in author.lower() or 'et al' in author.lower():
            continue
        # Extract last name (after last space/comma)
        parts = re.split(r'[,\s]+', author.strip())
        if parts:
            last_names.add(parts[-1].lower())
    return last_names


def parse_bib_with_comments(filepath):
    """Parse BibTeX file and extract NOT FOUND comments."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse BibTeX entries
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    bib_db = bibtexparser.loads(content, parser=parser)

    # Extract NOT FOUND comments
    not_found = []
    for line in content.split('\n'):
        if line.strip().startswith('%') and 'NOT FOUND' in line.upper():
            not_found.append(line.strip())

    return bib_db.entries, not_found


def classify_entry(control_entry, treatment_entry, gt_entry, control_nf, treatment_nf, citation_idx):
    """
    Classify Control and Treatment entries for a single citation.

    Returns: (control_category, treatment_category, notes)
    """
    # Check Ground Truth
    gt_title = normalize_title(gt_entry.get('title', '')) if gt_entry else ''
    gt_authors = normalize_authors(gt_entry.get('author', '')) if gt_entry else set()
    gt_year = gt_entry.get('year', '') if gt_entry else ''

    control_cat = None
    treatment_cat = None
    notes = {}

    # Classify Control
    if control_entry is None:
        # Check if in NOT FOUND list
        if any(str(citation_idx) in nf or (gt_entry and gt_entry.get('ID', '') in nf) for nf in control_nf):
            control_cat = NF
            notes['control'] = "Explicit NOT FOUND comment"
        else:
            control_cat = NF
            notes['control'] = "Missing entry"
    else:
        c_title = normalize_title(control_entry.get('title', ''))
        c_authors = normalize_authors(control_entry.get('author', ''))
        c_year = control_entry.get('year', '')

        # Check for "Author Unknown"
        has_unknown_author = 'author unknown' in control_entry.get('author', '').lower()
        has_and_others = 'and others' in control_entry.get('author', '').lower()

        # Check if paper matches
        title_match = c_title and gt_title and (c_title == gt_title or c_title in gt_title or gt_title in c_title)
        author_match = c_authors and gt_authors and len(c_authors & gt_authors) > 0
        year_match = c_year == gt_year

        if not title_match and not author_match:
            # Wrong paper or fabricated
            control_cat = WP  # For now, assume real paper (need manual verification for FP)
            notes['control'] = f"Title/author mismatch: {c_title[:50]}..."
        elif title_match and (has_unknown_author or has_and_others):
            control_cat = IA
            notes['control'] = "Correct paper, incomplete author"
        elif title_match and not control_entry.get('doi'):
            control_cat = IM
            notes['control'] = "Correct paper, missing DOI"
        elif title_match:
            control_cat = PM
            notes['control'] = "Perfect match"
        else:
            control_cat = CM
            notes['control'] = "Possible corruption"

    # Classify Treatment
    if treatment_entry is None:
        if any(str(citation_idx) in nf or (gt_entry and gt_entry.get('ID', '') in nf) for nf in treatment_nf):
            treatment_cat = NF
            notes['treatment'] = "Explicit NOT FOUND comment"
        else:
            treatment_cat = NF
            notes['treatment'] = "Missing entry"
    else:
        t_title = normalize_title(treatment_entry.get('title', ''))
        t_authors = normalize_authors(treatment_entry.get('author', ''))
        t_year = treatment_entry.get('year', '')

        # Check if paper matches
        title_match = t_title and gt_title and (t_title == gt_title or t_title in gt_title or gt_title in t_title)
        author_match = t_authors and gt_authors and len(t_authors & gt_authors) > 0
        year_match = t_year == gt_year

        if not title_match and not author_match:
            treatment_cat = WP
            notes['treatment'] = f"Title/author mismatch: {t_title[:50]}..."
        elif not treatment_entry.get('doi'):
            treatment_cat = IM
            notes['treatment'] = "Missing DOI"
        else:
            treatment_cat = PM
            notes['treatment'] = "Perfect match"

    return control_cat, treatment_cat, notes


def main():
    # Load files
    gt_entries, _ = parse_bib_with_comments('ground_truth.bib')
    control_entries, control_nf = parse_bib_with_comments('data/control_output.bib')
    treatment_entries, treatment_nf = parse_bib_with_comments('data/treatment_output.bib')

    print(f"Loaded {len(gt_entries)} ground truth entries")
    print(f"Loaded {len(control_entries)} control entries, {len(control_nf)} NOT FOUND")
    print(f"Loaded {len(treatment_entries)} treatment entries, {len(treatment_nf)} NOT FOUND")
    print()

    # Create dictionaries
    gt_dict = {entry['ID']: entry for entry in gt_entries}
    control_dict = {entry['ID']: entry for entry in control_entries}
    treatment_dict = {entry['ID']: entry for entry in treatment_entries}

    # Classify all entries
    control_counts = Counter()
    treatment_counts = Counter()

    results = []

    for idx, (gt_id, gt_entry) in enumerate(gt_dict.items(), 1):
        control_entry = control_dict.get(gt_id)
        treatment_entry = treatment_dict.get(gt_id)

        c_cat, t_cat, notes = classify_entry(control_entry, treatment_entry, gt_entry,
                                             control_nf, treatment_nf, idx)

        control_counts[c_cat] += 1
        treatment_counts[t_cat] += 1

        results.append({
            'idx': idx,
            'gt_id': gt_id,
            'control_cat': c_cat,
            'treatment_cat': t_cat,
            'notes': notes
        })

    # Print frequency distribution
    total = len(gt_dict)

    print("="*80)
    print("FREQUENCY DISTRIBUTION")
    print("="*80)
    print()
    print(f"{'Category':<25} {'Control (n)':<15} {'Control (%)':<15} {'Treatment (n)':<15} {'Treatment (%)':<15} {'Delta':<10}")
    print("-"*80)

    categories = [NF, WP, FP, FM, CM, IA, IM, PM]
    for cat in categories:
        c_count = control_counts[cat]
        t_count = treatment_counts[cat]
        c_pct = (c_count / total) * 100
        t_pct = (t_count / total) * 100
        delta = t_pct - c_pct

        print(f"{cat:<25} {c_count:<15} {c_pct:<15.1f} {t_count:<15} {t_pct:<15.1f} {delta:+.1f}%")

    print("-"*80)
    print(f"{'TOTAL':<25} {total:<15} {100.0:<15.1f} {total:<15} {100.0:<15.1f}")
    print()

    # Print examples
    print("="*80)
    print("EXAMPLE CLASSIFICATIONS")
    print("="*80)
    print()

    for cat in categories:
        examples = [r for r in results if r['control_cat'] == cat or r['treatment_cat'] == cat][:3]
        if examples:
            print(f"\n{cat} Examples:")
            for ex in examples:
                print(f"  Citation #{ex['idx']} ({ex['gt_id']})")
                print(f"    Control: {ex['control_cat']} - {ex['notes'].get('control', 'N/A')}")
                print(f"    Treatment: {ex['treatment_cat']} - {ex['notes'].get('treatment', 'N/A')}")

    # Save detailed results
    with open('data/classification_results_v3.csv', 'w', encoding='utf-8') as f:
        f.write("idx,gt_id,control_category,treatment_category,control_notes,treatment_notes\n")
        for r in results:
            f.write(f"{r['idx']},{r['gt_id']},{r['control_cat']},{r['treatment_cat']},"
                   f"\"{r['notes'].get('control', '')}\",\"{r['notes'].get('treatment', '')}\"\n")

    print("\n\nDetailed results saved to: data/classification_results_v3.csv")


if __name__ == '__main__':
    main()
