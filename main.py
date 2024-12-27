import subprocess
import argparse
import pandas as pd
import os
import sqlite3
import tempfile
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clone_repo(repo_url, dest_folder):
    """Clone a Git repository to the specified destination folder."""
    if not os.path.exists(dest_folder):
        logging.info(f"Cloning repository from {repo_url} to {dest_folder}")
        subprocess.run(['git', 'clone', repo_url, dest_folder], check=True)
    else:
        logging.info(f"Repository {dest_folder} already exists. Skipping cloning.")

def fetch_commit_history(repo_path, remote=False, repo_url=None):
    """Fetch commit history from a local or remote Git repository."""
    if remote:
        with tempfile.TemporaryDirectory() as temp_dir:
            logging.info(f"Initializing temporary repository in {temp_dir}")
            subprocess.run(["git", "init", temp_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "-C", temp_dir, "remote", "add", "origin", repo_url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "-C", temp_dir, "fetch", "--depth=1", "origin"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            repo_path = temp_dir

    logging.info(f"Fetching commit history from {repo_path}")
    result = subprocess.run(['git', '-C', repo_path, 'log', '--pretty=format:%H|%an|%ad|%s', '--date=iso'], stdout=subprocess.PIPE, text=True)
    commits = [dict(zip(["hash", "author", "date", "message"], line.split('|', 3))) for line in result.stdout.splitlines()]
    return commits

def save_to_file(commit_data, output_path, file_format, db_path=None, table_name=None):
    df = pd.DataFrame(commit_data)
    if file_format == "parquet":
        df.to_parquet(output_path, engine='pyarrow', index=False)
        logging.info(f"Data saved to Parquet file: {output_path}")
    elif file_format == "excel":
        df.to_excel(output_path, index=False)
        logging.info(f"Data saved to Excel file: {output_path}")
    elif file_format == "sqlite":
        with sqlite3.connect(db_path) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        logging.info(f"Data saved to table '{table_name}' in SQLite database: {db_path}")
    elif file_format == "csv":
        df.to_csv(output_path, index=False)
        logging.info(f"Data saved to CSV file: {output_path}")
    elif file_format == "json":
        df.to_json(output_path, orient='records', lines=True)
        logging.info(f"Data saved to JSON file: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze commit history of a Git repository.")
    parser.add_argument("repo_url", type=str, help="URL of the Git repository to analyze commit history.")
    parser.add_argument("--noclone", "-n", action="store_true", help="Do not clone the repository; fetch commit history directly from remote.")
    parser.add_argument("--dest", "-d", type=str, default="./cloned_repo", help="Directory to clone the repository if the URL is provided. Default: ./cloned_repo")
    parser.add_argument("--output", "-o", type=str, default="commit_history", help="Base name for the output file without extension. Default: commit_history")
    parser.add_argument("--output-dir", "-od", type=str, default=".", help="Directory to save the output file. Default: current directory")
    parser.add_argument("--format", "-f", type=str, choices=["parquet", "excel", "sqlite", "csv", "json"], default="parquet", help="Output format: 'parquet', 'excel', 'sqlite', 'csv', or 'json'. Default: parquet")
    parser.add_argument("--db-path", "-db", type=str, default="commit_history.db", help="Path to the SQLite database if 'sqlite' format is selected. Default: commit_history.db")
    parser.add_argument("--table-name", "-t", type=str, default="commits", help="Table name in the database if 'sqlite' format is selected. Default: commits")
    args = parser.parse_args()

    remote_commits = None
    local_commits = None

    if args.noclone:
        logging.info("Fetching commit history without cloning...")
        remote_commits = fetch_commit_history(None, remote=True, repo_url=args.repo_url)
    else:
        logging.info(f"Cloning repository into {args.dest}...")
        clone_repo(args.repo_url, args.dest)
        logging.info("Fetching commit history from cloned repository...")
        local_commits = fetch_commit_history(args.dest)

    output_path = os.path.join(args.output_dir, f"{args.output}.{args.format}")
    save_to_file(remote_commits if args.noclone else local_commits, output_path, args.format, db_path=args.db_path, table_name=args.table_name)
    logging.info("Done!")