#!/usr/bin/env python3

from functools import lru_cache
import json
import subprocess

desc = "This script is for cherry-picking commits from one branch to another."
usage = """
Use case 1: cherry-pick specific number of commits (-n) from a branch to another branch
e.g. quick-git-cp.py --onto-branch V_6_59 -n 1 --create-new-branch --push

Use case 2: cherry-pick commits from a PR and create a PR
e.g. quick-git-cp.py --onto-branch origin/V_6_60 --create-new-branch --create-pr --from-pr 111
"""


def step_info(step_name):
    print('='*10, 'STEP:', step_name, '='*10)


def step_info_decorator(func):
    def wrapper(*args, **kwargs):
        step_info(func.__name__)
        return func(*args, **kwargs)
    return wrapper


def get_commit_list(num):
    logs = subprocess.run(
        ["git", "log", "--pretty=format:%h %s", "-n", str(num)], stdout=subprocess.PIPE
    )
    logs.check_returncode()
    return logs.stdout.decode().split("\n")


def parse_commit_log(log):
    return log.split(" ", 1)[0]


@step_info_decorator
def git_checkout(branch):
    r = subprocess.run(["git", "checkout", branch])
    r.check_returncode()


@step_info_decorator
def git_fetch():
    r = subprocess.run(["git", "fetch"])
    r.check_returncode()


@step_info_decorator
def git_create_branch(branch):
    r = subprocess.run(["git", "checkout", "-b", branch])
    r.check_returncode()


@step_info_decorator
def git_cherry_pick(*commits):
    r = subprocess.run(["git", "cherry-pick", *commits])
    r.check_returncode()


def git_branch_name():
    r = subprocess.run(["git", "branch", "--show-current"],
                       stdout=subprocess.PIPE)
    r.check_returncode()
    return r.stdout.decode().strip()


@step_info_decorator
def git_push():
    r = subprocess.run(["git", "push"])
    r.check_returncode()


@lru_cache(maxsize=None)
def get_pr_info(pr_id):
    r = subprocess.run(["gh", "pr", "view", pr_id, "--json", "commits,reviews,reviewRequests"],
                       stdout=subprocess.PIPE)
    r.check_returncode()
    return json.loads(r.stdout.decode())


def get_commits_from_pr_id(pr_id):
    d = get_pr_info(pr_id)
    return [c["oid"] for c in d["commits"]]


def get_reviewers_from_pr_id(pr_id):
    d = get_pr_info(pr_id)
    reviewers = set(r['author']['login'] for r in d["reviews"])
    reviewers |= set(r['login'] for r in d["reviewRequests"])
    return list(reviewers)


@step_info_decorator
def gh_create_pr(branch_name=None, reviewers: list = []):
    cmd = ["gh", "pr", "create", "--fill"]
    if branch_name is not None:
        cmd += ["-B", branch_name]

    for reviewer in reviewers:
        cmd += ["-r", reviewer]

    r = subprocess.run(cmd)
    r.check_returncode()


if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser(usage=usage, description=desc)
    parser.add_argument(
        "--commit-number",
        "-n",
        type=int,
        default=1,
        help="number of commits to cherry-pick",
    )
    parser.add_argument(
        "--onto-branch", "-o", type=str, help="onto branch", required=True
    )
    parser.add_argument("--create-new-branch", "-c", action="store_true")
    parser.add_argument("--from-branch", "-f", type=str,
                        help="default: current branch")
    parser.add_argument("--push", "-p", action="store_true")
    parser.add_argument("--from-pr", type=str,
                        help="PR ID. this option will override --commit-number")
    parser.add_argument("--create-pr", action="store_true")

    args = parser.parse_args()

    num = args.commit_number
    onto_branch = args.onto_branch
    from_branch = args.from_branch
    create_new_branch = args.create_new_branch

    git_fetch()

    if from_branch is not None:
        git_checkout(from_branch)

    branch_name = git_branch_name()

    commits = [parse_commit_log(log)
               for log in reversed(get_commit_list(num))
               ] if not args.from_pr else get_commits_from_pr_id(args.from_pr)

    git_checkout(onto_branch)

    if create_new_branch:
        if args.from_pr:
            new_branch_name = f'cp-from-pr-{args.from_pr}-onto-{onto_branch}-{time.strftime("%Y%m%d%H%M%S")}'
        else:
            new_branch_name = f'{branch_name}-cp{num}-onto-{onto_branch}-{time.strftime("%Y%m%d%H%M%S")}'
        git_create_branch(new_branch_name.replace('/', '_'))

    git_cherry_pick(*commits)

    if args.push or args.create_pr:
        git_push()

    if args.create_pr:
        reviewers = get_reviewers_from_pr_id(
            args.from_pr) if args.from_pr else []
        gh_create_pr(onto_branch.split('/')[-1], reviewers)
