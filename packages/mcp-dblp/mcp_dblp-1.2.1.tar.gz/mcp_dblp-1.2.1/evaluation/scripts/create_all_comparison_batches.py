#!/usr/bin/env python3
"""
Create comparison batches for all 104 citations.
Match by citation order from test_input.txt
"""

import re
from pathlib import Path

def parse_bibtex_file(file_path):
    """Parse BibTeX file into ordered list of entries."""
    with open(file_path, 'r') as f:
        content = f.read()

    entries = []
    current = []
    in_entry = False

    for line in content.split('\n'):
        if line.strip().startswith('@'):
            if current and in_entry:
                entries.append('\n'.join(current))
                current = []
            current.append(line)
            in_entry = True
        elif in_entry:
            current.append(line)
            if line.strip() == '}':
                entries.append('\n'.join(current))
                current = []
                in_entry = False
        elif line.strip().startswith('%'):
            # Comment line, could indicate NOT FOUND
            if 'NOT FOUND' in line:
                if current:
                    entries.append('\n'.join(current))
                entries.append(line)
                current = []

    if current:
        entries.append('\n'.join(current))

    return entries

def load_citations():
    """Load test input citations."""
    with open('/Users/szeider/git/mcp-dblp/evaluation/data/test_input.txt') as f:
        citations = []
        for line in f:
            match = re.match(r'^\d+\.\s+(.+)$', line.strip())
            if match:
                citations.append(match.group(1))
    return citations

def main():
    base = Path('/Users/szeider/git/mcp-dblp/evaluation')

    # Load all data
    citations = load_citations()
    gt_entries = parse_bibtex_file(base / 'ground_truth.bib')
    control_entries = parse_bibtex_file(base / 'data/control_output.bib')
    treatment_entries = parse_bibtex_file(base / 'data/treatment_output.bib')

    print(f"Citations: {len(citations)}")
    print(f"Ground truth: {len(gt_entries)}")
    print(f"Control: {len(control_entries)} blocks")
    print(f"Treatment: {len(treatment_entries)} blocks")

    # Create mapping files for manual review
    output_dir = base / 'data' / 'manual_comparison'
    output_dir.mkdir(exist_ok=True)

    # Export structured comparison file
    with open(output_dir / 'all_comparisons.txt', 'w') as f:
        for i in range(len(citations)):
            f.write(f"\n{'='*80}\n")
            f.write(f"CITATION {i+1}: {citations[i]}\n")
            f.write(f"{'='*80}\n\n")

            f.write("GROUND TRUTH:\n")
            if i < len(gt_entries):
                f.write(gt_entries[i])
            else:
                f.write("(no entry)")
            f.write("\n\n")

            f.write("CONTROL OUTPUT:\n")
            if i < len(control_entries):
                f.write(control_entries[i])
            else:
                f.write("(no entry)")
            f.write("\n\n")

            f.write("TREATMENT OUTPUT:\n")
            if i < len(treatment_entries):
                f.write(treatment_entries[i])
            else:
                f.write("(no entry)")
            f.write("\n\n")

    print(f"\nCreated {output_dir}/all_comparisons.txt")
    print(f"Contains all {len(citations)} citation comparisons")

    # Create batches of 20 for GPTT processing
    batch_size = 20
    for batch_num in range(0, len(citations), batch_size):
        end_idx = min(batch_num + batch_size, len(citations))
        batch_file = output_dir / f'batch_{batch_num//batch_size + 1}_citations_{batch_num+1}-{end_idx}.txt'

        with open(batch_file, 'w') as f:
            for i in range(batch_num, end_idx):
                f.write(f"\n## CITATION {i+1}: \"{citations[i]}\"\n\n")

                f.write("GROUND TRUTH:\n```\n")
                if i < len(gt_entries):
                    f.write(gt_entries[i].strip())
                else:
                    f.write("(no entry)")
                f.write("\n```\n\n")

                f.write("CONTROL OUTPUT:\n```\n")
                if i < len(control_entries):
                    entry = control_entries[i].strip()
                    if entry.startswith('%'):
                        f.write(f"NOT FOUND{entry}")
                    else:
                        f.write(entry)
                else:
                    f.write("(no entry)")
                f.write("\n```\n\n")

                f.write("TREATMENT OUTPUT:\n```\n")
                if i < len(treatment_entries):
                    entry = treatment_entries[i].strip()
                    if entry.startswith('%'):
                        f.write(f"NOT FOUND{entry}")
                    else:
                        f.write(entry)
                else:
                    f.write("(no entry)")
                f.write("\n```\n\n")

        print(f"Created batch file: {batch_file.name}")

if __name__ == '__main__':
    main()
