#!/usr/bin/env python3
"""
AI Fix Generator for Security Vulnerabilities
Uses Claude (Anthropic) or Codex (OpenAI) to generate secure code fixes.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Determine which AI agent to use
AGENT = os.getenv('AGENT', 'claude')
VULN_FILE = os.getenv('VULN_FILE', '')
VULN_LINE = int(os.getenv('VULN_LINE', '0'))
VULN_RULE = os.getenv('VULN_RULE', '')
ISSUE_NUMBER = os.getenv('ISSUE_NUMBER', '')

def read_file_context(file_path, line_num, context_lines=20):
    """Read the vulnerable file with context around the issue."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        start = max(0, line_num - context_lines)
        end = min(len(lines), line_num + context_lines)
        
        context = {
            'before': ''.join(lines[start:line_num-1]),
            'vulnerable_line': lines[line_num-1] if line_num > 0 else '',
            'after': ''.join(lines[line_num:end]),
            'full_file': ''.join(lines)
        }
        return context
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def generate_fix_with_claude(context, rule):
    """Generate a fix using Claude (Anthropic)."""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        prompt = f"""You are a security expert fixing a vulnerability in C/C++ code.

**Vulnerability**: {rule}
**File**: {VULN_FILE}
**Line**: {VULN_LINE}

**Code Context**:
```c
{context['before']}
>>> {context['vulnerable_line'].strip()}  // VULNERABLE LINE
{context['after']}
```

**Task**: Provide a secure fix for this vulnerability. Return ONLY the corrected code section that should replace the vulnerable area. Include comments explaining the security improvement.

**Requirements**:
1. Fix must eliminate the security vulnerability
2. Maintain existing functionality
3. Follow Flipper Zero coding standards
4. Add security comments
5. No breaking changes

**Output Format**: Return only the fixed code, no explanations outside the code."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}")
        return None

def generate_fix_with_codex(context, rule):
    """Generate a fix using OpenAI Codex."""
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""Fix this security vulnerability in C/C++ code:

Vulnerability: {rule}
File: {VULN_FILE}
Line: {VULN_LINE}

Code:
```c
{context['before']}
{context['vulnerable_line']}  // VULNERABLE
{context['after']}
```

Provide a secure fix with comments. Return only the corrected code."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a security-focused code reviewer fixing vulnerabilities in embedded C/C++ code."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def apply_fix(file_path, fixed_code):
    """Apply the AI-generated fix to the file."""
    try:
        # Extract code from markdown if present
        if '```' in fixed_code:
            code_blocks = fixed_code.split('```')
            for block in code_blocks:
                if block.strip() and not block.startswith('c'):
                    continue
                fixed_code = block.replace('c\n', '', 1).strip()
                break
        
        # For now, write the fix to a patch file for manual review
        patch_file = f"/tmp/fix_{ISSUE_NUMBER}.patch"
        with open(patch_file, 'w') as f:
            f.write(f"# AI-generated fix for {VULN_FILE}:{VULN_LINE}\n")
            f.write(f"# Rule: {VULN_RULE}\n")
            f.write(f"# Agent: {AGENT}\n\n")
            f.write(fixed_code)
        
        print(f"✅ Fix generated and saved to {patch_file}")
        print(f"\n📝 Proposed fix:\n{fixed_code}")
        
        # TODO: Implement automatic application with backup
        # For safety, require manual review for now
        
        return True
    except Exception as e:
        print(f"Error applying fix: {e}")
        return False

def main():
    print(f"🤖 AI Fix Generator ({AGENT.upper()})")
    print(f"📁 File: {VULN_FILE}")
    print(f"📍 Line: {VULN_LINE}")
    print(f"🔍 Rule: {VULN_RULE}")
    
    if not VULN_FILE or not os.path.exists(VULN_FILE):
        print(f"❌ File not found: {VULN_FILE}")
        sys.exit(1)
    
    print(f"\n📖 Reading file context...")
    context = read_file_context(VULN_FILE, VULN_LINE)
    
    if not context:
        print("❌ Failed to read file context")
        sys.exit(1)
    
    print(f"\n🔧 Generating fix with {AGENT}...")
    
    if AGENT == 'claude':
        fixed_code = generate_fix_with_claude(context, VULN_RULE)
    else:
        fixed_code = generate_fix_with_codex(context, VULN_RULE)
    
    if not fixed_code:
        print("❌ Failed to generate fix")
        sys.exit(1)
    
    print(f"\n✨ Applying fix...")
    if apply_fix(VULN_FILE, fixed_code):
        print(f"\n✅ Fix complete! Review the changes and commit.")
    else:
        print(f"\n❌ Failed to apply fix")
        sys.exit(1)

if __name__ == "__main__":
    main()
