# scripts/my_cli.py
import argparse
import webbrowser
import requests
import json
import os

COMPOSIO_TOKEN = 'ghp_1J2g3h4i5j6k7l8m9n0o33'
BASE_URL = "https://hermes-production-6901.up.railway.app/api"

def save_user_id(user_id):
    user_data = {'user_id': user_id}
    # TODO: Need to change to some other location once pip package is created.
    with open('user_data.json', 'w') as outfile:
        json.dump(user_data, outfile)

def get_user_id():
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as infile:
            user_data = json.load(infile)
            return user_data.get('user_id')
    return None

def auth(args):
    if not args.email:
        print("Error: Email ID is required for authentication.")
        return
    print(f"Authenticating {args.email}...")
    url = f"{BASE_URL}/user/create/{args.email}"
    headers = {
      'X_COMPOSIO_TOKEN': COMPOSIO_TOKEN
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        user_id = response.json().get('userId')
        print(f"Authenticated successfully. User ID: {user_id}")
        save_user_id(user_id)
    else:
        print("Authentication failed.")

def list_tools(args):
    user_id = get_user_id()
    if user_id is None:
        print("Error: No authenticated user found. Please authenticate first.")
        return
    print(f"Fetching tools for User ID: {user_id}...")
    url = f"{BASE_URL}/tools"
    headers = {
      'X_COMPOSIO_TOKEN': COMPOSIO_TOKEN,
      'X_ENDUSER_ID': user_id
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tools_data = response.json()
        for tool in tools_data.get('tools', []):
            print(f"Name: {tool['Name']}, Description: {tool['Description']}")
            if args.auth and tool['Authentication']['isAuthenticated'] == "False":
                print(f"Tool {tool['Name']} requires authentication.")
    else:
        print("Failed to fetch tools.")

def auth_tool(args):
    user_id = get_user_id()
    if user_id is None:
        print("Error: No authenticated user found. Please authenticate first.")
        return
    print(f"Authenticating tool: {args.tool_name} for User ID: {user_id}")
    url = f"{BASE_URL}/user/auth"
    payload = json.dumps({
      "endUserID": user_id,
      "provider": {
        "name": args.tool_name,
        "scope": [
          "user.email",
          "user.profile"
        ]
      },
      "redirectURIClient": "https://composio.dev/"
    })
    headers = {
      'X_COMPOSIO_TOKEN': COMPOSIO_TOKEN,
      'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        auth_url = response.json().get('providerAuthURL')
        webbrowser.open(auth_url)
    else:
        print("Failed to authenticate tool.")

def main():
    parser = argparse.ArgumentParser(description='Authenticate and use package')
    subparsers = parser.add_subparsers(help='commands')

    # Auth command
    auth_parser = subparsers.add_parser('auth', help='Authenticate user')
    auth_parser.add_argument('email', type=str, help='User email ID for authentication')
    auth_parser.set_defaults(func=auth)

    # List tools command
    list_tools_parser = subparsers.add_parser('list_tools', help='List tools')
    list_tools_parser.add_argument('--auth', action='store_true', help='List only authenticated tools')
    list_tools_parser.set_defaults(func=list_tools)

    # Auth tool command
    auth_tool_parser = subparsers.add_parser('auth_tool', help='Authenticate a tool')
    auth_tool_parser.add_argument('tool_name', type=str, help='Name of the tool to authenticate')
    auth_tool_parser.set_defaults(func=auth_tool)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()