#!/usr/bin/env bash

# gwta.sh --from <start-point> <branch-name>
# will create a new worktree in the root of the repo .worktrees/<branch-name> and switch to it
# if --from is not provided, it will default to the current branch
# if --from is provided, it will create the worktree from the specified start-point (branch, tag, commit)
# if the worktree already exists, it will switch to it
# if the branch already exists, it will create the worktree from the existing branch
# if run this script from a worktree, it will create the new worktree also in the root of the repo .worktrees/<branch-name>, NOT inside the current worktree

set -euo pipefail

usage() {
  echo "Usage: $0 [--from <start-point>] <branch-name>"
  exit 1
}

FROM=""
BRANCH=""

# 解析参数
if [[ $# -eq 0 ]]; then
  usage
fi

if [[ "$1" == "--from" ]]; then
  if [[ $# -lt 3 ]]; then
    usage
  fi
  FROM="$2"
  BRANCH="$3"
else
  BRANCH="$1"
fi

# 获取 repo root（关键：即使在 worktree 内也正确）
REPO_ROOT=$(dirname "$(git rev-parse --git-common-dir)")

WORKTREE_DIR="$REPO_ROOT/.worktrees/$BRANCH"

mkdir -p "$REPO_ROOT/.worktrees"

# 如果 worktree 已存在
if [[ -d "$WORKTREE_DIR" ]]; then
  echo "Worktree already exists: $WORKTREE_DIR"
  cd "$WORKTREE_DIR"
  exec "$SHELL"
fi

# 判断分支是否已存在
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "Branch exists, creating worktree from existing branch..."
  git worktree add "$WORKTREE_DIR" "$BRANCH"
else
  # 分支不存在
  if [[ -n "$FROM" ]]; then
    echo "Creating branch '$BRANCH' from '$FROM'..."
    git worktree add -b "$BRANCH" "$WORKTREE_DIR" "$FROM"
  else
    # 默认从当前分支
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

    if [[ "$CURRENT_BRANCH" == "HEAD" ]]; then
      echo "Error: current HEAD is detached, please specify --from"
      exit 1
    fi

    echo "Creating branch '$BRANCH' from current branch '$CURRENT_BRANCH'..."
    git worktree add -b "$BRANCH" "$WORKTREE_DIR"
  fi
fi

cd "$WORKTREE_DIR"
exec "$SHELL"
