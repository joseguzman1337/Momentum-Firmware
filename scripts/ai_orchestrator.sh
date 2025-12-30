#!/usr/bin/env bash
# AI Agent Task Orchestrator
# Assigns new tasks to each AI agent and manages log output

set -e

REPO_ROOT="/Users/x/x/Momentum-Firmware"
LOGS_DIR="$REPO_ROOT/logs"

# Ensure log directories exist
mkdir -p "$LOGS_DIR"/{codex,claude,gemini,jules,warp}

echo "🤖 AI Agent Task Orchestrator"
echo "=============================="
echo ""

# Function to get pending issues
get_pending_issues() {
    gh issue list --limit 50 --json number,title --jq '.[] | "#\(.number): \(.title)"'
}

# Function to start Codex on next issue
start_codex_task() {
    local issue=$(gh issue list --limit 1 --json number,title --jq '.[0] | {number, title}')
    local issue_num=$(echo "$issue" | jq -r '.number')
    local issue_title=$(echo "$issue" | jq -r '.title')
    
    if [ -n "$issue_num" ] && [ "$issue_num" != "null" ]; then
        echo "🔧 [Codex] Assigning Issue #$issue_num: $issue_title"
        nohup codex --full-auto exec "Fix and resolve Issue #$issue_num: $issue_title. Make sure to generate a Pull Request (or commit) message that includes 'Closes #$issue_num' to auto-close the issue on merge." \
            > "$LOGS_DIR/codex/issue_${issue_num}.log" 2>&1 &
        echo "   Log: logs/codex/issue_${issue_num}.log"
    else
        echo "🔧 [Codex] No pending issues found"
    fi
}

# Function to start Gemini on complex issues
start_gemini_task() {
    echo "🧠 [Gemini] Running automation script..."
    python3 "$REPO_ROOT/scripts/gemini_automation.py" \
        > "$LOGS_DIR/gemini/automation_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
    echo "   Log: logs/gemini/automation_$(date +%Y%m%d_%H%M%S).log"
}

# Function to check Jules status
check_jules_status() {
    echo "🚀 [Jules] Checking session status..."
    export PNPM_HOME="$HOME/.pnpm-global"
    "$PNPM_HOME/jules" remote list --session 2>&1 | tee "$LOGS_DIR/jules/status_$(date +%Y%m%d_%H%M%S).log" | head -n 10
}

# Function to update Warp tasks
update_warp_tasks() {
    echo "⚡ [Warp] Task list available at: warp_agent_tasks.md"
    echo "   Execute manually in Warp Terminal"
}

# Main execution
echo "📋 Fetching pending issues..."
ISSUE_COUNT=$(gh issue list --limit 100 --json number | jq '. | length')
echo "   Found $ISSUE_COUNT open issues"
echo ""

# Assign tasks
start_codex_task
echo ""
start_gemini_task
echo ""
check_jules_status
echo ""
update_warp_tasks
echo ""

echo "=============================="
echo "✅ Task assignment complete!"
echo "📊 Monitor logs in: $LOGS_DIR/"
echo ""
echo "Active processes:"
ps aux | grep -E "codex|gemini|claude" | grep -v grep | wc -l | xargs echo "  Running agents:"
