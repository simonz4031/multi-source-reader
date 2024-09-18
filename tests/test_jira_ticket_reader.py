import pytest
from unittest.mock import patch, MagicMock
from src.jira_ticket_reader import JiraAndConfluenceReader

@pytest.fixture
def mock_jira():
    with patch('src.jira_ticket_reader.JIRA') as mock:
        yield mock

@pytest.fixture
def mock_getenv():
    with patch('src.jira_ticket_reader.os.getenv') as mock:
        mock.side_effect = lambda x: {
            'JIRA_DOMAIN': 'https://example.atlassian.net',
            'JIRA_EMAIL': 'test@example.com',
            'JIRA_TOKEN': 'fake_token'
        }[x]
        yield mock

def test_read_ticket(mock_jira, mock_getenv):
    mock_issue = MagicMock()
    mock_issue.key = 'PROJ-123'
    mock_issue.fields.summary = 'Test Issue'
    mock_issue.fields.description = 'Issue description'
    mock_issue.fields.comment.comments = [MagicMock(body='Comment 1')]
    mock_jira.return_value.issue.return_value = mock_issue

    reader = JiraAndConfluenceReader()
    result = reader.read_ticket('PROJ-123')

    expected_output = {
        'key': 'PROJ-123',
        'summary': 'Test Issue',
        'description': 'Issue description',
        'comments': ['Comment 1']
    }
    assert result == expected_output