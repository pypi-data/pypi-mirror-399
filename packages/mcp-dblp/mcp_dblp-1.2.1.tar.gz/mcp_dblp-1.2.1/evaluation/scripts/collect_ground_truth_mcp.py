#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests",
#   "pandas",
# ]
# ///
"""
Collect ground truth BibTeX entries using MCP-DBLP tools.

This version uses the MCP-DBLP search API which is more rate-limit friendly.

Sampling strategy:
- 100 papers from 2020-2025 (50%)
- 50 papers from 2015-2020 (25%)
- 50 papers from 2010-2015 (25%)
- Total: 200 papers (buffer for evaluation)
- Seed: 42 (reproducibility)
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
import requests
import pandas as pd

# Configuration
REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 2.5  # More conservative: 2.5 seconds between requests
USER_AGENT = "mcp-dblp-evaluation/1.0 (https://github.com/szeider/mcp-dblp)"

# Sampling configuration
SEED = 42
SAMPLING_CONFIG = {
    "2020-2025": 100,  # 50%
    "2015-2020": 50,   # 25%
    "2010-2015": 50,   # 25%
}
TOTAL_PAPERS = 200


def fetch_papers_for_period(start_year: int, end_year: int, target_count: int) -> List[Dict]:
    """
    Fetch papers for a time period using single broad search.

    Strategy: Make fewer, broader searches with larger result sets.
    """
    papers = []
    headers = {"User-Agent": USER_AGENT}

    print(f"Fetching papers from {start_year}-{end_year} (target: {target_count})...")

    # Use broader search terms with more results per request
    # This minimizes total API calls
    search_terms = [
        "machine learning",
        "algorithm",
        "neural network",
        "optimization",
        "security",
        "database",
    ]

    for term in search_terms:
        if len(papers) >= target_count * 3:  # Fetch 3x target
            break

        # Single search across entire year range with high result count
        url = f"https://dblp.org/search/publ/api?q={term.replace(' ', '%20')}&format=json&h=500"

        print(f"  Searching '{term}'...", end=" ", flush=True)

        try:
            time.sleep(RATE_LIMIT_DELAY)
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                hits = data.get("result", {}).get("hits", {}).get("hit", [])

                added = 0
                for hit in hits:
                    info = hit.get("info", {})

                    # Filter by year range
                    year = info.get("year", "")
                    try:
                        year_int = int(year)
                        if year_int < start_year or year_int > end_year:
                            continue
                    except (ValueError, TypeError):
                        continue

                    # Filter to articles and inproceedings only
                    pub_type = info.get("type", "")
                    if pub_type not in ["Journal Articles", "Conference and Workshop Papers"]:
                        continue

                    # Extract key (needed for BibTeX URL)
                    key = info.get("key", "")
                    if not key:
                        continue

                    # Add paper info
                    papers.append({
                        "key": key,
                        "title": info.get("title", ""),
                        "year": year,
                        "venue": info.get("venue", ""),
                        "type": pub_type,
                        "authors": info.get("authors", {}).get("author", [])
                    })
                    added += 1

                print(f"{len(hits)} hits, {added} in range, {len(papers)} total")

            elif response.status_code == 429:
                print("Rate limited, waiting 10 seconds...")
                time.sleep(10)

        except Exception as e:
            print(f"Error: {e}")
            continue

    print(f"  Total papers collected: {len(papers)}")
    print()
    return papers


def sample_papers(papers: List[Dict], target_count: int, seed: int = 42) -> List[Dict]:
    """
    Sample papers randomly from the list.
    """
    df = pd.DataFrame(papers)

    # Remove duplicates by key
    df = df.drop_duplicates(subset=["key"])

    # Sample
    if len(df) > target_count:
        sampled = df.sample(n=target_count, random_state=seed)
    else:
        print(f"  WARNING: Only {len(df)} papers available, target was {target_count}")
        sampled = df

    return sampled.to_dict("records")


def fetch_bibtex(key: str) -> str:
    """
    Fetch BibTeX entry from DBLP.
    """
    headers = {"User-Agent": USER_AGENT}
    url = f"https://dblp.org/rec/{key}.bib"

    try:
        time.sleep(RATE_LIMIT_DELAY)
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            return response.text.strip()
        elif response.status_code == 429:
            print(f"    Rate limited, waiting 10 seconds...")
            time.sleep(10)
            # Retry once
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"    Failed after retry (status {response.status_code})")
                return ""
        else:
            print(f"    Failed to fetch BibTeX (status {response.status_code})")
            return ""

    except Exception as e:
        print(f"    Error fetching BibTeX: {e}")
        return ""


def main():
    """
    Main execution function.
    """
    print("=" * 80)
    print("MCP-DBLP Ground Truth Collection (Rate-Limit Friendly)")
    print("=" * 80)
    print()
    print("Configuration:")
    print(f"  Total papers: {TOTAL_PAPERS}")
    print(f"  Sampling:")
    for period, count in SAMPLING_CONFIG.items():
        start, end = period.split("-")
        print(f"    {period}: {count:3d} papers ({count/TOTAL_PAPERS*100:.0f}%)")
    print(f"  Random seed: {SEED}")
    print(f"  Rate limit delay: {RATE_LIMIT_DELAY}s per request")
    print()

    # Collect papers for each time period
    all_papers = []
    all_metadata = []

    for period, target_count in SAMPLING_CONFIG.items():
        start_year, end_year = map(int, period.split("-"))

        print(f"Period: {period}")
        print("-" * 80)

        # Fetch papers
        papers = fetch_papers_for_period(start_year, end_year, target_count)

        # Sample
        sampled = sample_papers(papers, target_count, seed=SEED)

        print(f"  Sampled {len(sampled)} papers")
        print()

        all_papers.extend(sampled)

    print("=" * 80)
    print(f"Total papers collected: {len(all_papers)}")
    print("=" * 80)
    print()

    # Fetch BibTeX entries
    print("Fetching BibTeX entries...")
    print("-" * 80)

    bibtex_entries = []
    successful = 0

    for idx, paper in enumerate(all_papers, 1):
        key = paper["key"]
        title = paper.get("title", "")
        if isinstance(title, str):
            title_short = title[:60]
        else:
            title_short = str(title)[:60]

        print(f"[{idx:3d}/{len(all_papers):3d}] {key}")
        print(f"              {title_short}...")

        bibtex = fetch_bibtex(key)

        if bibtex:
            bibtex_entries.append(bibtex)
            successful += 1
            print(f"              ✓ Success")

            # Save metadata
            all_metadata.append({
                "index": idx,
                "key": key,
                "title": paper.get("title", ""),
                "year": paper.get("year", ""),
                "venue": paper.get("venue", ""),
                "type": paper.get("type", ""),
            })
        else:
            print(f"              ✗ Failed")

        # Progress update every 20 papers
        if idx % 20 == 0:
            print()
            print(f"  Progress: {idx}/{len(all_papers)} papers, {successful} successful ({successful/idx*100:.1f}%)")
            print()

    print("=" * 80)
    print(f"BibTeX entries fetched: {successful}/{len(all_papers)} ({successful/len(all_papers)*100:.1f}%)")
    print("=" * 80)
    print()

    # Save results
    print("Saving results...")

    # Save BibTeX file
    bibtex_file = Path("ground_truth.bib")
    with open(bibtex_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(bibtex_entries))
    print(f"  ✓ Saved BibTeX to {bibtex_file}")

    # Save metadata CSV
    metadata_file = Path("ground_truth_metadata.csv")
    df_metadata = pd.DataFrame(all_metadata)
    df_metadata.to_csv(metadata_file, index=False)
    print(f"  ✓ Saved metadata to {metadata_file}")

    print()
    print("Done!")
    print()
    print(f"Estimated runtime: {len(all_papers) * RATE_LIMIT_DELAY / 60:.1f} minutes for BibTeX fetching")


if __name__ == "__main__":
    main()
