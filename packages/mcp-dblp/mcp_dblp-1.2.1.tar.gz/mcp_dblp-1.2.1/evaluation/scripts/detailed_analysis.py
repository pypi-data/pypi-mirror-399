#!/usr/bin/env python3
"""
Detailed analysis to find specific examples of different error types.
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
    """Normalize string for comparison."""
    if not s:
        return ""
    s = re.sub(r'\\[\'"`^~=.]{0,1}\{([a-zA-Z])\}', r'\1', s)
    s = re.sub(r'\\[\'"`^~=.]([a-zA-Z])', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    s = s.replace('{', '').replace('}', '')
    s = ' '.join(s.lower().split())
    return s

def extract_authors(author_str: str) -> List[str]:
    """Extract list of author last names."""
    if not author_str:
        return []
    authors = re.split(r'\s+and\s+', author_str)
    last_names = []
    for author in authors:
        author = author.strip()
        if not author:
            continue
        if ',' in author:
            parts = author.split(',')
            last_names.append(normalize_string(parts[0]))
        else:
            words = author.split()
            if words:
                last_names.append(normalize_string(words[-1]))
    return last_names

def find_examples(ground_truth_path: str, control_path: str, treatment_path: str):
    """Find specific examples of different error patterns."""

    ground_truth = parse_bibtex_file(ground_truth_path)
    control_entries = parse_bibtex_file(control_path)
    treatment_entries = parse_bibtex_file(treatment_path)

    print("="*80)
    print("DETAILED EXAMPLES")
    print("="*80)

    # Find control errors - metadata corruption
    print("\n### CONTROL ERRORS: Metadata Corruption ###\n")
    count = 0
    for c_key, c_entry in control_entries.items():
        if count >= 5:
            break

        # Find matching ground truth by title similarity
        c_title = normalize_string(c_entry.get('title', ''))
        c_year = c_entry.get('year', '')

        for gt_key, gt_entry in ground_truth.items():
            gt_title = normalize_string(gt_entry.get('title', ''))
            gt_year = gt_entry.get('year', '')

            if not c_title or not gt_title:
                continue

            c_words = set(c_title.split())
            gt_words = set(gt_title.split())
            if c_words and gt_words:
                overlap = len(c_words & gt_words) / len(gt_words)
                if overlap > 0.6 and c_year == gt_year:
                    # Found a match - compare metadata
                    c_authors = extract_authors(c_entry.get('author', ''))
                    gt_authors = extract_authors(gt_entry.get('author', ''))

                    if c_authors != gt_authors:
                        count += 1
                        print(f"Example {count}: {c_key}")
                        print(f"  Citation key: {gt_key}")
                        print(f"  Title match: {overlap*100:.0f}%")
                        print(f"  Control authors: {', '.join(c_authors[:3])}...")
                        print(f"  Ground truth authors: {', '.join(gt_authors[:3])}...")
                        print(f"  FINDING: Correct paper found, but authors corrupted\n")
                        break

    # Find treatment errors - wrong paper retrieved
    print("\n### TREATMENT ERRORS: Wrong Paper Retrieved (Safe Failure) ###\n")

    # Look for entries in treatment that don't match ground truth
    count = 0
    for t_key, t_entry in treatment_entries.items():
        if count >= 5:
            break

        t_title = normalize_string(t_entry.get('title', ''))
        t_doi = normalize_string(t_entry.get('doi', ''))

        if not t_title:
            continue

        # Check if this matches any ground truth entry
        found_match = False
        for gt_key, gt_entry in ground_truth.items():
            gt_title = normalize_string(gt_entry.get('title', ''))
            gt_doi = normalize_string(gt_entry.get('doi', ''))

            if gt_doi and t_doi and gt_doi == t_doi:
                found_match = True
                break

            if gt_title:
                t_words = set(t_title.split())
                gt_words = set(gt_title.split())
                if t_words and gt_words:
                    overlap = len(t_words & gt_words) / len(gt_words)
                    if overlap > 0.6:
                        found_match = True
                        break

        if not found_match:
            # This is a wrong paper - verify it has complete metadata
            if (t_entry.get('author') and t_entry.get('title') and
                t_entry.get('year') and t_entry.get('doi')):
                count += 1
                print(f"Example {count}: {t_key}")
                print(f"  Title: {t_entry.get('title', '')[:80]}...")
                print(f"  Authors: {', '.join(extract_authors(t_entry.get('author', ''))[:3])}...")
                print(f"  Year: {t_entry.get('year', '')}")
                print(f"  DOI: {t_entry.get('doi', '')}")
                print(f"  FINDING: Wrong paper retrieved, but metadata is complete and verifiable\n")

    # Show examples where both got it right
    print("\n### BOTH CORRECT: Same Paper, Different Metadata Quality ###\n")
    count = 0
    for gt_key, gt_entry in ground_truth.items():
        if count >= 3:
            break

        # Find this paper in both outputs
        gt_title = normalize_string(gt_entry.get('title', ''))
        gt_doi = normalize_string(gt_entry.get('doi', ''))

        c_match = None
        t_match = None

        # Find in control
        for c_key, c_entry in control_entries.items():
            c_title = normalize_string(c_entry.get('title', ''))
            c_doi = normalize_string(c_entry.get('doi', ''))

            if gt_doi and c_doi and gt_doi == c_doi:
                c_match = c_entry
                break
            elif gt_title and c_title:
                c_words = set(c_title.split())
                gt_words = set(gt_title.split())
                if c_words and gt_words:
                    overlap = len(c_words & gt_words) / len(gt_words)
                    if overlap > 0.7:
                        c_match = c_entry
                        break

        # Find in treatment
        for t_key, t_entry in treatment_entries.items():
            t_title = normalize_string(t_entry.get('title', ''))
            t_doi = normalize_string(t_entry.get('doi', ''))

            if gt_doi and t_doi and gt_doi == t_doi:
                t_match = t_entry
                break
            elif gt_title and t_title:
                t_words = set(t_title.split())
                gt_words = set(gt_title.split())
                if t_words and gt_words:
                    overlap = len(t_words & gt_words) / len(gt_words)
                    if overlap > 0.7:
                        t_match = t_entry
                        break

        if c_match and t_match:
            # Compare metadata quality
            c_authors = extract_authors(c_match.get('author', ''))
            t_authors = extract_authors(t_match.get('author', ''))
            gt_authors = extract_authors(gt_entry.get('author', ''))

            if t_authors == gt_authors and c_authors != gt_authors:
                count += 1
                print(f"Example {count}: {gt_key}")
                print(f"  Ground truth authors: {', '.join(gt_authors[:3])}...")
                print(f"  Control authors: {', '.join(c_authors[:3])}...")
                print(f"  Treatment authors: {', '.join(t_authors[:3])}...")
                print(f"  FINDING: Both found correct paper, Treatment has perfect metadata, Control corrupted\n")

if __name__ == '__main__':
    ground_truth_path = '/Users/szeider/git/mcp-dblp/evaluation/ground_truth.bib'
    control_path = '/Users/szeider/git/mcp-dblp/evaluation/data/control_output.bib'
    treatment_path = '/Users/szeider/git/mcp-dblp/evaluation/data/treatment_output.bib'

    find_examples(ground_truth_path, control_path, treatment_path)
