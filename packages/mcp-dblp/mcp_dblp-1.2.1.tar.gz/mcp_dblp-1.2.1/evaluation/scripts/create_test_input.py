#!/usr/bin/env python3
"""
Create obfuscated test input from ground truth BibTeX file.

Generates informal citations with varying difficulty levels:
- Easy: "Author et al. YEAR" or "Author YEAR"
- Medium: "Author's paper on TOPIC from YEAR"
- Hard: "Author venueYY" or partial title
- Very Hard: "That TOPIC paper by Author" or vague descriptions
"""

import re
import random
from pathlib import Path


def clean_latex(text):
    """Remove LaTeX escape sequences and clean text."""
    if not text:
        return text

    # Handle hyphens first (before general brace removal)
    text = re.sub(r'{-}', '-', text)  # {-} to hyphen (no backslash - literal braces)

    # Remove accent commands - handle various LaTeX accent formats
    # Pattern: \'{a}, \"o, \^e, \`a, \~n, etc.
    text = re.sub(r"\\['`\"^~=.]([a-zA-Z])", r'\1', text)
    # Pattern: \'{a} with optional braces, {\'a}, {\"o}, etc.
    text = re.sub(r"{\\['`\"^~=.]({)?([a-zA-Z])(})? ?}", r'\2', text)

    # Handle special characters
    text = re.sub(r'\\c{([a-zA-Z])}', r'\1', text)  # Cedilla \c{c}
    text = re.sub(r'{\\c{([a-zA-Z])}}', r'\1', text)  # {\\c{c}}

    # Remove remaining braces (after specific patterns handled)
    text = re.sub(r'{([^}]*)}', r'\1', text)  # Remove all braces with their contents

    # Clean up any remaining LaTeX artifacts
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remove remaining LaTeX commands
    text = re.sub(r'\\', '', text)  # Remove remaining backslashes

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def parse_bibtex_file(file_path):
    """Parse BibTeX file and extract entries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into individual entries
    entries = re.split(r'\n@', content)
    entries = ['@' + entry if not entry.startswith('@') else entry for entry in entries if entry.strip()]

    parsed_entries = []
    for entry in entries:
        # Extract entry type and key
        match = re.match(r'@(\w+)\{([^,]+),', entry)
        if not match:
            continue

        entry_type = match.group(1)
        key = match.group(2)

        # Extract fields
        fields = {}
        fields['type'] = entry_type
        fields['key'] = key

        # Extract author (use non-greedy match to closing },)
        author_match = re.search(r'author\s*=\s*\{(.+?)\},', entry, re.DOTALL)
        if author_match:
            fields['author'] = author_match.group(1).strip()

        # Extract title
        title_match = re.search(r'title\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', entry, re.DOTALL)
        if title_match:
            fields['title'] = title_match.group(1).strip()

        # Extract year
        year_match = re.search(r'year\s*=\s*\{([^}]+)\}', entry)
        if year_match:
            fields['year'] = year_match.group(1).strip()

        # Extract journal or booktitle (venue)
        journal_match = re.search(r'journal\s*=\s*\{([^}]+)\}', entry)
        booktitle_match = re.search(r'booktitle\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', entry, re.DOTALL)

        if journal_match:
            fields['venue'] = journal_match.group(1).strip()
        elif booktitle_match:
            fields['venue'] = booktitle_match.group(1).strip()

        parsed_entries.append(fields)

    return parsed_entries


def get_first_author(author_str):
    """Extract first author's last name and clean LaTeX."""
    if not author_str:
        return "Unknown"

    # Split by 'and' to get first author
    authors = author_str.split(' and ')
    first_author = authors[0].strip()

    # Try to extract last name (usually last word before newlines/special chars)
    # Handle format: "Last, First" or "First Last"
    if ',' in first_author:
        last_name = first_author.split(',')[0].strip()
    else:
        # Take last word
        words = first_author.split()
        last_name = words[-1] if words else first_author

    # Clean LaTeX escapes
    last_name = clean_latex(last_name)

    return last_name


def extract_topic_keywords(title):
    """Extract topic keywords from title."""
    if not title:
        return "topic"

    # Remove common words and extract meaningful keywords
    common_words = {'a', 'an', 'the', 'of', 'for', 'in', 'on', 'with', 'using', 'via', 'and', 'or', 'to', 'from'}

    # Clean title first
    clean_title = clean_latex(title)
    clean_title = re.sub(r'[^\w\s-]', ' ', clean_title)  # Remove punctuation

    words = clean_title.lower().split()
    keywords = [w for w in words if len(w) > 3 and w not in common_words]

    # Return first 1-2 meaningful keywords
    if len(keywords) >= 2:
        return ' '.join(keywords[:2])
    elif keywords:
        return keywords[0]
    else:
        return "topic"


def get_venue_abbrev(venue_str):
    """Extract venue abbreviation."""
    if not venue_str:
        return "conf"

    # Look for common conference/journal abbreviations
    venue_lower = venue_str.lower()

    # Common patterns
    if 'neurips' in venue_lower or 'nips' in venue_lower:
        return 'neurips'
    elif 'icml' in venue_lower:
        return 'icml'
    elif 'iclr' in venue_lower:
        return 'iclr'
    elif 'cvpr' in venue_lower:
        return 'cvpr'
    elif 'iccv' in venue_lower:
        return 'iccv'
    elif 'eccv' in venue_lower:
        return 'eccv'
    elif 'aaai' in venue_lower:
        return 'aaai'
    elif 'ijcai' in venue_lower:
        return 'ijcai'
    elif 'acl' in venue_lower:
        return 'acl'
    elif 'emnlp' in venue_lower:
        return 'emnlp'
    elif 'sigmod' in venue_lower:
        return 'sigmod'
    elif 'vldb' in venue_lower:
        return 'vldb'
    elif 'kdd' in venue_lower:
        return 'kdd'
    else:
        # Extract first word or acronym
        words = venue_str.split()
        if words:
            first_word = re.sub(r'[^\w]', '', words[0])
            return first_word[:6].lower()
        return 'conf'


def create_obfuscated_citation(entry, difficulty):
    """Create an obfuscated citation based on difficulty level."""
    author = get_first_author(entry.get('author', ''))
    year = entry.get('year', '????')
    title = entry.get('title', '')
    venue = entry.get('venue', '')

    topic = extract_topic_keywords(title)
    venue_abbrev = get_venue_abbrev(venue)
    year_short = year[-2:] if len(year) >= 2 else year

    if difficulty == 'easy':
        # "Author et al. YEAR" or "Author YEAR"
        if random.random() < 0.7:
            return f"{author} et al. {year}"
        else:
            return f"{author} {year}"

    elif difficulty == 'medium':
        # "Author's paper on TOPIC from YEAR" or "TOPIC paper by Author YEAR"
        if random.random() < 0.5:
            return f"{author}'s paper on {topic} from {year}"
        else:
            return f"{topic} paper by {author} {year}"

    elif difficulty == 'hard':
        # "Author venueYY" or partial title (4-6 words, complete)
        if random.random() < 0.6:
            # NO apostrophe in year abbreviation
            return f"{author} {venue_abbrev}{year_short}"
        else:
            # Partial title - ensure complete words
            clean_title = clean_latex(title)
            words = clean_title.split()

            # Get 4-6 words (or all if fewer)
            num_words = min(random.randint(4, 6), len(words))
            partial = ' '.join(words[:num_words])

            # If we cut off mid-sentence, ensure it ends on a word boundary
            # and isn't too generic
            if len(words) > num_words:
                # Add "..." to indicate truncation
                return f"{partial}..."
            else:
                return partial

    else:  # very_hard
        # "That TOPIC paper by Author" or very vague (but always include author and/or year)
        templates = [
            f"that {topic} paper by {author}",
            f"{author}'s {topic} work from {year}",
            f"the {topic} paper from {year}",
            f"{author}'s {venue_abbrev} paper on {topic}",
        ]
        return random.choice(templates)


def main():
    # Set random seed for reproducibility
    random.seed(42)

    # Paths
    ground_truth_path = Path(__file__).parent / 'ground_truth.bib'
    output_dir = Path(__file__).parent / 'data'
    output_path = output_dir / 'test_input.txt'

    # Create output directory if needed
    output_dir.mkdir(exist_ok=True)

    # Parse BibTeX file
    print(f"Parsing {ground_truth_path}...")
    entries = parse_bibtex_file(ground_truth_path)
    print(f"Found {len(entries)} entries")

    # Validate all entries have required fields
    valid_entries = []
    for entry in entries:
        if 'author' in entry and 'year' in entry and 'title' in entry:
            valid_entries.append(entry)
        else:
            print(f"Warning: Skipping incomplete entry {entry.get('key', 'unknown')}")

    print(f"Using {len(valid_entries)} valid entries")

    # Create difficulty distribution (approximately equal)
    n = len(valid_entries)
    difficulties = ['easy'] * (n // 4) + ['medium'] * (n // 4) + ['hard'] * (n // 4) + ['very_hard'] * (n // 4)
    # Add remaining to balance
    difficulties += ['easy'] * (n - len(difficulties))

    # Shuffle to randomize difficulty order
    random.shuffle(difficulties)

    # Generate obfuscated citations
    print("Generating obfuscated citations...")
    citations = []
    for i, (entry, diff) in enumerate(zip(valid_entries, difficulties), 1):
        citation = create_obfuscated_citation(entry, diff)
        citations.append(f"{i}. {citation}")

    # Write to file
    print(f"Writing to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(citations) + '\n')

    print(f"✅ Created {len(citations)} obfuscated citations in {output_path}")

    # Print difficulty distribution
    from collections import Counter
    diff_counts = Counter(difficulties[:len(valid_entries)])
    print(f"\nDifficulty distribution:")
    for diff, count in sorted(diff_counts.items()):
        print(f"  {diff}: {count}")


if __name__ == '__main__':
    main()
