import re
import os

def parse_bib_file(file_path):
    """Parses the ground_truth.bib file to extract metadata."""
    entries = []
    if not os.path.exists(file_path):
        print(f"Error: Bib file not found at {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f
