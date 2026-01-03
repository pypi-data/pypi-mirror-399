Here is the Python script `regenerate_test_input_v2.py`. It parses the ground truth BibTeX file, applies the specific logic to the 31 target citations to make them fair but challenging, and writes the result to `test_input_v2.txt`.

```python
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