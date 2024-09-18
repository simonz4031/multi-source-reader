import os
from urllib.parse import urlparse, unquote
from jira import JIRA
from atlassian import Confluence
from atlassian.errors import ApiError

class JiraAndConfluenceReader:
    def __init__(self):
        self.domain = os.getenv('JIRA_DOMAIN')
        self.email = os.getenv('JIRA_EMAIL')
        self.token = os.getenv('JIRA_TOKEN')
        self.jira = JIRA(server=self.domain, basic_auth=(self.email, self.token))
        self.confluence = Confluence(
            url=self.domain,
            username=self.email,
            password=self.token,
            cloud=True
        )

    def check_confluence_connection(self):
        try:
            spaces = self.confluence.get_all_spaces(start=0, limit=1)
            return f"Connected successfully. Found {len(spaces)} spaces."
        except Exception as e:
            return str(e)

    def read_ticket(self, ticket_key):
        issue = self.jira.issue(ticket_key)
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'description': issue.fields.description,
            'comments': [comment.body for comment in issue.fields.comment.comments]
        }

    def read_confluence_page_by_url(self, url):
        print(f"Attempting to read Confluence page: {url}")
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('/')
            
            # Find the index of 'spaces' in the path
            try:
                space_index = path_parts.index('spaces')
                space_key = path_parts[space_index + 1]
                page_id = path_parts[-1]
            except ValueError:
                print("Error: Unable to parse space key from URL")
                return {'error': "Unable to parse space key from URL"}
            
            print(f"Extracted page_id: {page_id}, space_key: {space_key}")
            
            # Try to get space info to check permissions
            try:
                space_info = self.confluence.get_space(space_key)
                print(f"Successfully accessed space: {space_key}")
            except Exception as e:
                print(f"Error accessing space {space_key}: {str(e)}")
                return {'error': f"Error accessing Confluence space: {str(e)}"}
            
            # Try to get page by ID first
            try:
                page = self.confluence.get_page_by_id(page_id, expand='body.storage')
                print(f"Successfully retrieved page with ID: {page_id}")
                return {
                    'id': page['id'],
                    'title': page['title'],
                    'content': page['body']['storage']['value']
                }
            except Exception as e:
                print(f"Error retrieving page with ID {page_id}: {str(e)}")
                
                # If page ID fails, try by title
                try:
                    page_title = unquote(page_id.replace('+', ' '))
                    page = self.confluence.get_page_by_title(space_key, page_title, expand='body.storage')
                    print(f"Successfully retrieved page by title: {page_title}")
                    return {
                        'id': page['id'],
                        'title': page['title'],
                        'content': page['body']['storage']['value']
                    }
                except Exception as e:
                    print(f"Error retrieving page by title {page_title}: {str(e)}")
                    return {'error': f"Error reading Confluence page: {str(e)}"}
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {'error': f"Unexpected error reading Confluence page: {str(e)}"}