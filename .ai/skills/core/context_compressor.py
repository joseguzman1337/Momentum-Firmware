#!/usr/bin/env python3
import sys
import json
import re

def compress_context(text, max_tokens=1000):
    """
    Lightweight context compressor.
    - Removes excessive whitespace
    - Summarizes repetitive log patterns
    - Truncates large file dumps while keeping headers/footers
    """
    # Remove comments and excessive newlines
    text = re.sub(r'//.*?
', '
', text)
    text = re.sub(r'
\s*
', '
', text)
    
    # If too long, keep the most important parts (start and end)
    lines = text.split('
')
    if len(lines) > 50:
        compressed = lines[:20] + ["... [TRUNCATED] ..."] + lines[-20:]
        return "
".join(compressed)
    
    return text

if __name__ == "__main__":
    if not sys.stdin.isatty():
        input_text = sys.stdin.read()
        print(compress_context(input_text))
