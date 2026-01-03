#!/usr/bin/env python3
"""
Two-Stage Evaluation of Control vs Treatment BibTeX Outputs

Stage 1: Paper Matching - Did we find the right paper?
Stage 2: Metadata Fidelity - Is the BibTeX accurate for the retrieved paper?
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import sys

def parse_bibtex_file(filepath: str) -> Dict[str, Dict[str, str]]:
    """Parse a BibTeX file and extract entries with their fields."""
    entries = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into individual entries
    # Match @type{key, ... }
    pattern = r'@(\w+)\{([^,]+),\s*(.*?)\n\}'
    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        entry_type = match.group(1).lower()
        key = match.group(2).strip()
        fields_str = match.group(3)

        entry = {
            '_type': entry_type,
            '_key': key
        }

        # Parse fields
        # Handle multi-line fields properly
        field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}|(\w+)\s*=\s*"([^"]*)"'
        for field_match in re.finditer(field_pattern, fields_str):
            if field_match.group(1):
                field_name = field_match.group(1).lower()
                field_value = field_match.group(2)
            else:
                field_name = field_match.group(3).lower()
                field_value = field_match.group(4)

            entry[field_name] = field_value.strip()

        entries[key] = entry

    return entries

def normalize_string(s: str) -> str:
    """Normalize string for comparison - lowercase, remove extra whitespace."""
    if not s:
        return ""
    # Remove LaTeX commands like \'{a}, \"{o}, etc.
    s = re.sub(r'\\[\'"`^~=.]{0,1}\{([a-zA-Z])\}', r'\1', s)
    s = re.sub(r'\\[\'"`^~=.]([a-zA-Z])', r'\1', s)
    # Remove other LaTeX commands
    s = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    # Remove braces
    s = s.replace('{', '').replace('}', '')
    # Lowercase and normalize whitespace
    s = ' '.join(s.lower().split())
    return s

def extract_authors(author_str: str) -> List[str]:
    """Extract list of author last names."""
    if not author_str:
        return []
    # Split by 'and'
    authors = re.split(r'\s+and\s+', author_str)
    last_names = []
    for author in authors:
        author = author.strip()
        if not author:
            continue
        # Handle "Last, First" format
        if ',' in author:
            parts = author.split(',')
            last_names.append(normalize_string(parts[0]))
        else:
            # Handle "First Last" format - take last word
            words = author.split()
            if words:
                last_names.append(normalize_string(words[-1]))
    return last_names

def match_paper(test_entry: Dict[str, str], ground_truth: Dict[str, Dict[str, str]]) -> Tuple[str, Optional[str], float]:
    """
    Match a test entry against ground truth.

    Returns:
        (status, matched_key, confidence)
        status: 'correct_match', 'wrong_but_real', 'fabricated', 'missing'
    """
    if not test_entry:
        return ('missing', None, 0.0)

    # Check if it's a NOT FOUND comment
    if '_type' not in test_entry:
        return ('missing', None, 0.0)

    # Try to match by DOI first (most reliable)
    test_doi = normalize_string(test_entry.get('doi', ''))
    if test_doi:
        for gt_key, gt_entry in ground_truth.items():
            gt_doi = normalize_string(gt_entry.get('doi', ''))
            if gt_doi and test_doi == gt_doi:
                return ('correct_match', gt_key, 1.0)

    # Try to match by title + year
    test_title = normalize_string(test_entry.get('title', ''))
    test_year = test_entry.get('year', '')

    best_match_key = None
    best_match_score = 0.0

    for gt_key, gt_entry in ground_truth.items():
        gt_title = normalize_string(gt_entry.get('title', ''))
        gt_year = gt_entry.get('year', '')

        # Calculate title similarity (simple word overlap)
        if test_title and gt_title:
            test_words = set(test_title.split())
            gt_words = set(gt_title.split())
            if test_words and gt_words:
                overlap = len(test_words & gt_words)
                union = len(test_words | gt_words)
                similarity = overlap / union if union > 0 else 0.0

                # Boost if years match
                if test_year == gt_year and similarity > best_match_score:
                    best_match_score = similarity
                    best_match_key = gt_key

    # Threshold for "correct match"
    if best_match_score > 0.6:  # More than 60% word overlap
        return ('correct_match', best_match_key, best_match_score)
    elif best_match_score > 0.3:  # Some overlap but wrong paper
        return ('wrong_but_real', best_match_key, best_match_score)
    else:
        # Check if it has valid-looking metadata (real paper) or fabricated
        if test_entry.get('author') and test_entry.get('title') and test_entry.get('year'):
            return ('wrong_but_real', None, 0.0)
        else:
            return ('fabricated', None, 0.0)

def compare_metadata(test_entry: Dict[str, str], gt_entry: Dict[str, str]) -> Dict[str, bool]:
    """Compare metadata fields between test and ground truth entries."""
    results = {}

    # Compare authors
    test_authors = set(extract_authors(test_entry.get('author', '')))
    gt_authors = set(extract_authors(gt_entry.get('author', '')))
    results['authors_match'] = test_authors == gt_authors
    results['authors_partial'] = len(test_authors & gt_authors) > 0 if test_authors and gt_authors else False

    # Compare title
    test_title = normalize_string(test_entry.get('title', ''))
    gt_title = normalize_string(gt_entry.get('title', ''))
    results['title_exact'] = test_title == gt_title
    # Allow minor differences
    if test_title and gt_title:
        test_words = set(test_title.split())
        gt_words = set(gt_title.split())
        overlap = len(test_words & gt_words) / len(gt_words) if gt_words else 0
        results['title_close'] = overlap > 0.9
    else:
        results['title_close'] = False

    # Compare year
    results['year_match'] = test_entry.get('year', '') == gt_entry.get('year', '')

    # Compare venue (journal/booktitle)
    test_venue = normalize_string(test_entry.get('journal', test_entry.get('booktitle', '')))
    gt_venue = normalize_string(gt_entry.get('journal', gt_entry.get('booktitle', '')))
    results['venue_exact'] = test_venue == gt_venue if test_venue and gt_venue else False
    # Allow abbreviations/partial matches
    if test_venue and gt_venue:
        results['venue_partial'] = test_venue in gt_venue or gt_venue in test_venue
    else:
        results['venue_partial'] = False

    # Compare DOI
    test_doi = normalize_string(test_entry.get('doi', ''))
    gt_doi = normalize_string(gt_entry.get('doi', ''))
    results['doi_match'] = test_doi == gt_doi if test_doi and gt_doi else False

    return results

def evaluate_outputs(ground_truth_path: str, control_path: str, treatment_path: str):
    """Run two-stage evaluation."""

    print("Loading BibTeX files...")
    ground_truth = parse_bibtex_file(ground_truth_path)
    control_entries = parse_bibtex_file(control_path)
    treatment_entries = parse_bibtex_file(treatment_path)

    print(f"\nGround truth entries: {len(ground_truth)}")
    print(f"Control entries: {len(control_entries)}")
    print(f"Treatment entries: {len(treatment_entries)}")

    # Stage 1: Paper Matching
    print("\n" + "="*80)
    print("STAGE 1: PAPER MATCHING")
    print("="*80)

    control_matches = defaultdict(int)
    treatment_matches = defaultdict(int)

    control_matched_keys = []
    treatment_matched_keys = []

    for key, entry in control_entries.items():
        status, gt_key, conf = match_paper(entry, ground_truth)
        control_matches[status] += 1
        if status == 'correct_match':
            control_matched_keys.append((key, gt_key, entry))

    for key, entry in treatment_entries.items():
        status, gt_key, conf = match_paper(entry, ground_truth)
        treatment_matches[status] += 1
        if status == 'correct_match':
            treatment_matched_keys.append((key, gt_key, entry))

    print(f"\nControl Group:")
    print(f"  Correct Match: {control_matches['correct_match']}/{len(ground_truth)}")
    print(f"  Wrong-but-Real: {control_matches['wrong_but_real']}")
    print(f"  Fabricated: {control_matches['fabricated']}")
    print(f"  Missing: {control_matches['missing']}")

    print(f"\nTreatment Group:")
    print(f"  Correct Match: {treatment_matches['correct_match']}/{len(ground_truth)}")
    print(f"  Wrong-but-Real: {treatment_matches['wrong_but_real']}")
    print(f"  Fabricated: {treatment_matches['fabricated']}")
    print(f"  Missing: {treatment_matches['missing']}")

    # Stage 2: Metadata Fidelity
    print("\n" + "="*80)
    print("STAGE 2: METADATA FIDELITY (for correctly matched papers)")
    print("="*80)

    control_metadata = {
        'perfect_fidelity': 0,
        'authors_match': 0,
        'title_exact': 0,
        'year_match': 0,
        'venue_exact': 0,
        'doi_match': 0
    }

    treatment_metadata = {
        'perfect_fidelity': 0,
        'authors_match': 0,
        'title_exact': 0,
        'year_match': 0,
        'venue_exact': 0,
        'doi_match': 0
    }

    print(f"\nAnalyzing {len(control_matched_keys)} control matches...")
    for test_key, gt_key, test_entry in control_matched_keys:
        gt_entry = ground_truth[gt_key]
        results = compare_metadata(test_entry, gt_entry)

        if all([results['authors_match'], results['title_exact'],
                results['year_match'], results.get('doi_match', True)]):
            control_metadata['perfect_fidelity'] += 1

        if results['authors_match']:
            control_metadata['authors_match'] += 1
        if results['title_exact']:
            control_metadata['title_exact'] += 1
        if results['year_match']:
            control_metadata['year_match'] += 1
        if results['venue_exact']:
            control_metadata['venue_exact'] += 1
        if results.get('doi_match'):
            control_metadata['doi_match'] += 1

    print(f"\nAnalyzing {len(treatment_matched_keys)} treatment matches...")
    for test_key, gt_key, test_entry in treatment_matched_keys:
        gt_entry = ground_truth[gt_key]
        results = compare_metadata(test_entry, gt_entry)

        if all([results['authors_match'], results['title_exact'],
                results['year_match'], results.get('doi_match', True)]):
            treatment_metadata['perfect_fidelity'] += 1

        if results['authors_match']:
            treatment_metadata['authors_match'] += 1
        if results['title_exact']:
            treatment_metadata['title_exact'] += 1
        if results['year_match']:
            treatment_metadata['year_match'] += 1
        if results['venue_exact']:
            treatment_metadata['venue_exact'] += 1
        if results.get('doi_match'):
            treatment_metadata['doi_match'] += 1

    # Print results
    control_total = len(control_matched_keys)
    treatment_total = len(treatment_matched_keys)

    print(f"\nControl Group Metadata Fidelity (n={control_total}):")
    if control_total > 0:
        print(f"  Perfect Fidelity: {control_metadata['perfect_fidelity']/control_total*100:.1f}%")
        print(f"  Author Accuracy: {control_metadata['authors_match']/control_total*100:.1f}%")
        print(f"  Title Accuracy: {control_metadata['title_exact']/control_total*100:.1f}%")
        print(f"  Year Accuracy: {control_metadata['year_match']/control_total*100:.1f}%")
        print(f"  Venue Accuracy: {control_metadata['venue_exact']/control_total*100:.1f}%")
        print(f"  DOI Accuracy: {control_metadata['doi_match']/control_total*100:.1f}%")

    print(f"\nTreatment Group Metadata Fidelity (n={treatment_total}):")
    if treatment_total > 0:
        print(f"  Perfect Fidelity: {treatment_metadata['perfect_fidelity']/treatment_total*100:.1f}%")
        print(f"  Author Accuracy: {treatment_metadata['authors_match']/treatment_total*100:.1f}%")
        print(f"  Title Accuracy: {treatment_metadata['title_exact']/treatment_total*100:.1f}%")
        print(f"  Year Accuracy: {treatment_metadata['year_match']/treatment_total*100:.1f}%")
        print(f"  Venue Accuracy: {treatment_metadata['venue_exact']/treatment_total*100:.1f}%")
        print(f"  DOI Accuracy: {treatment_metadata['doi_match']/treatment_total*100:.1f}%")

    return {
        'stage1_control': control_matches,
        'stage1_treatment': treatment_matches,
        'stage2_control': control_metadata,
        'stage2_treatment': treatment_metadata,
        'control_matched': control_matched_keys,
        'treatment_matched': treatment_matched_keys
    }

if __name__ == '__main__':
    ground_truth_path = '/Users/szeider/git/mcp-dblp/evaluation/ground_truth.bib'
    control_path = '/Users/szeider/git/mcp-dblp/evaluation/data/control_output.bib'
    treatment_path = '/Users/szeider/git/mcp-dblp/evaluation/data/treatment_output.bib'

    results = evaluate_outputs(ground_truth_path, control_path, treatment_path)
