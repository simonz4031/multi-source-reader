# Multi-Source Reader

This console Python program allows you to read information from various sources, including GitHub pull requests, Google Docs/Sheets, and Jira tickets.

## Setup

1. Clone the repository and navigate to the project directory.

2. If you're using Miniconda, create and activate a new environment:
   ```
   conda create -n multi-source-reader python=3.8
   conda activate multi-source-reader
   ```

3. Set up the necessary credentials:
   - Create a `.env` file in either the current directory or your home directory with the following content:
     ```
     GITHUB_TOKEN=your_github_token
     GITHUB_REPO_OWNER=your_github_username_or_org
     GITHUB_REPO=your_repository_name
     JIRA_DOMAIN=https://your-domain.atlassian.net
     JIRA_EMAIL=your_jira_email
     JIRA_TOKEN=your_jira_api_token
     ```
   - Place your Google service account JSON file as `google-credentials.json` in either the current directory or your home directory.

## Installation

After setting up your environment and credentials, install the package:

```
python src/main.py --github "PR Title"
```
or
```
python src/main.py --github "https://github.com/owner/repo/pull/123"
```

2. Google Doc:
```
python src/main.py --google "https://docs.google.com/document/d/your-doc-id/edit"
```

3. Google Sheet:
```
python src/main.py --google "https://docs.google.com/spreadsheets/d/your-sheet-id/edit"
```

4. Jira Ticket:
```
python src/main.py --jira "PROJ-123"
```

## Running Tests

To run the unit tests using pytest, use the following command from the project root directory:

```
PYTHONPATH=. pytest tests/
```

This command sets the PYTHONPATH to include the current directory, allowing pytest to find the `src` module.