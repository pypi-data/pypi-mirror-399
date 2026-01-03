#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pandas",
# ]
# ///
"""
Rebalance ground truth dataset to 50/50 conferences/journals.

Strategy:
- Keep all 52 conferences
- Sample 52 journals (stratified by time period to match conferences)
- Use seed=42 for reproducibility
"""

import pandas as pd
from pathlib import Path

SEED = 42


def rebalance_dataset():
    """Rebalance to 50/50 conferences/journals."""
    print("=" * 80)
    print("Ground Truth Dataset Rebalancing")
    print("=" * 80)
    print()

    # Read current dataset
    df = pd.read_csv("ground_truth_metadata.csv")

    print("Current Distribution:")
    print("-" * 80)
    conf = df[df['type'] == 'Conference and Workshop Papers']
    jour = df[df['type'] == 'Journal Articles']
    print(f"  Conferences: {len(conf):3d} ({len(conf)/len(df)*100:5.1f}%)")
    print(f"  Journals:    {len(jour):3d} ({len(jour)/len(df)*100:5.1f}%)")
    print(f"  Total:       {len(df):3d}")
    print()

    # Target: Match number of conferences
    target_journals = len(conf)

    print(f"Target: {len(conf)} conferences + {target_journals} journals = {len(conf) + target_journals} papers (50/50)")
    print()

    # Analyze conference temporal distribution
    conf_copy = conf.copy()
    conf_copy['year_int'] = pd.to_numeric(conf_copy['year'], errors='coerce')

    conf_2020_2025 = len(conf_copy[(conf_copy['year_int'] >= 2020) & (conf_copy['year_int'] <= 2025)])
    conf_2015_2019 = len(conf_copy[(conf_copy['year_int'] >= 2015) & (conf_copy['year_int'] < 2020)])
    conf_2010_2014 = len(conf_copy[(conf_copy['year_int'] >= 2010) & (conf_copy['year_int'] < 2015)])

    print("Conference Temporal Distribution:")
    print("-" * 80)
    print(f"  2020-2025: {conf_2020_2025:2d} papers ({conf_2020_2025/len(conf)*100:5.1f}%)")
    print(f"  2015-2019: {conf_2015_2019:2d} papers ({conf_2015_2019/len(conf)*100:5.1f}%)")
    print(f"  2010-2014: {conf_2010_2014:2d} papers ({conf_2010_2014/len(conf)*100:5.1f}%)")
    print()

    # Sample journals to match conference distribution by period
    print("Sampling Journals (stratified by period to match conferences):")
    print("-" * 80)

    jour_copy = jour.copy()
    jour_copy['year_int'] = pd.to_numeric(jour_copy['year'], errors='coerce')

    # Sample from each period
    jour_2020_2025 = jour_copy[(jour_copy['year_int'] >= 2020) & (jour_copy['year_int'] <= 2025)]
    jour_2015_2019 = jour_copy[(jour_copy['year_int'] >= 2015) & (jour_copy['year_int'] < 2020)]
    jour_2010_2014 = jour_copy[(jour_copy['year_int'] >= 2010) & (jour_copy['year_int'] < 2015)]

    sampled_journals = []

    if len(jour_2020_2025) >= conf_2020_2025:
        sample = jour_2020_2025.sample(n=conf_2020_2025, random_state=SEED)
        sampled_journals.append(sample)
        print(f"  2020-2025: {conf_2020_2025:2d} papers sampled from {len(jour_2020_2025):3d} available")
    else:
        print(f"  2020-2025: WARNING - Only {len(jour_2020_2025)} available, need {conf_2020_2025}")
        sampled_journals.append(jour_2020_2025)

    if len(jour_2015_2019) >= conf_2015_2019:
        sample = jour_2015_2019.sample(n=conf_2015_2019, random_state=SEED)
        sampled_journals.append(sample)
        print(f"  2015-2019: {conf_2015_2019:2d} papers sampled from {len(jour_2015_2019):3d} available")
    else:
        print(f"  2015-2019: WARNING - Only {len(jour_2015_2019)} available, need {conf_2015_2019}")
        sampled_journals.append(jour_2015_2019)

    if len(jour_2010_2014) >= conf_2010_2014:
        sample = jour_2010_2014.sample(n=conf_2010_2014, random_state=SEED)
        sampled_journals.append(sample)
        print(f"  2010-2014: {conf_2010_2014:2d} papers sampled from {len(jour_2010_2014):3d} available")
    else:
        print(f"  2010-2014: WARNING - Only {len(jour_2010_2014)} available, need {conf_2010_2014}")
        sampled_journals.append(jour_2010_2014)

    print()

    # Combine conferences + sampled journals
    jour_sampled = pd.concat(sampled_journals, ignore_index=True)
    df_balanced = pd.concat([conf, jour_sampled], ignore_index=True)

    # Sort by original index to maintain rough chronological order
    df_balanced = df_balanced.sort_values('index').reset_index(drop=True)

    # Reindex sequentially
    df_balanced['index'] = range(1, len(df_balanced) + 1)

    print("Rebalanced Distribution:")
    print("-" * 80)
    conf_new = df_balanced[df_balanced['type'] == 'Conference and Workshop Papers']
    jour_new = df_balanced[df_balanced['type'] == 'Journal Articles']
    print(f"  Conferences: {len(conf_new):3d} ({len(conf_new)/len(df_balanced)*100:5.1f}%)")
    print(f"  Journals:    {len(jour_new):3d} ({len(jour_new)/len(df_balanced)*100:5.1f}%)")
    print(f"  Total:       {len(df_balanced):3d}")
    print()

    # Extract BibTeX entries for selected papers
    print("Extracting BibTeX entries...")
    print("-" * 80)

    with open("ground_truth.bib", "r", encoding="utf-8") as f:
        content = f.read()

    entries = content.split("\n\n")

    # Get indices to keep (0-indexed for list)
    indices_to_keep = set(df_balanced['index'].tolist())

    # Filter BibTeX entries
    filtered_entries = [
        entry for i, entry in enumerate(entries, 1)
        if i in indices_to_keep
    ]

    print(f"  Filtered from {len(entries)} to {len(filtered_entries)} BibTeX entries")
    print()

    # Backup existing files
    print("Backing up files...")
    print("-" * 80)
    Path("ground_truth.bib").rename("ground_truth_190papers.bib")
    Path("ground_truth_metadata.csv").rename("ground_truth_metadata_190papers.csv")
    print("  ✓ Backed up ground_truth.bib → ground_truth_190papers.bib")
    print("  ✓ Backed up ground_truth_metadata.csv → ground_truth_metadata_190papers.csv")
    print()

    # Save rebalanced files
    print("Saving rebalanced dataset...")
    print("-" * 80)

    with open("ground_truth.bib", "w", encoding="utf-8") as f:
        f.write("\n\n".join(filtered_entries))
    print("  ✓ Saved ground_truth.bib")

    df_balanced.to_csv("ground_truth_metadata.csv", index=False)
    print("  ✓ Saved ground_truth_metadata.csv")
    print()

    print("=" * 80)
    print("Rebalancing Complete")
    print("=" * 80)
    print()
    print(f"Final dataset: {len(df_balanced)} papers (50% conferences, 50% journals)")
    print()
    print("Files:")
    print("  - ground_truth.bib (rebalanced, 104 papers)")
    print("  - ground_truth_metadata.csv (rebalanced, 104 papers)")
    print("  - ground_truth_190papers.bib (backup before rebalancing)")
    print("  - ground_truth_metadata_190papers.csv (backup before rebalancing)")
    print()

    return len(df_balanced)


if __name__ == "__main__":
    rebalance_dataset()
