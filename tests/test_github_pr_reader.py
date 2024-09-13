import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from src.github_pr_reader import GitHubPRReader

@pytest.fixture
def mock_github():
    with patch('src.github_pr_reader.Github') as mock:
        yield mock

@pytest.fixture
def mock_getenv():
    with patch('src.github_pr_reader.os.getenv') as mock:
        mock.side_effect = lambda x: {
            'GITHUB_TOKEN': 'fake_token',
            'GITHUB_REPO_OWNER': 'fake_owner',
            'GITHUB_REPO': 'fake_repo'
        }[x]
        yield mock

def test_read_pr_by_title(mock_github, mock_getenv):
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_pr.title = 'Test PR'
    mock_pr.number = 1
    mock_pr.body = 'PR description'
    mock_pr.get_comments.return_value = [MagicMock(body='Comment 1')]
    mock_pr.get_files.return_value = [MagicMock(filename='file1.py', patch='@@ -1,3 +1,4 @@\n Line1\n+Line2\n Line3\n Line4')]
    mock_repo.get_pulls.return_value = [mock_pr]
    mock_github.return_value.get_repo.return_value = mock_repo

    reader = GitHubPRReader()
    result = reader.read_pr_by_title('Test PR')

    expected_output = {
        'title': 'Test PR',
        'number': 1,
        'description': 'PR description',
        'comments': ['Comment 1'],
        'file_changes': [{'file': 'file1.py', 'patch': '@@ -1,3 +1,4 @@\n Line1\n+Line2\n Line3\n Line4'}]
    }
    assert result == expected_output

def test_read_pr_by_url(mock_github, mock_getenv):
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_pr.title = 'Test PR'
    mock_pr.number = 1
    mock_pr.body = 'PR description'
    mock_pr.get_comments.return_value = [MagicMock(body='Comment 1')]
    mock_pr.get_files.return_value = [MagicMock(filename='file1.py', patch='@@ -1,3 +1,4 @@\n Line1\n+Line2\n Line3\n Line4')]
    mock_repo.get_pull.return_value = mock_pr
    mock_github.return_value.get_repo.return_value = mock_repo

    reader = GitHubPRReader()
    result = reader.read_pr_by_url('https://github.com/fake_owner/fake_repo/pull/1')

    expected_output = {
        'title': 'Test PR',
        'number': 1,
        'description': 'PR description',
        'comments': ['Comment 1'],
        'file_changes': [{'file': 'file1.py', 'patch': '@@ -1,3 +1,4 @@\n Line1\n+Line2\n Line3\n Line4'}]
    }
    assert result == expected_output