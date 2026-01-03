#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pandas",
# ]
# ///
"""
Filter ground truth dataset to remove low-quality entries.

Based on Gemini 3 Pro analysis, remove:
- Editorials and acknowledgments
- Corrections and retractions
- Duplicate entries
"""

import pandas as pd
from pathlib import Path

# Indices to remove (1-indexed as reported by Gemini)
INDICES_TO_REMOVE = [5, 24, 38, 60, 69, 83, 104, 166, 189, 195]

def filter_bibtex():
    """Filter BibTeX file by removing entries at specified indices."""
    print("Filtering ground_truth.bib...")

    # Read BibTeX file
    with open("ground_truth.bib", "r", encoding="utf-8") as f:
        content = f.read()

    # Split into individual entries
    entries = content.split("\n\n")
    print(f"  Total entries: {len(entries)}")

    # Remove entries at specified indices (convert to 0-indexed)
    filtered_entries = [
        entry for i, entry in enumerate(entries, 1)
        if i not in INDICES_TO_REMOVE
    ]
    print(f"  Removed: {len(entries) - len(filtered_entries)}")
    print(f"  Remaining: {len(filtered_entries)}")

    # Save filtered BibTeX
    backup_file = Path("ground_truth_old.bib")
    Path("ground_truth.bib").rename(backup_file)
    print(f"  Backed up original to {backup_file}")

    with open("ground_truth.bib", "w", encoding="utf-8") as f:
        f.write("\n\n".join(filtered_entries))
    print(f"  Saved filtered to ground_truth.bib")
    print()

    return len(filtered_entries)


def filter_metadata():
    """Filter metadata CSV by removing rows at specified indices."""
    print("Filtering ground_truth_metadata.csv...")

    # Read CSV
    df = pd.read_csv("ground_truth_metadata.csv")
    print(f"  Total rows: {len(df)}")

    # Filter rows (indices are 1-indexed in CSV, matching paper numbers)
    df_filtered = df[~df['index'].isin(INDICES_TO_REMOVE)]
    print(f"  Removed: {len(df) - len(df_filtered)}")
    print(f"  Remaining: {len(df_filtered)}")

    # Reindex to maintain sequential numbering
    df_filtered = df_filtered.copy()
    df_filtered['index'] = range(1, len(df_filtered) + 1)

    # Save filtered metadata
    backup_file = Path("ground_truth_metadata_old.csv")
    Path("ground_truth_metadata.csv").rename(backup_file)
    print(f"  Backed up original to {backup_file}")

    df_filtered.to_csv("ground_truth_metadata.csv", index=False)
    print(f"  Saved filtered to ground_truth_metadata.csv")
    print()

    return len(df_filtered)


def main():
    print("=" * 80)
    print("Ground Truth Dataset Cleanup")
    print("=" * 80)
    print()
    print("Removing problematic entries identified by Gemini 3 Pro:")
    print()
    print("  Editorials/Acknowledgments:")
    print("    - Index 5:   journals/algorithms/Jansson25")
    print("    - Index 38:  journals/spm/Edwards21e")
    print("    - Index 60:  conf/aaaiss/MartinH20")
    print("    - Index 69:  journals/algorithms/Office20")
    print("    - Index 83:  journals/algorithms/Rescigno25")
    print("    - Index 189: journals/biodb/GaudetMRABCKOY13")
    print()
    print("  Corrections/Retractions:")
    print("    - Index 24:  journals/esi/Pradeepkumar23")
    print("    - Index 166: journals/nn/MarichalGM13")
    print("    - Index 195: journals/isci/KuoY10")
    print()
    print("  Duplicates:")
    print("    - Index 104: journals/algorithms/Office20 (duplicate of 69)")
    print()
    print("=" * 80)
    print()

    # Filter both files
    bibtex_count = filter_bibtex()
    metadata_count = filter_metadata()

    print("=" * 80)
    print("Cleanup Complete")
    print("=" * 80)
    print()
    print(f"Final dataset size: {metadata_count} papers")
    print()
    print("Files:")
    print("  - ground_truth.bib (filtered)")
    print("  - ground_truth_metadata.csv (filtered)")
    print("  - ground_truth_old.bib (backup)")
    print("  - ground_truth_metadata_old.csv (backup)")
    print()


if __name__ == "__main__":
    main()
