import requests
from requests.auth import HTTPBasicAuth

urlToken = 'http://localhost:5000/api/v2/login'
url = 'http://localhost:5000/api/v2/protected'

auth = HTTPBasicAuth('nifi', 'nifi')


response = requests.get(urlToken, auth=auth)

if response.status_code == 200:
    access_token = response.json()['access_token']
    print('Access token:', access_token)
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)
else:
    print('Failed to get access token')


print('Response:')
print(response.json())