import requests
import json

def test_history():
    url = "http://localhost:8000/api/history?thread_id=1"
    try:
        print(f"Calling {url}...")
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2))
            if "messages" in data:
                print(f"SUCCESS: Found {len(data['messages'])} messages.")
            else:
                print("FAILURE: 'messages' key not found in response.")
        else:
            print(f"FAILURE: Received status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_history()
