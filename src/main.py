import argparse
import sys
import json
import os
from dotenv import load_dotenv
from .github_pr_reader import GitHubPRReader
from .google_doc_reader import GoogleDocReader
from .jira_ticket_reader import JiraTicketReader

def load_environment():
    # Try to load .env from the current directory
    if os.path.exists('.env'):
        load_dotenv()
    # If not found, try to load from the home directory
    elif os.path.exists(os.path.expanduser('~/.env')):
        load_dotenv(os.path.expanduser('~/.env'))
    else:
        print("Warning: .env file not found in current or home directory.", file=sys.stderr)

def main():
    load_environment()

    parser = argparse.ArgumentParser(description='Read information from various sources')
    parser.add_argument('--github', help='GitHub PR title or URL')
    parser.add_argument('--google', help='Google Doc/Sheet URL')
    parser.add_argument('--jira', help='Jira ticket key')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    if args.github:
        reader = GitHubPRReader()
        if args.github.startswith('http'):
            result = reader.read_pr_by_url(args.github)
        else:
            result = reader.read_pr_by_title(args.github)
        print_result(result)

    elif args.google:
        try:
            reader = GoogleDocReader()
            if 'document' in args.google:
                result = reader.read_document(args.google)
            elif 'spreadsheets' in args.google:
                result = reader.read_sheet(args.google)
            else:
                debug_print("Invalid Google URL", args.debug)
                sys.exit(1)
            print_result(result)
        except RuntimeError as e:
            debug_print(f"Error: {e}", args.debug)
            debug_print("Please check your google-credentials.json file and ensure it contains the correct information.", args.debug)
        except Exception as e:
            debug_print(f"An unexpected error occurred: {e}", args.debug)

    elif args.jira:
        reader = JiraTicketReader()
        result = reader.read_ticket(args.jira)
        print_result(result)

    else:
        debug_print("Please provide a valid argument. Use --help for more information.", args.debug)

def print_result(result):
    print(json.dumps(result, indent=2))

def debug_print(message, debug_enabled):
    if debug_enabled:
        print(message, file=sys.stderr)

if __name__ == '__main__':
    main()