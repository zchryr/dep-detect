# Git Diff Detector

A simple Python script that detects changes in your git repository.

## Features

- Detects changed files in your current branch compared to the main branch
- Shows file status (Added, Modified, Deleted)
- Simple and lightweight - no external dependencies required
- Easy to test and verify changes

## Usage

1. Make sure you have Python 3.6+ installed
2. Clone this repository
3. Run the script:

```bash
python git_diff_detector.py
```

## Output

The script will output a list of changed files with their status:

```
Changed files:
A       new_file.txt
M       modified_file.py
D       deleted_file.js
```

Where:
- `A` means the file was Added
- `M` means the file was Modified
- `D` means the file was Deleted

## Development

This script uses only Python standard library modules, so there are no external dependencies to install.

## Testing

To test the script:
1. Make some changes to files
2. Run the script to see the changes
3. Verify the output matches your changes

## License

MIT