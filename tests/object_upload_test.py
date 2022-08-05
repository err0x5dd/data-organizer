import requests
from requests.exceptions import JSONDecodeError
import hashlib

URL='http://127.0.0.1:5000'
VERSION = '/v1'
BASE = URL + VERSION


print('Create backend')
response = requests.post(BASE + '/backends/', json={
	'name': 'testbackend',
	'type': 'file',
	'config': {
		'path': './uploads/'
	}
})
print(response.json())
backend_id = response.headers.get('Location').split('/')[-1]


print('Create object')
response = requests.post(BASE + '/objects/', json={
	'name': '_testfile',
	'sha512': '5626a79cbc9ffe28dfc1b525a58864a3aa7b1c110ad13bf229394b2ef969b2d09f482d213d40ce7f4dada458779df1616eb7b81c6002fa353949e9b29a8a1781',
	'backends': [
		int(backend_id)
	]
})
print(response.json())
object_id = response.headers.get('Location').split('/')[-1]


print('Upload object data')
with open('_testfile', 'rb') as f:
	response = requests.put(BASE + '/objects/' + object_id + '/blob', files={'file': f})
try:
	print(response.json())
except JSONDecodeError:
	pass

# Follow redirect ?

if response.ok:
	print('OK')
else:
	print('Error with upload')


print('Download object data')
response = requests.get(BASE + '/objects/' + object_id + '/blob')
with open('_testfile.2', 'wb') as f:
	f.write(response.content)
print(response.headers.get('content-type'))

with open('_testfile.2', 'rb') as f:
	bytes = f.read()
print(hashlib.sha512(bytes).hexdigest())
