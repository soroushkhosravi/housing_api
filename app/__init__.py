"""The definition of the flask app and it's endpoints."""
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/health')
def health():
    """The definition of the index endpoint."""
    return jsonify({'status': 'healthy'})


@app.route('/home')
def home():
    """The definition of the index endpoint."""
    return render_template('home.html')

@app.route('/second', methods=['POST'])
def second():
    """This shows the second form."""
    return render_template('job.html')


@app.route('/third', methods=['POST'])
def third():
    """This shows the third form."""
    form_data = request.form
    all_fields = ''
    all_valus = ''
    for key in form_data.keys():
        all_fields = all_fields + ' ' + str(key)
        all_valus = all_valus + ' ' + str(form_data[key])

    return jsonify({'keys': all_fields, 'values': all_valus})