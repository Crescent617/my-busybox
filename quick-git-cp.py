#!/usr/bin/env python3


def get_commit_list(num):
    logs = subprocess.run(['git', 'log', '--pretty=format:%h %s', '-n', str(num)],
                          stdout=subprocess.PIPE)
    logs.check_returncode()
    return logs.stdout.decode().split('\n')


def parse_commit_log(log):
    return log.split(' ', 1)[0]


def git_checkout(branch):
    r = subprocess.run(['git', 'checkout', branch])
    r.check_returncode()


def git_create_branch(branch):
    r = subprocess.run(['git', 'checkout', '-b', branch])
    r.check_returncode()


def git_cherry_pick(*commits):
    r = subprocess.run(['git', 'cherry-pick', *commits])
    r.check_returncode()


def git_branch_name():
    r = subprocess.run(['git', 'branch', '--show-current'],
                       stdout=subprocess.PIPE)
    r.check_returncode()
    return r.stdout.decode().strip()


def git_push():
    r = subprocess.run(['git', 'push'])
    r.check_returncode()


if __name__ == '__main__':

    import argparse
    import subprocess
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--commit-number', '-n', type=int,
                        default=1, help='number of commits to cherry-pick')
    parser.add_argument('--onto-branch', '-o', type=str,
                        help='onto branch', required=True)
    parser.add_argument('--create-new-branch', '-c', action='store_true')
    parser.add_argument('--from-branch', '-f', type=str, help='from branch')
    parser.add_argument('--push', '-p', action='store_true')

    args = parser.parse_args()

    num = args.commit_number
    onto_branch = args.onto_branch
    from_branch = args.from_branch
    create_new_branch = args.create_new_branch

    if from_branch is not None:
        git_checkout(from_branch)
    branch_name = git_branch_name()

    commit_list = [parse_commit_log(log)
                   for log in reversed(get_commit_list(num))]

    git_checkout(onto_branch)

    if create_new_branch:
        git_create_branch(
            f'{branch_name}-cp{num}-onto-{onto_branch}-{time.strftime("%Y%m%d%H%M%S")}')

    git_cherry_pick(*commit_list)

    if args.push:
        git_push()
