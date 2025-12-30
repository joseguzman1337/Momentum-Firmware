#!/bin/bash

WORKTREE_BASE="$HOME/.claude-worktrees/momentum-firmware"

create_worktree() {
    local branch_name="$1"
    local worktree_path="$WORKTREE_BASE/$branch_name"
    
    git worktree add "$worktree_path" -b "$branch_name"
    
    # Copy files from .worktreeinclude
    while IFS= read -r pattern; do
        [[ "$pattern" =~ ^#.*$ ]] && continue
        [[ -z "$pattern" ]] && continue
        find . -name "$pattern" -exec cp {} "$worktree_path"/{} \; 2>/dev/null
    done < .worktreeinclude
    
    echo "Worktree created: $worktree_path"
}

list_worktrees() {
    git worktree list
}

remove_worktree() {
    local branch_name="$1"
    local worktree_path="$WORKTREE_BASE/$branch_name"
    git worktree remove "$worktree_path"
    git branch -D "$branch_name"
}

case "$1" in
    create) create_worktree "$2" ;;
    list) list_worktrees ;;
    remove) remove_worktree "$2" ;;
    *) echo "Usage: $0 {create|list|remove} [branch_name]" ;;
esac