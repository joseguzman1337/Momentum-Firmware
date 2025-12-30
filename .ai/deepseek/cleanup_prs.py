#!/usr/bin/env python3
import subprocess
import json
import time

def cleanup_and_reprocess():
    print("🧹 Fetching open DeepSeek PRs to close...")
    # Get all open PRs by the current user (assuming they are the bot's) or formatted as DeepSeek
    cmd = "gh pr list --state open --author \"@me\" --json number,title,headRefName,body"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Failed to fetch PRs")
        return

    prs = json.loads(result.stdout)
    print(f"📉 Found {len(prs)} open PRs to review.")
    
    for pr in prs:
        num = pr['number']
        title = pr['title']
        head = pr['headRefName']
        
        # Filter for DeepSeek PRs
        if "deepseek-fix/" in head:
            print(f"🚫 Closing PR #{num}: {title} (Obsolescent logic)")
            # Close the PR
            subprocess.run(f"gh pr close {num} --delete-branch", shell=True)
            
            # Extract task info to re-trigger
            # Branch naming: deepseek-fix/{rule_id}-{timestamp}
            # Title: Fix {rule_id}: ...
            # We can parse the Title or Head to get the ID back.
            # Example head: deepseek-fix/vulnerability-15-1767032414
            # We want "vulnerability-15"
            
            try:
                # remove prefix and timestamp
                parts = head.replace("deepseek-fix/", "").split('-')
                # Reconstruct ID (handles hyphens in rule names if any, though our format is simpler)
                # Actually, our format was f"issue-{issue_id}" or f"vulnerability-{issue_id}"
                # So we can just take the first two parts? No, timestamp is last.
                
                # Check if it starts with 'vulnerability' or 'issue'
                if head.startswith("deepseek-fix/vulnerability-"):
                    # Extract ID. 
                    # Format: deepseek-fix/vulnerability-15-1767...
                    # Split by '-'
                    items = head.split('-')
                    # index 0: deepseek
                    # index 1: fix/vulnerability
                    # index 2: 15
                    # index 3: timestamp
                    type_str = "vulnerability"
                    id_val = items[2] 
                    
                    # We need to construct the full CLI command from scratch, 
                    # but we are missing the file path/line number context that `reprocess.py` has.
                    # HOWEVER, we can't easily guess the file path/line without querying the vulnerability API again.
                    # So, the best strategy: Close the PRs, then RUN `reprocess.py` again.
                    # reprocess.py fetches ALL open vulnerabilities, effectively "re-queueing" them.
                    pass
                    
                elif head.startswith("deepseek-fix/issue-"):
                     # Same logic. Close PR. Run `process_issues.py` again.
                     pass
                     
            except Exception as e:
                print(f"⚠️ Error parsing PR ref {head}: {e}")

    print("✅ All obsolescent PRs closed.")
    print("🔄 Restarting full reprocessing sequence to apply NEW logic...")
    
    # Relaunch the processors
    subprocess.Popen(["python3", ".ai/deepseek/reprocess.py"])
    subprocess.Popen(["python3", ".ai/deepseek/process_issues.py"])
    print("🚀 Agents restarted in background.")

if __name__ == "__main__":
    cleanup_and_reprocess()
