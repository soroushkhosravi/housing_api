"""The definition of the flask app and it's endpoints."""
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/health')
def health():
    """The definition of the index endpoint."""
    return jsonify({'status': 'healthy'})


@app.route('/home')
@app.route('/')
def home():
    """The definition of the index endpoint."""
    return render_template('home.html')

@app.route('/second', methods=['POST', 'GET'])
def second():
    """This shows the second form in the flow."""
    return render_template('job.html')


@app.route('/third', methods=['POST', 'GET'])
def third():
    """This shows the third form."""
    form_data = request.form
    all_fields = ''
    all_valus = ''
    for key in form_data.keys():
        all_fields = all_fields + ' ' + str(key)
        all_valus = all_valus + ' ' + str(form_data[key])

    return jsonify({'keys': all_fields, 'values': all_valus})

@app.route('/about')
def about():
    """Returns the about endpoint."""
    return jsonify({'message': 'This is the about page.'})