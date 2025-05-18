# WORK IN PROGRESS

# Git Diff Dependency Detector

A simple Python script to detect new and removed dependencies between any two git branches, supporting many common dependency manifest files across multiple languages.

## Features

- Detects added and removed dependencies between any two branches
- Supports Python, JavaScript, Java, C#, PHP, C++, Go, Ruby, Kotlin, Swift, and Rust manifest files
- Works with files like `requirements.txt`, `package.json`, `pom.xml`, `composer.json`, and more
- Outputs results in human-readable or JSON format (for CI or automation)
- Bidirectional: works regardless of your current branch

## Supported Manifest Files

- **Python:** `requirements.txt`, `Pipfile`, `Pipfile.lock`, `pyproject.toml`
- **JavaScript/TypeScript:** `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- **Java:** `pom.xml`, `build.gradle`, `build.gradle.kts`
- **C#:** `.csproj`, `packages.config`
- **PHP:** `composer.json`, `composer.lock`
- **C++:** `conanfile.txt`, `vcpkg.json`, `CMakeLists.txt`
- **Go:** `go.mod`, `go.sum`
- **Ruby:** `Gemfile`, `Gemfile.lock`
- **Kotlin:** `build.gradle`, `build.gradle.kts`, `pom.xml`
- **Swift:** `Package.swift`, `Podfile`, `Podfile.lock`
- **Rust:** `Cargo.toml`, `Cargo.lock`

## Usage

```bash
python3 git_diff_detector.py [target_branch] [base_branch] [--json]
```
- `target_branch`: The branch you want to analyze (e.g., a feature or PR branch)
- `base_branch`: The branch to compare against (default: your current branch)
- `--json`: Output results as JSON (optional)

### Examples

**Compare what would be introduced in `feature-branch` compared to `main`:**
```bash
python3 git_diff_detector.py feature-branch main
```

**Show only new/removed dependencies as JSON:**
```bash
python3 git_diff_detector.py feature-branch main --json
```

**If you are on `main`, you can also run:**
```bash
python3 git_diff_detector.py feature-branch --json
```

## Output

### Human-readable
```
Changes in dependency manifest files (comparing feature-branch against main):
--------------------------------------------------

JAVASCRIPT:
  A     tests/package.json
    New dependencies:
      + express
      + lodash
    Removed dependencies:
      - old-package

PYTHON:
  M     tests/requirements.txt
    New dependencies:
      + requests
    Removed dependencies:
      - flask
```

### JSON
```json
{
  "javascript": {
    "tests/package.json": {
      "new_deps": ["express", "lodash"],
      "removed_deps": ["old-package"]
    }
  },
  "python": {
    "tests/requirements.txt": {
      "new_deps": ["requests"],
      "removed_deps": ["flask"]
    }
  }
}
```

## Development

- No external dependencies required (uses Python standard library)
- Works with any git repository

## License

MIT