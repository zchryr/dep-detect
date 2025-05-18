#!/usr/bin/env python3

import subprocess
import sys
import json
from typing import List, Dict, Optional, Set, Tuple

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

def get_current_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

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

def get_file_content(filename: str, branch: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "show", f"{branch}:{filename}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def parse_dependencies(filename: str, content: str) -> Set[str]:
    if not content:
        return set()
    try:
        if filename.endswith('.json'):
            data = json.loads(content)
            deps = set()
            if 'dependencies' in data:
                deps.update(data['dependencies'].keys())
            if 'devDependencies' in data:
                deps.update(data['devDependencies'].keys())
            if 'require' in data:
                deps.update(data['require'].keys())
            if 'require-dev' in data:
                deps.update(data['require-dev'].keys())
            return deps
        elif filename.endswith('.txt'):
            deps = set()
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    package = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
                    if package:
                        deps.add(package)
            return deps
    except Exception as e:
        print(f"Error parsing {filename}: {e}", file=sys.stderr)
    return set()

def get_git_diff(base_branch: str, target_branch: str) -> List[Dict[str, str]]:
    try:
        # Compare base_branch..target_branch to get what is new in target_branch
        result = subprocess.run(
            ["git", "diff", "--name-status", f"{base_branch}..{target_branch}"],
            capture_output=True,
            text=True,
            check=True
        )
        changed_files = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            status = parts[0]
            if status.startswith('R'):
                old_filename = parts[1]
                new_filename = parts[2]
                if is_manifest_file(old_filename) or is_manifest_file(new_filename):
                    changed_files.append({
                        "filename": new_filename,
                        "status": "R",
                        "language": get_language_for_file(new_filename),
                        "old_filename": old_filename
                    })
            else:
                filename = parts[1]
                if is_manifest_file(filename):
                    changed_files.append({
                        "filename": filename,
                        "status": status,
                        "language": get_language_for_file(filename)
                    })
        return changed_files
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}", file=sys.stderr)
        return []

def analyze_dependencies(changed_files: List[Dict[str, str]], base_branch: str, target_branch: str) -> Dict[str, List[Dict[str, Set[str]]]]:
    changes_by_language = {}
    for file_info in changed_files:
        lang = file_info["language"]
        if lang not in changes_by_language:
            changes_by_language[lang] = []
        filename = file_info["filename"]
        status = file_info["status"]
        if status == "A":
            content = get_file_content(filename, target_branch)
            deps = parse_dependencies(filename, content)
            changes_by_language[lang].append({
                "filename": filename,
                "status": status,
                "new_deps": deps,
                "removed_deps": set()
            })
        elif status == "D":
            content = get_file_content(filename, base_branch)
            deps = parse_dependencies(filename, content)
            changes_by_language[lang].append({
                "filename": filename,
                "status": status,
                "new_deps": set(),
                "removed_deps": deps
            })
        elif status == "M":
            base_content = get_file_content(filename, base_branch)
            target_content = get_file_content(filename, target_branch)
            base_deps = parse_dependencies(filename, base_content)
            target_deps = parse_dependencies(filename, target_content)
            new_deps = target_deps - base_deps
            removed_deps = base_deps - target_deps
            changes_by_language[lang].append({
                "filename": filename,
                "status": status,
                "new_deps": new_deps,
                "removed_deps": removed_deps
            })
        elif status == "R":
            old_filename = file_info["old_filename"]
            base_content = get_file_content(old_filename, base_branch)
            target_content = get_file_content(filename, target_branch)
            base_deps = parse_dependencies(old_filename, base_content)
            target_deps = parse_dependencies(filename, target_content)
            new_deps = target_deps - base_deps
            removed_deps = base_deps - target_deps
            changes_by_language[lang].append({
                "filename": filename,
                "status": status,
                "old_filename": old_filename,
                "new_deps": new_deps,
                "removed_deps": removed_deps
            })
    return changes_by_language

def main():
    # Usage: script.py [target_branch] [base_branch] [--json]
    output_json = False
    args = sys.argv[1:]
    if '--json' in args:
        output_json = True
        args.remove('--json')
    if len(args) == 0:
        print("Usage: script.py [target_branch] [base_branch] [--json]")
        sys.exit(1)
    elif len(args) == 1:
        target_branch = args[0]
        base_branch = get_current_branch()
    else:
        target_branch = args[0]
        base_branch = args[1]
    changed_files = get_git_diff(base_branch, target_branch)
    if not changed_files:
        print(f"No changes detected in dependency manifest files.")
        print(f"\nNote: Comparing '{target_branch}' against '{base_branch}'.")
        print("If you're not seeing expected changes, make sure your branch arguments are correct.")
        print("The script shows changes in the target branch compared to the base branch.")
        return
    changes_by_language = analyze_dependencies(changed_files, base_branch, target_branch)
    if output_json:
        result = {}
        for lang, files in changes_by_language.items():
            lang_dict = {}
            for file_info in files:
                lang_dict[file_info["filename"]] = {
                    "new_deps": sorted(file_info["new_deps"]),
                    "removed_deps": sorted(file_info["removed_deps"])
                }
            if lang_dict:
                result[lang] = lang_dict
        print(json.dumps(result, indent=2))
        return
    print(f"Changes in dependency manifest files (comparing {target_branch} against {base_branch}):")
    print("-" * 50)
    for lang, files in sorted(changes_by_language.items()):
        if not files:
            continue
        print(f"\n{lang.upper()}:")
        for file_info in files:
            status = file_info["status"]
            filename = file_info["filename"]
            if status == "R":
                old_filename = file_info["old_filename"]
                print(f"  {status}\t{old_filename} -> {filename}")
            else:
                print(f"  {status}\t{filename}")
            if file_info["new_deps"]:
                print("    New dependencies:")
                for dep in sorted(file_info["new_deps"]):
                    print(f"      + {dep}")
            if file_info["removed_deps"]:
                print("    Removed dependencies:")
                for dep in sorted(file_info["removed_deps"]):
                    print(f"      - {dep}")

if __name__ == "__main__":
    main()