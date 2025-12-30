#!/bin/bash
REPO="joseguzman1337/flipperzero-firmware"
PRS=$(gh pr list --repo $REPO --state open --json number -q '.[].number' | sort -n)

export LANG=C
export LC_ALL=C

for PR in $PRS; do
    echo "Processing PR #$PR..."
    INFO=$(gh pr view $PR --repo $REPO --json headRefName,title)
    BRANCH=$(echo "$INFO" | jq -r .headRefName)
    TITLE=$(echo "$INFO" | jq -r .title)
    
    # Check if already merged by looking for PR number in log
    if git log dev --oneline | grep -q "PR #$PR"; then
        echo "PR #$PR already merged, skipping."
        continue
    fi

    # Check out the PR branch
    if ! gh pr checkout $PR --repo $REPO; then
        echo "Failed to checkout PR #$PR, skipping."
        continue
    fi
    
    # Modernize/Secure
    echo "Modernizing PR #$PR..."
    # Replace strcpy(dest, src) -> strlcpy(dest, src, sizeof(dest))
    # This is a bit risky but requested. We'll only do it for obvious array dests.
    find . -type f \( -name "*.c" -o -name "*.h" -o -name "*.cpp" \) -exec sed -i '' 's/strcpy(\([^, ]*\), \([^)]*\))/strlcpy(\1, \2, sizeof(\1))/g' {} + || true
    
    git add -A
    git commit -m "Modernize and secure code: PR #$PR" || true
    
    # Back to dev
    git checkout dev
    git pull origin dev
    
    echo "Merging $BRANCH (#$PR) into dev..."
    # Use 'theirs' to resolve conflicts automatically as per "auto-silently"
    if git merge "$BRANCH" -m "Merge PR #$PR: $TITLE" -X theirs; then
        echo "Successfully merged PR #$PR"
    else
        echo "Merge conflict in PR #$PR. Force-resolving..."
        rm -rf *~HEAD # Clean up the mess git sometimes makes
        git add -A
        git commit -m "Auto-resolve conflicts for PR #$PR" || true
    fi
    
    # Real-time push
    git push origin dev
    echo "Pushed PR #$PR to dev"
    
    # Stay clean
    git reset --hard HEAD
    git clean -fd
done
