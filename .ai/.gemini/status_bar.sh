#!/bin/bash

# Claude Code Comprehensive Status Line
# Displays all possible information from the Claude Code status API

# Read JSON input from stdin
JSON=$(cat)

# Color codes
RESET="\033[0m"
BOLD="\033[1m"
DIM="\033[2m"

# Foreground colors
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
MAGENTA="\033[35m"
CYAN="\033[36m"
WHITE="\033[37m"
ORANGE="\033[38;5;208m"
PURPLE="\033[38;5;141m"
PINK="\033[38;5;213m"
LIME="\033[38;5;154m"

# Extract data using jq
MODEL=$(echo "$JSON" | jq -r '.model.display_name // "Unknown"')
MODEL_ID=$(echo "$JSON" | jq -r '.model.id // ""')
SESSION_ID=$(echo "$JSON" | jq -r '.session_id // ""' | cut -c1-8)
VERSION=$(echo "$JSON" | jq -r '.version // ""')

# Cost information
COST=$(echo "$JSON" | jq -r '.cost.total_cost_usd // 0')
DURATION_MS=$(echo "$JSON" | jq -r '.cost.total_duration_ms // 0')
API_DURATION_MS=$(echo "$JSON" | jq -r '.cost.total_api_duration_ms // 0')
LINES_ADDED=$(echo "$JSON" | jq -r '.cost.total_lines_added // 0')
LINES_REMOVED=$(echo "$JSON" | jq -r '.cost.total_lines_removed // 0')

# Context window information
INPUT_TOKENS=$(echo "$JSON" | jq -r '.context_window.total_input_tokens // 0')
OUTPUT_TOKENS=$(echo "$JSON" | jq -r '.context_window.total_output_tokens // 0')
CONTEXT_SIZE=$(echo "$JSON" | jq -r '.context_window.context_window_size // 200000')
CACHE_READ=$(echo "$JSON" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
CACHE_CREATE=$(echo "$JSON" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')

# Workspace information
CURRENT_DIR=$(echo "$JSON" | jq -r '.workspace.current_dir // .cwd // ""')
PROJECT_DIR=$(echo "$JSON" | jq -r '.workspace.project_dir // ""')

# Calculate context window percentage
TOTAL_TOKENS=$((INPUT_TOKENS + OUTPUT_TOKENS))
if [ "$CONTEXT_SIZE" -gt 0 ]; then
    CONTEXT_PCT=$((TOTAL_TOKENS * 100 / CONTEXT_SIZE))
else
    CONTEXT_PCT=0
fi

# Format cost with proper precision
COST_FORMATTED=$(printf "%.4f" "$COST")

# Convert durations to seconds
DURATION_SEC=$(echo "scale=1; $DURATION_MS / 1000" | bc 2>/dev/null || echo "0")
API_DURATION_SEC=$(echo "scale=1; $API_DURATION_MS / 1000" | bc 2>/dev/null || echo "0")

# Get git information if in a git repo
GIT_BRANCH=""
GIT_STATUS=""
if [ -d "$CURRENT_DIR/.git" ] || git -C "$CURRENT_DIR" rev-parse --git-dir > /dev/null 2>&1; then
    GIT_BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null)

    # Get git status counts
    UNTRACKED=$(git -C "$CURRENT_DIR" status --porcelain 2>/dev/null | grep -c "^??")
    MODIFIED=$(git -C "$CURRENT_DIR" status --porcelain 2>/dev/null | grep -c "^ M")
    STAGED=$(git -C "$CURRENT_DIR" status --porcelain 2>/dev/null | grep -c "^M")

    if [ "$STAGED" -gt 0 ] || [ "$MODIFIED" -gt 0 ] || [ "$UNTRACKED" -gt 0 ]; then
        GIT_STATUS=" ${GREEN}✓${STAGED}${RESET} ${YELLOW}●${MODIFIED}${RESET} ${RED}+${UNTRACKED}${RESET}"
    else
        GIT_STATUS=" ${GREEN}✓${RESET}"
    fi
fi

# Get current time
CURRENT_TIME=$(date +"%H:%M:%S")

# Directory display (show basename)
DIR_DISPLAY=$(basename "$CURRENT_DIR")

# Build status line with all information
STATUS=""

# Model info with icon
if [[ "$MODEL" == "Opus"* ]]; then
    STATUS+="${PURPLE}${BOLD}◆${RESET} ${PURPLE}${MODEL}${RESET}"
elif [[ "$MODEL" == "Sonnet"* ]]; then
    STATUS+="${ORANGE}${BOLD}◆${RESET} ${ORANGE}${MODEL}${RESET}"
elif [[ "$MODEL" == "Haiku"* ]]; then
    STATUS+="${CYAN}${BOLD}◆${RESET} ${CYAN}${MODEL}${RESET}"
else
    STATUS+="${WHITE}${BOLD}◆${RESET} ${WHITE}${MODEL}${RESET}"
fi

# Session ID
STATUS+=" ${DIM}│${RESET} ${BLUE}⚡${SESSION_ID}${RESET}"

# Git branch and status
if [ -n "$GIT_BRANCH" ]; then
    STATUS+=" ${DIM}│${RESET} ${MAGENTA}${GIT_BRANCH}${RESET}${GIT_STATUS}"
fi

# Directory
STATUS+=" ${DIM}│${RESET} ${CYAN}📁${DIR_DISPLAY}${RESET}"

# Cost and duration
STATUS+=" ${DIM}│${RESET} ${GREEN}\$${COST_FORMATTED}${RESET}"
STATUS+=" ${DIM}│${RESET} ${YELLOW}⏱${DURATION_SEC}s${RESET}"

# Lines changed
if [ "$LINES_ADDED" -gt 0 ] || [ "$LINES_REMOVED" -gt 0 ]; then
    STATUS+=" ${DIM}│${RESET} ${GREEN}+${LINES_ADDED}${RESET}${DIM}/${RESET}${RED}-${LINES_REMOVED}${RESET}"
fi

# Context window usage
STATUS+=" ${DIM}│${RESET}"
if [ "$CONTEXT_PCT" -gt 80 ]; then
    STATUS+=" ${RED}${BOLD}${CONTEXT_PCT}%${RESET}"
elif [ "$CONTEXT_PCT" -gt 60 ]; then
    STATUS+=" ${YELLOW}${CONTEXT_PCT}%${RESET}"
else
    STATUS+=" ${LIME}${CONTEXT_PCT}%${RESET}"
fi
STATUS+=" ${DIM}(${INPUT_TOKENS}i/${OUTPUT_TOKENS}o)${RESET}"

# Cache info (if any)
if [ "$CACHE_READ" -gt 0 ] || [ "$CACHE_CREATE" -gt 0 ]; then
    STATUS+=" ${DIM}│${RESET} ${PINK}⚡${CACHE_READ}${RESET}"
fi

# Current time
STATUS+=" ${DIM}│${RESET} ${WHITE}${CURRENT_TIME}${RESET}"

# Output the status line
echo -e "$STATUS"
