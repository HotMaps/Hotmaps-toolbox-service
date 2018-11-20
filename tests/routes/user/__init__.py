import requests

url = "http://192.168.99.100/api/users/login"

payload = {
    "email": "hotmapstest@gmail.com",
    "password": "weqriogvyx"
}

output = requests.post(url, json=payload)

test_token = output.json()['token']
