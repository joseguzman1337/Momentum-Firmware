#!/usr/bin/env python3
import sys
import os

def audit_furi_calls(file_path):
    """
    Skill: Audit Furi Core OS calls for safety.
    Checks for:
    - Missing furi_check after allocations
    - Potential NULL dereferences in record_open
    """
    findings = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "furi_record_open" in line and "furi_check" not in lines[i+1 if i+1 < len(lines) else i]:
                findings.append(f"L{i+1}: Potential unchecked record access")
            if "malloc" in line and "furi_check" not in lines[i+1 if i+1 < len(lines) else i]:
                findings.append(f"L{i+1}: Unchecked heap allocation")
    return findings

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            if os.path.exists(path):
                results = audit_furi_calls(path)
                print(f"--- Findings for {path} ---")
                print("
".join(results) if results else "No issues found.")
