#!/usr/bin/env python3

import subprocess


def list_panes():
    r = subprocess.run(
        [
            "tmux",
            "list-panes",
            "-a",
            "-F",
            '#S:#I:#W - "#T" #{session_alerts}(#{?pane_pipe,piped,not piped})',
        ],
        stdout=subprocess.PIPE,
    )
    r.check_returncode()
    return r.stdout.decode().strip()


command_map = {
    "list-panes": list_panes,
}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", type=str, help="command to run", choices=command_map.keys()
    )

    args = parser.parse_args()
    print(command_map[args.command]())
