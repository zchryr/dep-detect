# Dependency Detection GitHub Action

This GitHub Action detects new dependencies added in pull requests across various programming languages and package managers.

## Features

- Detects new dependencies in pull requests
- Supports multiple programming languages and package managers:
  - Python (requirements.txt, Pipfile, pyproject.toml)
  - JavaScript/TypeScript (package.json, yarn.lock, etc.)
  - Java (pom.xml, build.gradle)
  - C# (.csproj, packages.config)
  - PHP (composer.json)
  - C++ (conanfile.txt, vcpkg.json)
  - Go (go.mod)
  - Ruby (Gemfile)
  - Kotlin (build.gradle, pom.xml)
  - Swift (Package.swift, Podfile)
  - Rust (Cargo.toml)

## Usage

Add the following to your workflow file (e.g., `.github/workflows/dependency-check.yml`):

```yaml
name: Check Dependencies

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check for new dependencies
        uses: zchryr/dependency-detection-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Outputs

The action provides the following outputs:

- `new_dependencies`: A formatted string containing information about newly added dependencies, organized by file.

## Example Output

```
New dependencies detected:

package.json:
  - lodash
  - express

requirements.txt:
  - requests
  - pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.