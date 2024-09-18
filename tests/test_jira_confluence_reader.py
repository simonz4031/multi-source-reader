import pytest
from unittest.mock import patch, MagicMock
from src.jira_ticket_reader import JiraAndConfluenceReader

@pytest.fixture
def mock_confluence():
    with patch('src.jira_ticket_reader.Confluence') as mock:
        yield mock

@pytest.fixture
def mock_jira():
    with patch('src.jira_ticket_reader.JIRA') as mock:
        yield mock

@pytest.fixture
def mock_env_vars():
    with patch.dict('os.environ', {
        'JIRA_DOMAIN': 'https://test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_TOKEN': 'test_token'
    }):
        yield

def test_check_confluence_connection_success(mock_confluence, mock_env_vars):
    mock_confluence.return_value.get_all_spaces.return_value = [{'key': 'TEST'}]
    reader = JiraAndConfluenceReader()
    result = reader.check_confluence_connection()
    assert "Connected successfully" in result
    assert "Found 1 spaces" in result

def test_check_confluence_connection_failure(mock_confluence, mock_env_vars):
    mock_confluence.return_value.get_all_spaces.side_effect = Exception("Connection failed")
    reader = JiraAndConfluenceReader()
    result = reader.check_confluence_connection()
    assert "Connection failed" in result

def test_read_confluence_page_by_url_success(mock_confluence, mock_env_vars):
    mock_confluence.return_value.get_space.return_value = {'key': 'TEST'}
    mock_confluence.return_value.get_page_by_id.return_value = {
        'id': '123',
        'title': 'Test Page',
        'body': {'storage': {'value': 'Test content'}}
    }
    reader = JiraAndConfluenceReader()
    result = reader.read_confluence_page_by_url("https://test.atlassian.net/wiki/spaces/TEST/pages/123/Test+Page")
    assert result == {
        'id': '123',
        'title': 'Test Page',
        'content': 'Test content'
    }

def test_read_confluence_page_by_url_failure(mock_confluence, mock_env_vars):
    mock_confluence.return_value.get_space.side_effect = Exception("Space not found")
    reader = JiraAndConfluenceReader()
    result = reader.read_confluence_page_by_url("https://test.atlassian.net/wiki/spaces/TEST/pages/123/Test+Page")
    assert 'error' in result
    assert "Error accessing Confluence space" in result['error']

def test_read_confluence_page_by_url_invalid_url(mock_confluence, mock_env_vars):
    reader = JiraAndConfluenceReader()
    result = reader.read_confluence_page_by_url("https://invalid-url.com")
    assert 'error' in result
    assert "Unable to parse space key from URL" in result['error']

def test_read_ticket(mock_jira, mock_env_vars):
    mock_issue = MagicMock()
    mock_issue.key = 'TEST-123'
    mock_issue.fields.summary = 'Test Summary'
    mock_issue.fields.description = 'Test Description'
    mock_issue.fields.comment.comments = [MagicMock(body='Test Comment')]
    mock_jira.return_value.issue.return_value = mock_issue

    reader = JiraAndConfluenceReader()
    result = reader.read_ticket('TEST-123')

    assert result == {
        'key': 'TEST-123',
        'summary': 'Test Summary',
        'description': 'Test Description',
        'comments': ['Test Comment']
    }