import urllib.request
import urllib.parse
import json

def test_actions():
    try:
        # Token
        url = "http://localhost:8001/token"
        data = urllib.parse.urlencode({"username": "favorite restaurant", "password": "1234"}).encode()
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode())
            token = resp_data["access_token"]
            print("Token obtained successfully.")
        
        # Actions
        url = "http://localhost:8001/api/actions"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode())
            actions = resp_data["actions"]
            print(f"Found {len(actions)} actions.")
            types = [a['type'] for a in actions]
            print(f"Action types found: {set(types)}")
            
            recs = [a for a in actions if a['type'] == 'recommendations']
            if recs:
                print(f"Found {len(recs)} recommendations.")
                print(json.dumps(recs[0], indent=2))
            else:
                print("No recommendations returned.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_actions()
