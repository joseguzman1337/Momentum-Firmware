#!/bin/bash
# Real-time Pusher Script
# Usage: ./real_time_pusher.sh "commit message"

MESSAGE=$1
git add .
# Atomic check: if nothing to commit, skip
if git diff-index --quiet HEAD --; then
    exit 0
fi

# Strategy: git commit --amend and git push --force-with-lease
# If it's the first commit for a task, we might not want to amend.
# But per instructions: "git commit --amend, git push --force-with-lease"
git commit --amend -m "$MESSAGE" || git commit -m "$MESSAGE"
git push origin next --force-with-lease
