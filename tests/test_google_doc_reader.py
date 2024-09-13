import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from src.google_doc_reader import GoogleDocReader
from google.auth.exceptions import MalformedError

@pytest.fixture
def mock_credentials():
    with patch('src.google_doc_reader.service_account.Credentials.from_service_account_file') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_build():
    with patch('src.google_doc_reader.build') as mock:
        yield mock

@pytest.fixture
def mock_open():
    with patch('builtins.open', create=True) as mock:
        mock.return_value.__enter__.return_value.read.return_value = '{"type": "service_account"}'
        yield mock

@pytest.fixture
def mock_json_load():
    with patch('json.load') as mock:
        mock.return_value = {"type": "service_account"}
        yield mock

def test_read_google_doc_success(mock_credentials, mock_build, mock_open, mock_json_load):
    mock_docs = MagicMock()
    mock_docs.documents().get().execute.return_value = {
        'title': 'Test Document',
        'body': {
            'content': [
                {'paragraph': {'elements': [{'textRun': {'content': 'Test content'}}]}}
            ]
        }
    }
    mock_build.return_value = mock_docs

    reader = GoogleDocReader()
    result = reader.read_document('https://docs.google.com/document/d/abc123/edit')

    expected_output = {
        'title': 'Test Document',
        'content': 'Test content'
    }
    assert result == expected_output

def test_read_google_sheet_success(mock_credentials, mock_build, mock_open, mock_json_load):
    mock_sheets = MagicMock()
    mock_sheets.spreadsheets().values().get().execute.return_value = {
        'values': [
            ['Header 1', 'Header 2'],
            ['Value 1', 'Value 2']
        ]
    }
    mock_build.return_value = mock_sheets

    reader = GoogleDocReader()
    result = reader.read_sheet('https://docs.google.com/spreadsheets/d/abc123/edit')

    expected_output = [
        ['Header 1', 'Header 2'],
        ['Value 1', 'Value 2']
    ]
    assert result == expected_output

def test_initialization_failure(mock_credentials, mock_open, mock_json_load):
    mock_credentials.side_effect = MalformedError("Test error")

    with pytest.raises(RuntimeError):
        GoogleDocReader()

def test_read_document_without_initialization(mock_credentials, mock_build, mock_open, mock_json_load):
    mock_credentials.side_effect = MalformedError("Test error")

    reader = GoogleDocReader()
    with pytest.raises(RuntimeError, match="Google Docs service is not initialized. Check your credentials."):
        reader.read_document('https://docs.google.com/document/d/abc123/edit')

def test_read_sheet_without_initialization(mock_credentials, mock_build, mock_open, mock_json_load):
    mock_credentials.side_effect = MalformedError("Test error")

    reader = GoogleDocReader()
    with pytest.raises(RuntimeError, match="Google Sheets service is not initialized. Check your credentials."):
        reader.read_sheet('https://docs.google.com/spreadsheets/d/abc123/edit')

def test_oauth_flow(mock_credentials, mock_build, mock_open, mock_json_load):
    with patch('src.google_doc_reader.Flow.from_client_config') as mock_flow:
        mock_flow.return_value.run_local_server.return_value = MagicMock()
        mock_json_load.return_value = {"installed": {"client_id": "test", "client_secret": "test"}}
        
        reader = GoogleDocReader()
        assert reader.docs_service is not None
        assert reader.sheets_service is not None

def test_file_not_found(mock_open):
    mock_open.side_effect = FileNotFoundError("File not found")

    with pytest.raises(RuntimeError):
        GoogleDocReader()

def test_json_decode_error(mock_open, mock_json_load):
    mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

    with pytest.raises(RuntimeError):
        GoogleDocReader()