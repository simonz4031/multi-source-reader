# Multi-Source Reader

This console Python program allows you to read information from various sources, including GitHub pull requests, Google Docs/Sheets, Jira tickets, and Confluence pages.

## Setup

1. Clone the repository and navigate to the project directory:
   ```
   git clone https://github.com/yourusername/multi-source-reader.git
   cd multi-source-reader
   ```

2. If you're using Miniconda, create and activate a new environment:
   ```
   conda create -n multi-source-reader python=3.8
   conda activate multi-source-reader
   ```

3. Install the package:
   ```
   pip install -e .
   ```

4. Set up the necessary credentials:
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

## Usage

After installation, you can use the `multi-source-reader` command from anywhere:

1. GitHub PR:
   ```
   multi-source-reader -g "PR Title"
   ```
   or
   ```
   multi-source-reader -g "https://github.com/owner/repo/pull/123"
   ```

2. Google Doc:
   ```
   multi-source-reader -d "https://docs.google.com/document/d/your-doc-id/edit"
   ```

3. Google Sheet:
   ```
   multi-source-reader -d "https://docs.google.com/spreadsheets/d/your-sheet-id/edit"
   ```

4. Jira Ticket:
   ```
   multi-source-reader -j "PROJ-123"
   ```

5. Confluence Page:
   ```
   multi-source-reader -c "https://your-domain.atlassian.net/wiki/spaces/SPACE/pages/PAGE-ID/Page+Title"
   ```

For more information on available options, use:
```
multi-source-reader -h
```
## Running Tests

To run the unit tests using pytest, use the following command from the project root directory:

```
pytest
```