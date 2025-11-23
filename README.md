# migrate_github_repo

This project provides a Python script to automate the migration of a GitHub repository from one account to another, with optional commit author rewriting.

## Features
- Clone a source GitHub repository using a Personal Access Token (PAT)
- Rewrite commit history to change author name/email (optional)
- Push the repository to a destination GitHub account
- Handles authentication and error reporting

## Requirements
- Python 3.9+
- `git-filter-repo` (install with `pip install git-filter-repo`)
- Valid GitHub Personal Access Tokens for both source and destination accounts

## Usage
1. Edit `migrate_github_repo.py` to set your source and destination repo URLs, usernames, and tokens.
2. Run the script:
   ```sh
   python3 migrate_github_repo.py
   ```
3. The script will clone, rewrite history (if configured), and push to the destination repo.

## Security
**Do not commit your Personal Access Tokens to public repositories.**

## License
MIT
