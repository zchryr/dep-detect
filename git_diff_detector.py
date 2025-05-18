#!/usr/bin/env python3

import subprocess
import sys
from typing import List, Dict, Optional, Set

# Define manifest file patterns for different languages
MANIFEST_PATTERNS = {
    'python': ['requirements.txt', 'Pipfile', 'Pipfile.lock', 'pyproject.toml'],
    'javascript': ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
    'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
    'csharp': ['.csproj', 'packages.config'],
    'php': ['composer.json', 'composer.lock'],
    'cpp': ['conanfile.txt', 'vcpkg.json', 'CMakeLists.txt'],
    'go': ['go.mod', 'go.sum'],
    'ruby': ['Gemfile', 'Gemfile.lock'],
    'kotlin': ['build.gradle', 'build.gradle.kts', 'pom.xml'],
    'swift': ['Package.swift', 'Podfile', 'Podfile.lock'],
    'rust': ['Cargo.toml', 'Cargo.lock']
}

def is_manifest_file(filename: str) -> bool:
    """
    Check if a file is a dependency manifest file.

    Args:
        filename: Name of the file to check

    Returns:
        True if the file is a manifest file, False otherwise
    """
    return any(
        filename.endswith(pattern)
        for patterns in MANIFEST_PATTERNS.values()
        for pattern in patterns
    )

def get_language_for_file(filename: str) -> Optional[str]:
    """
    Determine the programming language based on the manifest file.

    Args:
        filename: Name of the manifest file

    Returns:
        Language name if found, None otherwise
    """
    for lang, patterns in MANIFEST_PATTERNS.items():
        if any(filename.endswith(pattern) for pattern in patterns):
            return lang
    return None

def get_git_diff(base_branch: str = "main") -> List[Dict[str, str]]:
    """
    Get the list of changed manifest files in the current branch compared to the base branch.

    Args:
        base_branch: The base branch to compare against (default: "main")

    Returns:
        List of dictionaries containing file information with keys:
        - filename: Name of the changed file
        - status: Status of the change (A=added, M=modified, D=deleted)
        - language: Programming language of the manifest file
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

            # Only include manifest files
            if is_manifest_file(filename):
                language = get_language_for_file(filename)
                changed_files.append({
                    "filename": filename,
                    "status": status,
                    "language": language
                })

        return changed_files

    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}", file=sys.stderr)
        return []

def main():
    """Main function to detect and display changes in dependency manifest files."""
    changed_files = get_git_diff()

    if not changed_files:
        print("No changes detected in dependency manifest files.")
        return

    # Group changes by language
    changes_by_language = {}
    for file_info in changed_files:
        lang = file_info["language"]
        if lang not in changes_by_language:
            changes_by_language[lang] = []
        changes_by_language[lang].append(file_info)

    # Print changes organized by language
    print("Changes in dependency manifest files:")
    print("-" * 50)

    for lang, files in sorted(changes_by_language.items()):
        print(f"\n{lang.upper()}:")
        for file_info in files:
            status = file_info["status"]
            filename = file_info["filename"]
            print(f"  {status}\t{filename}")

if __name__ == "__main__":
    main()