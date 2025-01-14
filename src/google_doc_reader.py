import os
import json
import pickle
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import MalformedError
from urllib.parse import urlparse, parse_qs

class GoogleDocReader:
    def __init__(self):
        self.docs_service = None
        self.sheets_service = None
        try:
            credentials_path = self._find_credentials_file()
            token_path = os.path.join(os.path.dirname(credentials_path), 'token.pickle')
            
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Credentials file not found at {credentials_path}")

            with open(credentials_path, 'r') as f:
                cred_data = json.load(f)
                print("Credential file contents:")
                self._print_nested_keys(cred_data)

            if 'installed' in cred_data:
                print("OAuth 2.0 Client ID detected. Using OAuth flow.")
                credentials = self._get_oauth_credentials(cred_data['installed'], token_path)
            else:
                print("Attempting to use Service Account credentials.")
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
                )

            self.docs_service = build('docs', 'v1', credentials=credentials)
            self.sheets_service = build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            print(f"An error occurred during initialization: {str(e)}")
            # Don't raise an exception here, allow the object to be created with uninitialized services

    def _find_credentials_file(self):
        # Check current directory
        if os.path.exists('google-credentials.json'):
            return 'google-credentials.json'
        # Check home directory
        home_creds = os.path.expanduser('~/google-credentials.json')
        if os.path.exists(home_creds):
            return home_creds
        raise FileNotFoundError("google-credentials.json not found in current or home directory")

    def _print_nested_keys(self, data, prefix=''):
        if isinstance(data, dict):
            for key, value in data.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    self._print_nested_keys(value, new_prefix)
                else:
                    print(f"- {new_prefix}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_prefix = f"{prefix}[{i}]"
                self._print_nested_keys(item, new_prefix)

    def _get_oauth_credentials(self, client_config, token_path):
        scopes = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = None
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            except (pickle.UnpicklingError, AttributeError):
                print("Error loading token, proceeding with new authentication.")
                creds = None
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = Flow.from_client_config(
                        {"installed": client_config},
                        scopes=scopes
                    )
                    creds = flow.run_local_server(port=0)
                except AttributeError:
                    print("Falling back to InstalledAppFlow for OAuth authentication.")
                    flow = InstalledAppFlow.from_client_config(
                        {"installed": client_config},
                        scopes=scopes
                    )
                    creds = flow.run_local_server(port=0)
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds

    def read_document(self, url):
        if not self.docs_service:
            raise RuntimeError("Google Docs service is not initialized. Check your credentials.")
        doc_id = self._extract_id_from_url(url)
        document = self.docs_service.documents().get(documentId=doc_id).execute()
        content = ''
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for para_element in element['paragraph']['elements']:
                    if 'textRun' in para_element:
                        content += para_element['textRun']['content']
        return {
            'title': document.get('title', ''),
            'content': content
        }

    def read_sheet(self, url):
        if not self.sheets_service:
            raise RuntimeError("Google Sheets service is not initialized. Check your credentials.")
        sheet_id = self._extract_id_from_url(url)
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='A1:ZZ'
        ).execute()
        return result.get('values', [])

    def _extract_id_from_url(self, url):
        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query).get('id', [None])[0] or parsed_url.path.split('/')[-2]