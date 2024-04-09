import json
import os
import requests

DEFECTDOJO_HOST = 'https://demo.defectdojo.org'
DEFECTDOJO_USER = 'admin'
DEFECTDOJO_PASSWORD = '1Defectdojo@demo#appsec'

req_url_auth = f"{DEFECTDOJO_HOST}/api/v2/api-token-auth/"
headers = {"Content-Type": "application/json"}
payload = json.dumps({"username": DEFECTDOJO_USER, "password": DEFECTDOJO_PASSWORD})
response = requests.request("POST", req_url_auth, data=payload, headers=headers)
token = response.json()["token"]
req_url_settings = f"{DEFECTDOJO_HOST}/api/v2/system_settings/1/"
headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
payload = json.dumps({"enable_deduplication": True, "delete_duplicates": True, "max_dupes": 2})
response = requests.request("PUT", req_url_settings, data=payload, headers=headers)

print(response.json())
