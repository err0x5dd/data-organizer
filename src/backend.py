from flask import Blueprint, request, make_response, send_file
import json
import time
import os
import hashlib

bp = Blueprint('backend', __name__, url_prefix='/v1/backends')

data = []
data_lock = False

###
# General functions
###
def check_id(backend_id):
	if backend_id >= len(data):
		return False
	elif data[backend_id] is None:
		return False
	else:
		return True

def prioritize(backend_ids):
	print('backend.prioritize not yet implemented')
	return backend_ids

def upload(backend_id, filename, filebytes):
	if check_id(backend_id):
		match data[backend_id].type:
			case 'file':
				return upload_file(backend_id, filename, filebytes)
			case 's3' | 'webdav':
				print('Saving to backend type ' + data[backend_id].type + ' is not yet implemented')
				return False
			case _:
				print('Unkown backend type: ' + data[backend_id].type)
				return False

def validate(backend_id, filename, sha512):
	if check_id(backend_id):
		match data[backend_id].type:
			case 'file':
				return validate_file(backend_id, filename, sha512)
			case 's3' | 'webdav':
				print('Validation from backend type ' + data[backend_id].type + ' is not yet implemented')
				return False
			case _:
				print('Unkown backend type: ' + data[backend_id].type)
				return False

def download(backend_id, filename):
	if check_id(backend_id):
		match data[backend_id].type:
			case 'file':
				return download_file(backend_id, filename)
			case 's3' | 'webdav':
				print('Downloading from backend type ' + data[backend_id].type + ' is not yet implemented')
				return False
			case _:
				print('Unkown backend type: ' + data[backend_id].type)
				return False

def upload_file(backend_id, filename, filebytes):
	path = os.path.join(data[backend_id].config.get('path'), filename)
	if not os.path.isdir(path):
		os.makedirs(path)
	with open(path, 'wb') as f:
		f.write(filebytes)
	return True

def validate_file(backend_id, filename, sha512):
	path = os.path.join(data[backend_id].config.get('path'), filename)
	with open(path, 'rb') as f:
		filebytes = f.read()
	calc_sha512 = hashlib.sha512(filebytes).hexdigest();
	if sha512 == calc_sha512:
		return True
	else:
		return False

def download_file(backend_id, filename):
	path = os.path.join(data[backend_id].config.get('path'), filename)
	f = open(path, 'rb')
	#return f
	return send_file(
		f,
		download_name=filename
	)

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
	description = request.json.get('description')
	priority = request.json.get('priority') if request.json.get('priority') is not None else 0
	type = request.json.get('type')
	config = request.json.get('config')

	# TODO check required config fields according to type
	match type:
		case 'file':
			if config.get('path') is None:
				return {'msg': 'Type "file" requires "config" key "path"'}, 400
		case 's3' | 'webdav':
			return {'msg': 'Type "' + type + '" not yet implemented'}, 400
		case _:
			return {'msg': 'Type "' + type + '" unkown'}, 400

	
	while data_lock:
		time.sleep(0.010) # Wait for 10 ms
	data_lock = True
	index = len(data)
	entry = Backend(index, name, description, priority, type, config)
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
@bp.route('/<int:backend_id>', methods=['GET'])
def get(backend_id):
	if check_id(backend_id):
		return data[backend_id].toJSON()
	else:
		return '', 404

@bp.route('/<int:backend_id>', methods=['PUT'])
def put(backend_id):
	if backend_id >= len(data):
		return '', 404
	
	# Decode received data
	name = request.json.get('name')
	description = request.json.get('description')
	priority = request.json.get('priority') if request.json.get('priority') is not None else 0
	type = request.json.get('type')
	config = request.json.get('config')

	data[backend_id] = Backend(backend_id, name, description, priority, type, config)
	return data[backend_id].toJSON()

@bp.route('/<int:backend_id>', methods=['DELETE'])
def delete(backend_id):
	if not check_id(backend_id):
		return '', 404

	data[backend_id] = None
	return '', 204

###
# Object Classes
###
class Backend():
	def __init__(self,
			backend_id=None,
			name=None,
			description=None,
			priority=0,
			type=None,
			config=None):
		self.backend_id = backend_id
		self.name = name
		self.description = description
		self.priority = priority
		self.type = type
		self.config = config
	
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__)
