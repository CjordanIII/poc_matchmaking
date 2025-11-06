# import requests

# # Example GET request
# response = requests.get('https://www.example.com')
# print(response.status_code)
# print(response.text)

from filter.location import filter_by_location
from json_parser import parse_json_file

users = parse_json_file('data/users.json')


if(__name__ == "__main__"):
    by_location = filter_by_location(users)
    print(by_location)
    print("This is the main module.")