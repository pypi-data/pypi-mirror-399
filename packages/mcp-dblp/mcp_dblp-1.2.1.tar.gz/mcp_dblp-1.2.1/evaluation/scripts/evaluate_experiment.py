#!/usr/bin/env python3
"""
Comprehensive evaluation of MCP-DBLP experiment results.
Compares control group (web search) vs treatment group (MCP-DBLP) across 104 citations.
"""

import re
from pathlib import Path
from collections import Counter, defaultdict

# Error categories
NF = "NF"  # Not Found
WP = "WP"  # Wrong Paper
FP = "FP"  # Fabricated Paper
FM = "FM"  # Fabricated Metadata
CM = "CM"  # Corrupted Metadata
IA = "IA"  # Incomplete Author
IM = "IM"  # Incomplete Metadata
PM = "PM"  # Perfect Match

def read_bibtex_entries(filepath):
    """Parse BibTeX file and return dict of entries by citation key"""
    with open(filepath, 'r') as f:
        content = f.read()

    entries = {}
    # Match @type{key, ... }
    pattern = r'@(\w+)\{([^,]+),\s*(.*?)\n\}'
    for match in re.finditer(pattern, content, re.DOTALL):
        entry_type, key, fields = match.groups()
        entries[key] = {
            'type': entry_type,
            'key': key,
            'raw': match.group(0),
            'fields': {}
        }

        # Parse fields
        field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'
        for field_match in re.finditer(field_pattern, fields):
            field_name, field_value = field_match.groups()
            entries[key]['fields'][field_name] = field_value.strip()

    return entries

def read_test_input(filepath):
    """Parse test input file to get citation mappings"""
    citations = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Format: "number. informal citation text"
            match = re.match(r'(\d+)\.\s*(.+)', line)
            if match:
                citation_num = int(match.group(1))
                informal_text = match.group(2)
                citations[citation_num] = informal_text
    return citations

def normalize_string(s):
    """Normalize string for comparison: lowercase, remove punctuation, extra spaces"""
    s = s.lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def match_papers(ground_truth, output_entry):
    """Check if output entry matches ground truth paper"""
    gt_title = normalize_string(ground_truth['fields'].get('title', ''))
    gt_author = normalize_string(ground_truth['fields'].get('author', ''))
    gt_year = ground_truth['fields'].get('year', '')

    out_title = normalize_string(output_entry['fields'].get('title', ''))
    out_author = normalize_string(output_entry['fields'].get('author', ''))
    out_year = output_entry['fields'].get('year', '')

    # Match by title similarity (Jaccard similarity on words)
    def jaccard_similarity(s1, s2):
        words1 = set(s1.split())
        words2 = set(s2.split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)

    title_sim = jaccard_similarity(gt_title, out_title)

    # Papers match if title similarity > 0.7 and year matches
    if title_sim > 0.7 and gt_year == out_year:
        return True, title_sim

    return False, title_sim

def classify_entry(citation_num, informal_citation, ground_truth, output_entry):
    """
    Classify a single citation result using 8-category framework.
    Returns: (category, justification, details)
    """

    # If no output entry, it's Not Found
    if output_entry is None:
        return NF, "No BibTeX entry found in output file", {}

    # Check if output entry exists in DBLP
    # For now, assume all entries in output are real papers (we'd need to verify this separately)

    # Check if it matches ground truth
    is_match, title_sim = match_papers(ground_truth, output_entry)

    if not is_match:
        # Wrong paper - check if it's possibly fabricated
        out_title = output_entry['fields'].get('title', '')
        out_author = output_entry['fields'].get('author', '')

        # Heuristic: if title is very generic or contains ERROR/UNKNOWN, might be fabricated
        if 'error' in out_title.lower() or 'unknown' in out_title.lower():
            return FP, f"Fabricated paper (suspicious title)", {
                'title': out_title,
                'title_sim': title_sim
            }

        return WP, f"Wrong paper (title similarity: {title_sim:.2f})", {
            'expected': ground_truth['fields'].get('title', '')[:60],
            'got': out_title[:60],
            'title_sim': title_sim
        }

    # Paper matches - now check metadata quality
    gt_fields = ground_truth['fields']
    out_fields = output_entry['fields']

    # Check for incomplete authors
    out_author = out_fields.get('author', '')
    if 'unknown' in out_author.lower() or 'and others' in out_author.lower():
        return IA, "Incomplete author list (honest incompleteness)", {
            'author': out_author
        }

    # Check for fabricated metadata (invented fields)
    # This is hard to detect automatically - would need external verification
    # For now, we'll focus on corrupted metadata

    # Check for corrupted metadata (typos, wrong values)
    issues = []

    # Check DOI
    gt_doi = gt_fields.get('doi', '')
    out_doi = out_fields.get('doi', '')
    if gt_doi and out_doi and gt_doi != out_doi:
        issues.append(f"DOI mismatch: {out_doi} vs {gt_doi}")

    # Check pages
    gt_pages = gt_fields.get('pages', '')
    out_pages = out_fields.get('pages', '')
    if gt_pages and out_pages and gt_pages != out_pages:
        issues.append(f"Pages mismatch: {out_pages} vs {gt_pages}")

    # Check year (should already match from earlier check, but verify)
    gt_year = gt_fields.get('year', '')
    out_year = out_fields.get('year', '')
    if gt_year != out_year:
        issues.append(f"Year mismatch: {out_year} vs {gt_year}")

    # Check author names for corruption (not missing, but wrong)
    gt_author = normalize_string(gt_fields.get('author', ''))
    out_author_norm = normalize_string(out_author)
    author_sim = len(set(gt_author.split()).intersection(set(out_author_norm.split()))) / max(len(set(gt_author.split())), 1)
    if author_sim < 0.8 and 'unknown' not in out_author.lower():
        issues.append(f"Author corruption (similarity: {author_sim:.2f})")

    if issues:
        return CM, f"Corrupted metadata: {', '.join(issues)}", {
            'issues': issues
        }

    # Check for incomplete metadata (missing fields)
    missing_fields = []
    for field in ['doi', 'pages', 'venue']:
        if field in gt_fields and gt_fields[field] and field not in out_fields:
            missing_fields.append(field)

    if missing_fields:
        return IM, f"Incomplete metadata: missing {', '.join(missing_fields)}", {
            'missing': missing_fields
        }

    # Perfect match!
    return PM, "Perfect match with ground truth", {}

def find_output_entry(citation_num, output_entries, informal_citation, ground_truth):
    """
    Find the corresponding output entry for a citation.
    Uses multiple strategies:
    1. Citation key matching (e.g., Grassi2025)
    2. Title similarity matching
    3. Author+year matching
    """

    # Strategy 1: Extract expected citation key from ground truth
    gt_key = ground_truth['key']
    if gt_key in output_entries:
        return output_entries[gt_key]

    # Strategy 2: Find by title similarity
    gt_title = normalize_string(ground_truth['fields'].get('title', ''))
    gt_year = ground_truth['fields'].get('year', '')

    best_match = None
    best_sim = 0.0

    for key, entry in output_entries.items():
        out_title = normalize_string(entry['fields'].get('title', ''))
        out_year = entry['fields'].get('year', '')

        # Calculate title similarity
        words_gt = set(gt_title.split())
        words_out = set(out_title.split())
        if words_gt and words_out:
            jaccard = len(words_gt.intersection(words_out)) / len(words_gt.union(words_out))
            if jaccard > best_sim and out_year == gt_year:
                best_sim = jaccard
                best_match = entry

    # If we found a good match (>0.7 similarity), return it
    if best_sim > 0.7:
        return best_match

    # No match found
    return None

def main():
    base_path = Path('/Users/szeider/git/mcp-dblp/evaluation')

    print("=" * 80)
    print("MCP-DBLP EXPERIMENT EVALUATION")
    print("=" * 80)
    print()

    # Read all input files
    print("Loading data files...")

    # Test inputs
    test_input_1 = read_test_input(base_path / 'data' / 'test_input_v2_batch1.txt')
    test_input_2 = read_test_input(base_path / 'data' / 'test_input_v2_batch2.txt')
    test_input_3 = read_test_input(base_path / 'data' / 'test_input_v2_batch3.txt')
    all_test_input = {**test_input_1, **test_input_2, **test_input_3}

    # Ground truth
    ground_truth = read_bibtex_entries(base_path / 'ground_truth' / 'ground_truth.bib')

    # Read ground truth metadata to get correct mapping
    import csv
    gt_mapping = {}  # citation_num -> dblp_key
    with open(base_path / 'ground_truth' / 'ground_truth_metadata_regenerated.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            citation_num = int(row['index'])
            dblp_key = row['key']
            # BibTeX file uses DBLP: prefix
            gt_mapping[citation_num] = f"DBLP:{dblp_key}"

    # Control outputs
    control_1 = read_bibtex_entries(base_path / 'data' / 'control_output_v2_batch1.bib')
    control_2 = read_bibtex_entries(base_path / 'data' / 'control_output_v2_batch2.bib')
    control_3 = read_bibtex_entries(base_path / 'data' / 'control_output_v2_batch3.bib')
    all_control = {**control_1, **control_2, **control_3}

    # Treatment outputs
    treatment_1 = read_bibtex_entries(base_path / 'data' / 'treatment_output_v3_batch1.bib')
    treatment_2 = read_bibtex_entries(base_path / 'data' / 'treatment_output_v3_batch2.bib')
    treatment_3 = read_bibtex_entries(base_path / 'data' / 'treatment_output_v3_batch3.bib')
    all_treatment = {**treatment_1, **treatment_2, **treatment_3}

    print(f"Loaded {len(all_test_input)} test citations")
    print(f"Loaded {len(ground_truth)} ground truth entries")
    print(f"Loaded {len(gt_mapping)} ground truth mappings")
    print(f"Loaded {len(all_control)} control output entries")
    print(f"Loaded {len(all_treatment)} treatment output entries")
    print()

    # Perform evaluation
    print("Evaluating all 104 citations...")
    print("=" * 80)
    print()

    control_results = {}
    treatment_results = {}

    for i in range(1, 105):
        informal = all_test_input.get(i, f"[Missing citation {i}]")

        # Get corresponding ground truth entry using metadata mapping
        if i not in gt_mapping:
            print(f"WARNING: No ground truth mapping for citation {i}")
            continue

        gt_key = gt_mapping[i]
        if gt_key not in ground_truth:
            print(f"WARNING: Ground truth key {gt_key} not found in BibTeX file")
            continue

        gt_entry = ground_truth[gt_key]

        # Find corresponding entries in control and treatment outputs
        control_entry = find_output_entry(i, all_control, informal, gt_entry)
        treatment_entry = find_output_entry(i, all_treatment, informal, gt_entry)

        # Classify
        control_cat, control_just, control_details = classify_entry(i, informal, gt_entry, control_entry)
        treatment_cat, treatment_just, treatment_details = classify_entry(i, informal, gt_entry, treatment_entry)

        control_results[i] = (control_cat, control_just, control_details)
        treatment_results[i] = (treatment_cat, treatment_just, treatment_details)

        # Print per-citation results
        print(f"Citation {i}: {informal}")
        print(f"  Ground Truth: {gt_entry['fields'].get('author', 'NO AUTHOR')[:40]} - {gt_entry['fields'].get('title', 'NO TITLE')[:60]}")
        print(f"  Control: [{control_cat}] {control_just}")
        if control_details:
            for k, v in control_details.items():
                if isinstance(v, str):
                    print(f"    {k}: {v[:80]}")
        print(f"  Treatment: [{treatment_cat}] {treatment_just}")
        if treatment_details:
            for k, v in treatment_details.items():
                if isinstance(v, str):
                    print(f"    {k}: {v[:80]}")
        print()

    # Generate summary statistics
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print()

    control_counts = Counter([r[0] for r in control_results.values()])
    treatment_counts = Counter([r[0] for r in treatment_results.values()])

    categories = [NF, WP, FP, FM, CM, IA, IM, PM]

    print("Frequency Distribution:")
    print()
    print(f"{'Category':<10} {'Description':<30} {'Control':<10} {'Treatment':<10}")
    print("-" * 70)

    descriptions = {
        NF: "Not Found",
        WP: "Wrong Paper",
        FP: "Fabricated Paper",
        FM: "Fabricated Metadata",
        CM: "Corrupted Metadata",
        IA: "Incomplete Author",
        IM: "Incomplete Metadata",
        PM: "Perfect Match"
    }

    for cat in categories:
        desc = descriptions[cat]
        ctrl_count = control_counts.get(cat, 0)
        treat_count = treatment_counts.get(cat, 0)
        print(f"{cat:<10} {desc:<30} {ctrl_count:<10} {treat_count:<10}")

    print("-" * 70)
    print(f"{'TOTAL':<10} {'':<30} {sum(control_counts.values()):<10} {sum(treatment_counts.values()):<10}")
    print()

    # Calculate metrics
    control_found = 104 - control_counts.get(NF, 0)
    treatment_found = 104 - treatment_counts.get(NF, 0)

    control_perfect = control_counts.get(PM, 0)
    treatment_perfect = treatment_counts.get(PM, 0)

    print("Key Metrics:")
    print(f"  Coverage Rate (found/104):")
    print(f"    Control:   {control_found}/104 = {control_found/104*100:.1f}%")
    print(f"    Treatment: {treatment_found}/104 = {treatment_found/104*100:.1f}%")
    print()
    print(f"  Quality Rate (PM/found):")
    if control_found > 0:
        print(f"    Control:   {control_perfect}/{control_found} = {control_perfect/control_found*100:.1f}%")
    else:
        print(f"    Control:   N/A (no papers found)")
    if treatment_found > 0:
        print(f"    Treatment: {treatment_perfect}/{treatment_found} = {treatment_perfect/treatment_found*100:.1f}%")
    else:
        print(f"    Treatment: N/A (no papers found)")
    print()

    # Save detailed results
    output_file = base_path / 'data' / 'full_evaluation_results.txt'
    with open(output_file, 'w') as f:
        f.write("MCP-DBLP EXPERIMENT EVALUATION RESULTS\n")
        f.write("=" * 80 + "\n\n")

        f.write("PER-CITATION ANALYSIS\n")
        f.write("=" * 80 + "\n\n")

        for i in range(1, 105):
            informal = all_test_input.get(i, f"[Missing citation {i}]")
            if i not in gt_mapping:
                continue

            gt_key = gt_mapping[i]
            if gt_key not in ground_truth:
                continue

            gt_entry = ground_truth[gt_key]

            control_cat, control_just, control_details = control_results[i]
            treatment_cat, treatment_just, treatment_details = treatment_results[i]

            f.write(f"Citation {i}: {informal}\n")
            f.write(f"  Ground Truth: {gt_entry['key']}\n")
            f.write(f"    Author: {gt_entry['fields'].get('author', 'NO AUTHOR')}\n")
            f.write(f"    Title: {gt_entry['fields'].get('title', 'NO TITLE')}\n")
            f.write(f"    Year: {gt_entry['fields'].get('year', 'NO YEAR')}\n")
            f.write(f"  Control: [{control_cat}] {control_just}\n")
            if control_details:
                for k, v in control_details.items():
                    f.write(f"    {k}: {v}\n")
            f.write(f"  Treatment: [{treatment_cat}] {treatment_just}\n")
            if treatment_details:
                for k, v in treatment_details.items():
                    f.write(f"    {k}: {v}\n")
            f.write("\n")

        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("SUMMARY STATISTICS\n")
        f.write("=" * 80 + "\n\n")

        f.write("Frequency Distribution:\n\n")
        f.write(f"{'Category':<10} {'Description':<30} {'Control':<10} {'Treatment':<10}\n")
        f.write("-" * 70 + "\n")

        for cat in categories:
            desc = descriptions[cat]
            ctrl_count = control_counts.get(cat, 0)
            treat_count = treatment_counts.get(cat, 0)
            f.write(f"{cat:<10} {desc:<30} {ctrl_count:<10} {treat_count:<10}\n")

        f.write("-" * 70 + "\n")
        f.write(f"{'TOTAL':<10} {'':<30} {sum(control_counts.values()):<10} {sum(treatment_counts.values()):<10}\n\n")

        f.write("Key Metrics:\n")
        f.write(f"  Coverage Rate (found/104):\n")
        f.write(f"    Control:   {control_found}/104 = {control_found/104*100:.1f}%\n")
        f.write(f"    Treatment: {treatment_found}/104 = {treatment_found/104*100:.1f}%\n\n")
        f.write(f"  Quality Rate (PM/found):\n")
        if control_found > 0:
            f.write(f"    Control:   {control_perfect}/{control_found} = {control_perfect/control_found*100:.1f}%\n")
        else:
            f.write(f"    Control:   N/A (no papers found)\n")
        if treatment_found > 0:
            f.write(f"    Treatment: {treatment_perfect}/{treatment_found} = {treatment_perfect/treatment_found*100:.1f}%\n")
        else:
            f.write(f"    Treatment: N/A (no papers found)\n")

    print(f"Detailed results saved to: {output_file}")
    print()

if __name__ == '__main__':
    main()
