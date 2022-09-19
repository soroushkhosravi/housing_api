"""The definition of the flask app and it's endpoints."""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    """The definition of the index endpoint."""
    return jsonify({'status': 'healthy'})

@app.route('/index')
def index():
    return jsonify({'page': 'index'})

@app.route('/endpoint')
def end_point():
    """An example of an endpoint."""
    return jsonify({'response': 'response'})