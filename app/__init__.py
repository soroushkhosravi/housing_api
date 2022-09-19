"""The definition of the flask app and it's endpoints."""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    """The definition of the index endpoint."""
    return jsonify({'status': 'healthy'})


@app.route('/index')
def index():
    """The definition of the index endpoint."""
    return jsonify({'page': 'index'})


@app.route('/endpoint')
def endpoint():
    """The definition of the index endpoint."""
    return jsonify({'page': 'index'})