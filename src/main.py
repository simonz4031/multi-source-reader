import argparse
import sys
import json
import os
from dotenv import load_dotenv
from src.github_pr_reader import GitHubPRReader
from src.google_doc_reader import GoogleDocReader
from src.jira_ticket_reader import JiraAndConfluenceReader

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
    parser.add_argument('-g', '--github', help='GitHub PR title or URL')
    parser.add_argument('-d', '--google', help='Google Doc/Sheet URL')
    parser.add_argument('-j', '--jira', help='Jira ticket key')
    parser.add_argument('-c', '--confluence', help='Confluence page URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    # Enable debug mode by default for now
    args.debug = True

    if args.confluence:
        debug_print(f"Attempting to read Confluence page: {args.confluence}", args.debug)
        reader = JiraAndConfluenceReader()
        
        # Check Confluence connection
        connection_status = reader.check_confluence_connection()
        debug_print(f"Confluence connection status: {connection_status}", args.debug)

        if "Connected successfully" not in connection_status:
            debug_print(f"Error connecting to Confluence: {connection_status}", args.debug)
            return

        try:
            result = reader.read_confluence_page_by_url(args.confluence)
            debug_print("Raw result:", args.debug)
            debug_print(str(result), args.debug)
            if 'error' in result:
                debug_print(f"Error: {result['error']}", args.debug)
            else:
                print_result(result)
        except Exception as e:
            debug_print(f"An unexpected error occurred: {str(e)}", args.debug)

    elif args.github:
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
        reader = JiraAndConfluenceReader()
        result = reader.read_ticket(args.jira)
        print_result(result)

    else:
        debug_print("Please provide a valid argument. Use -h or --help for more information.", args.debug)

def print_result(result):
    print(json.dumps(result, indent=2))

def debug_print(message, debug_enabled):
    if debug_enabled:
        print(message, file=sys.stderr)

def run():
    main()

if __name__ == '__main__':
    run()