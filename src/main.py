from flask import Flask, Blueprint
from backend import bp as backend_bp
from object import bp as object_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(backend_bp)
app.register_blueprint(object_bp)


# ping test function
@app.route('/ping', methods=['GET'])
def ping():
	return {'msg': 'pong'}

if __name__ == '__main__':
	app.run(debug=True)
