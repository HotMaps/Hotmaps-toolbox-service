import requests
from .. import BASE_URL

url = BASE_URL + "/users/login"

payload = {
    "email": "hotmapstest@gmail.com",
    "password": "weqriogvyx"
}

output = requests.post(url, json=payload)

test_token = output.json()['token']
