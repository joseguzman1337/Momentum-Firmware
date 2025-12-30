#!/usr/bin/env python3
"""
Gemini CLI Automation Script for Momentum Firmware
Processes GitHub issues using Gemini CLI with proper context and checkpointing
"""

import subprocess
import json
import sys
from pathlib import Path

def get_open_issues():
    """Fetch open issues from GitHub"""
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--limit", "50", "--json", "number,title,labels"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching issues: {e}")
        return []

def filter_issues_for_gemini(issues):
    """Filter issues suitable for Gemini (complex, architectural, multi-component)"""
    gemini_issues = []
    
    # Keywords that indicate complex/architectural issues
    complex_keywords = [
        "architecture", "design", "refactor", "optimize", "performance",
        "integration", "api", "protocol", "system", "framework"
    ]
    
    for issue in issues:
        title_lower = issue["title"].lower()
        
        # Check if issue has complexity indicators
        if any(keyword in title_lower for keyword in complex_keywords):
            gemini_issues.append(issue)
            continue
            
        # Check labels
        labels = [label.get("name", "").lower() for label in issue.get("labels", [])]
        if any(label in ["enhancement", "feature", "architecture"] for label in labels):
            gemini_issues.append(issue)
    
    return gemini_issues

def run_gemini_on_issue(issue_number, issue_title):
    """Run Gemini CLI on a specific issue"""
    prompt = f"""Fix and implement a comprehensive solution for GitHub Issue #{issue_number}: {issue_title}

Please:
1. Analyze the issue thoroughly considering the entire codebase context
2. Design an optimal solution that fits the project architecture
3. Implement the fix with proper error handling and validation
4. Ensure backward compatibility
5. Add appropriate comments and documentation
6. Generate a commit message that includes "Closes #{issue_number}"

<<<<<<< HEAD
<<<<<<< HEAD
Use checkpointing to allow easy rollback if needed.
=======
Use the /restore command if you need to rollback changes.
>>>>>>> origin/renovate/node-24.x
=======
Use the /restore command if you need to rollback changes.
=======
Use checkpointing to allow easy rollback if needed.
>>>>>>> origin/dev
>>>>>>> origin/deepseek-fix/vulnerability-18-1767032628
"""
    
    print(f"\n{'='*60}")
    print(f"Processing Issue #{issue_number}: {issue_title}")
    print(f"{'='*60}\n")
    
    try:
<<<<<<< HEAD
<<<<<<< HEAD
        # Run Gemini with checkpointing enabled
        result = subprocess.run(
            ["gemini", "--checkpointing", "-p", prompt],
=======
        # Run Gemini with output format for parsing
        result = subprocess.run(
            ["gemini", "-p", prompt, "-o", "json"],
>>>>>>> origin/renovate/node-24.x
=======
        # Run Gemini with output format for parsing
        result = subprocess.run(
            ["gemini", "-p", prompt, "-o", "json"],
=======
        # Run Gemini with checkpointing enabled
        result = subprocess.run(
            ["gemini", "--checkpointing", "-p", prompt],
>>>>>>> origin/dev
>>>>>>> origin/deepseek-fix/vulnerability-18-1767032628
            cwd="/Users/x/x/Momentum-Firmware",
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⚠️  Timeout processing issue #{issue_number}")
        return False
    except Exception as e:
        print(f"❌ Error processing issue #{issue_number}: {e}")
        return False

def main():
    print("🤖 Gemini CLI Automation for Momentum Firmware")
    print("=" * 60)
    
    # Fetch issues
    print("\n📋 Fetching open issues...")
    all_issues = get_open_issues()
    print(f"Found {len(all_issues)} total open issues")
    
    # Filter for Gemini-suitable issues
    gemini_issues = filter_issues_for_gemini(all_issues)
    print(f"Identified {len(gemini_issues)} issues suitable for Gemini")
    
    if not gemini_issues:
        print("No suitable issues found for Gemini processing")
        return
    
    # Process each issue
    successful = 0
    failed = 0
    
    for issue in gemini_issues[:5]:  # Process first 5 to avoid overwhelming
        success = run_gemini_on_issue(issue["number"], issue["title"])
        if success:
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Summary:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
