#!/usr/bin/env python3
"""Web fetch tool for Gemini CLI"""

import re
import sys
import requests

def extract_urls(prompt):
    return re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', prompt)

def fetch_url(url):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'GeminiCLI/1.0'})
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error: {e}"

def web_fetch(prompt):
    urls = extract_urls(prompt)
    if not urls:
        return "No URLs found. Include at least one URL starting with http:// or https://"
    if len(urls) > 20:
        return "Too many URLs (max 20)"
    
    print(f"Fetch {len(urls)} URL(s)? (y/n): ", end='')
    if input().lower() != 'y':
        return "Cancelled"
    
    result = f"Processed {len(urls)} URL(s):\n\n"
    for url in urls:
        content = fetch_url(url)
        result += f"Source: {url}\nContent: {content[:500]}{'...' if len(content) > 500 else ''}\n\n"
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: web_fetch.py 'prompt with URLs'")
        sys.exit(1)
    print(web_fetch(" ".join(sys.argv[1:])))