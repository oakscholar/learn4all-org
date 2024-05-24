import requests

try:
    response = requests.get('https://www.google.com')
    print(response.status_code)
except requests.ConnectionError as e:
    print(f"Connection error: {e}")