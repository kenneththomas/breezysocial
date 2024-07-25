import sys
sys.path.append('../')
sys.path.append('../simulate_tools')
from simulate_tools.poast import poast
import json
import personality

def parse_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    
    for entry in data:
        username = entry['username']
        timestamp = entry['timestamp']
        text = entry['text']

        # For demonstration, print the extracted variables
        print("Username:", username)
        print("Timestamp:", timestamp)
        print("Text:", text)
        print("-------------")

        if username in personality.remapping:
            username_old = username
            username = personality.remapping[username]
            print(f'remapped {username_old} to {username}')

        # Post the tweet
        postid = poast(username, text, timestamp)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py json_filename")
        sys.exit(1)

    filename = sys.argv[1]
    parse_json_file(filename)