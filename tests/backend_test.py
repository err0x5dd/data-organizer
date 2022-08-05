import requests

URL='http://127.0.0.1:5000'
VERSION = '/v1'
BASE = URL + VERSION

print('GET all')
response = requests.get(BASE + '/backends/')
print(response.json())

print('POST test-backend-1')
response = requests.post(BASE + '/backends/', json={'name': 'test-backend-1'})
print(response.json())
location = response.headers.get('Location')

print('POST test-backend-2')
response = requests.post(BASE + '/backends/', json={'name': 'test-backend-2'})
print(response.json())

print('GET all')
response = requests.get(BASE + '/backends/')
print(response.json())

print('GET ID 0 (test-backend-1)')
response = requests.get(URL + location)
print(response.json())

print('PUT ID 0 (test-backend-1 -> test-backend-old)')
response = requests.put(URL + location, json={'name': 'test-backend-old'})
print(response.json())

print('DELETE ID 0 (test-backend-old')
response = requests.delete(URL + location)
print('No returned content on DELETE')

print('GET ID 0 (deleted)')
response = requests.get(URL + location)
print('Status: ' + str(response.status_code))

print('GET all')
response = requests.get(BASE + '/backends/')
print(response.json())
input()
response = requests.delete(BASE + '/backends/')
print('No returned content on DELETE')
