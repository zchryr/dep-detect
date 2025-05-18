#!/usr/bin/env python3

import subprocess
import sys
from typing import List, Dict, Optional

def get_git_diff(base_branch: str = "main") -> List[Dict[str, str]]:
    """
    Get the list of changed files in the current branch compared to the base branch.

    Args:
        base_branch: The base branch to compare against (default: "main")

    Returns:
        List of dictionaries containing file information with keys:
        - filename: Name of the changed file
        - status: Status of the change (A=added, M=modified, D=deleted)
    """
    try:
        # Get the list of changed files
        result = subprocess.run(
            ["git", "diff", "--name-status", base_branch],
            capture_output=True,
            text=True,
            check=True
        )

        changed_files = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            status, filename = line.split("\t")
            changed_files.append({
                "filename": filename,
                "status": status
            })

        return changed_files

    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}", file=sys.stderr)
        return []

def main():
    """Main function to detect and display git diffs."""
    changed_files = get_git_diff()

    if not changed_files:
        print("No changes detected.")
        return

    print("Changed files:")
    for file_info in changed_files:
        status = file_info["status"]
        filename = file_info["filename"]
        print(f"{status}\t{filename}")

if __name__ == "__main__":
    main()