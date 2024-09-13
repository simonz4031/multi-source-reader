import os
from jira import JIRA

class JiraTicketReader:
    def __init__(self):
        self.domain = os.getenv('JIRA_DOMAIN')
        self.email = os.getenv('JIRA_EMAIL')
        self.token = os.getenv('JIRA_TOKEN')
        self.jira = JIRA(server=self.domain, basic_auth=(self.email, self.token))

    def read_ticket(self, ticket_key):
        issue = self.jira.issue(ticket_key)
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'description': issue.fields.description,
            'comments': [comment.body for comment in issue.fields.comment.comments]
        }