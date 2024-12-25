# Git Repository Analysis Tool

This Python script analyzes the commit history of Git repositories and exports the data in various formats (Parquet, Excel, or SQLite). It can either clone a repository locally or fetch commit history directly from a remote repository.

## Features

- Clone Git repositories or fetch commit history directly from remote
- Extract commit information including hash, author, date, and commit message
- Export data in multiple formats:
  - Parquet (using PyArrow)
  - Excel
  - SQLite database

## Requirements

```
git
pandas
pyarrow
openpyxl
sqlite3
```

## Installation

1. Ensure you have Git installed on your system
2. Install the required Python packages:
   ```bash
   pip install pandas pyarrow openpyxl
   ```

## Usage

Basic usage:
```bash
python script.py <repository_url>
```

To see all available options:
```bash
python script.py -h
```
or
```bash
python script.py --help
```

Example with options:
```bash
python script.py https://github.com/user/repo --format sqlite --output my_analysis
```

### Command Line Arguments

- `repo_url`: URL of the Git repository to analyze (required)
- `-n, --noclone`: Fetch commit history directly from remote without cloning
- `-d, --dest`: Directory to clone the repository (default: "./cloned_repo")
- `-o, --output`: Base name for the output file without extension (default: "commit_history")
- `-f, --format`: Output format - 'parquet', 'excel', or 'sqlite' (default: "parquet")
- `-db, --db-path`: Path to SQLite database if using sqlite format (default: "commit_history.db")
- `-t, --table-name`: Table name in SQLite database (default: "commits")
- `-h, --help`: Show this help message and exit

### Output Format

The script extracts the following information for each commit:
- Hash: Commit hash
- Author: Commit author name
- Date: Commit date (ISO format)
- Message: Commit message

## Examples

1. Export commit history to Parquet:
   ```bash
   python script.py https://github.com/user/repo -f parquet -o repo_analysis
   ```

2. Export to SQLite without cloning:
   ```bash
   python script.py https://github.com/user/repo -n -f sqlite -db my_database.db -t commit_data
   ```

3. Export to Excel with custom output path:
   ```bash
   python script.py https://github.com/user/repo -f excel -o ./analysis/repo_commits
   ```

## Functions

### `clone_repo(repo_url, dest_folder)`
Clones a Git repository to the specified destination folder.

### `fetch_commit_history(repo_path, remote=False, repo_url=None)`
Fetches commit history from either a local or remote Git repository.

### `save_to_file(commit_data, output_path, file_format, db_path=None, table_name=None)`
Saves the commit data to the specified format (Parquet, Excel, or SQLite).

## Error Handling

- The script will check if a repository already exists before cloning
- Uses subprocess error checking for Git operations
- Provides appropriate error messages for failed operations
