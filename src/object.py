from flask import Blueprint, request, make_response, send_file
from werkzeug.utils import secure_filename
import json
import time
import os
import hashlib
import backend

bp = Blueprint('object', __name__, url_prefix='/v1/objects')

data = []
data_lock = False

###
# Resource Group Operations
###
@bp.route('/', methods=['GET'])
def get_all():
	return json.dumps([o.toJSON() for o in data if o is not None])

@bp.route('/', methods=['POST'])
def create():
	global data_lock

	# Decode received data
	name = request.json.get('name')
	sha512 = request.json.get('sha512')
	collections = request.json.get('collections')
	backends = request.json.get('backends')

	# TODO: Check for valid backends and collections
	for b in backends:
		if not backend.check_id(int(b)):
			return {'msg': 'Invalid backend id: ' + str(b)}, 404
	
	while data_lock:
		time.sleep(0.010) # Wait for 10 ms
	data_lock = True
	index = len(data)
	entry = Object(index, name, sha512, collections, backends)
	data.append(entry)
	data_lock = False
	
	response = make_response(entry.toJSON(), 201)
	response.headers['Location'] = request.path + str(index)
	return response

@bp.route('/', methods=['DELETE'])
def delete_all():
	data.clear()
	return '', 204

###
# Object Operations
###
@bp.route('/<int:object_id>', methods=['GET'])
def get(object_id):
	if object_id >= len(data):
		return '', 404
	elif data[object_id] is None:
		return '', 404
	else:
		return data[object_id].toJSON()

@bp.route('/<int:object_id>', methods=['PUT'])
def put(object_id):
	if object_id >= len(data):
		return '', 404
	
	# Decode received data
	name = request.json.get('name')
	sha512 = request.json.get('sha512')
	collections = request.json.get('collections')
	backends = request.json.get('backends')

	data[object_id] = Object(object_id, name, sha512, collections, backends)
	return data[object_id].toJSON()

@bp.route('/<int:object_id>', methods=['DELETE'])
def delete(object_id):
	if object_id >= len(data):
		return '', 404

	data[object_id] = None
	return '', 204

# DELETE: can be tested with: curl -F 'file=@/path/to/file' http://127.0.0.1:5000/v1/objects/{id}/blob
@bp.route('/<int:object_id>/blob', methods=['PUT'])
def put_blob(object_id):
	if object_id >= len(data):
		return '', 404
	elif data[object_id] is None:
		return '', 404

	if 'file' not in request.files:
		return {'msg': 'form-object with name \'file\' is missing'}, 400
	file = request.files['file']
	if file.filename == '':
		return {'msg': 'form-object with name \'file\' is empty'}, 400
	#filename = secure_filename(file.filename)
	filename = secure_filename(data[object_id].name)
	bytes = file.read()

	sha512 = hashlib.sha512(bytes).hexdigest();

	if sha512 == data[object_id].sha512 or data[object_id].sha512 == None:
	#if True:
		with open(os.path.join('uploads/', filename), 'wb') as f:
			f.write(bytes)
		if data[object_id].sha512 == None:
			data[object_id].sha512 = sha512
		return '', 200
	else:
		return {'msg': 'Saved sha512 value doesn\'t match uploaded file'}, 400

@bp.route('/<int:object_id>/blob', methods=['GET'])
def get_blob(object_id):
	if object_id >= len(data):
		return '', 404
	elif data[object_id] is None:
		return '', 404

	for b in backend.prioritize(data[object_id].backends):
		if backend.validate(b, secure_filename(data[object_id].name), data[object_id].sha512):
			#return send_file(
			#	backend.download(b, secure_filename(data[object_id].name)),
			#	download_name=secure_filename(data[object_id].name)
			#)
			return backend.download(b, secure_filename(data[object_id].name))

###
# Object Classes
###
class Object():
	def __init__(self,
			object_id=None,
			name=None,
			sha512=None,
			collections=None,
			backends=None):
		self.object_id = object_id
		self.name = name
		self.sha512 = sha512
		self.collections = collections
		self.backends = backends
	
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__)
