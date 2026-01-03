#!/usr/bin/env python3
"""Fork current tmux window to a new window in the same directory."""

import os
import subprocess
import sys


def main():
    """Create a new tmux window in the current (or specified) directory."""
    # Get directory from arg or current working directory
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.getcwd()
    
    directory = os.path.abspath(directory)
    name = os.path.basename(directory)
    
    # Check if we're in tmux
    if not os.environ.get('TMUX'):
        print("Error: not in a tmux session", file=sys.stderr)
        sys.exit(1)
    
    subprocess.run(['tmux', 'new-window', '-n', name, '-c', directory])


if __name__ == '__main__':
    main()