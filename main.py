import requests

# Example GET request
response = requests.get('https://www.example.com')
print(response.status_code)
print(response.text)