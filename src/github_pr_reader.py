import os
from github import Github
from urllib.parse import urlparse

class GitHubPRReader:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER')
        self.repo_name = os.getenv('GITHUB_REPO')
        self.github = Github(self.token)

    def read_pr_by_title(self, title):
        repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        pulls = repo.get_pulls(state='all')
        for pr in pulls:
            if pr.title == title:
                return self._get_pr_info(pr)
        raise ValueError(f"No pull request found with title: {title}")

    def read_pr_by_url(self, url):
        parts = urlparse(url)
        path_parts = parts.path.split('/')
        repo_name = '/'.join(path_parts[1:3])
        pr_number = int(path_parts[-1])
        
        repo = self.github.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        return self._get_pr_info(pr)

    def _get_pr_info(self, pr):
        return {
            'title': pr.title,
            'number': pr.number,
            'description': pr.body,
            'comments': [comment.body for comment in pr.get_comments()],
            'file_changes': [{'file': file.filename, 'patch': file.patch} for file in pr.get_files()]
        }