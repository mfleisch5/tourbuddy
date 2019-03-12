import json

def api():
    with open('config.json', 'r') as jf:
        return json.load(jf)['api']

