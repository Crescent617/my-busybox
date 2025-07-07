#!/usr/bin/env bash

# git worktree switch
verbose=0
while [[ $# -gt 0 ]]; do
  case "$1" in
  -v | --verbose)
    verbose=1
    shift
    ;;
  esac
done

worktrees=$(git worktree list | awk '{print $1}')
selected=$(echo "$worktrees" | fzf --height 20% --reverse --no-multi --prompt "Select worktree: ")
cd "$selected" || {
  echo "Failed to switch to worktree: $selected" >&2
  exit 1
}
