from flask import Flask, request, jsonify
import random
import string
import json
import threading
from utils import base62_encode, is_valid_url

app = Flask(__name__)

id_url_mapping = dict()

global increment
increment = 0

lock = threading.Lock()

def generate_id():
    """Generates ID."""
    # Generate random part
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    # Generate incremental part
    if random_part in id_url_mapping.keys():
        increment += 1
        return random_part + base62_encode(increment)
    return random_part


@app.route('/', methods=['POST'])
def create_short_url():
    """Creates a new short URL/ID for the given long URL."""
    long_url = request.json.get('value')
    if not long_url:
        return jsonify({'error': 'Long URL is required in the request body'}), 400
    if not is_valid_url(long_url):
        return jsonify({'error': 'Invalid URL format'}), 400
    with lock:
        id = generate_id()
        id_url_mapping[id] = long_url
    # short_url = 'http://127.0.0.1:5000/{id}'.format(id=id)
    return jsonify({'id': id}), 201

@app.route('/', methods=['GET'])
def list_urls():
    return jsonify(id_url_mapping), 200

@app.route('/<id>', methods=['GET'])
def redirect_to_long_url(id):
    """Redirect the user to the long URL corresponding to the given ID."""
    try:
        with lock:
            long_url = id_url_mapping[id]
        return jsonify({'value': long_url}), 301
    except KeyError:
        return jsonify({'error': 'Short URL not found'}), 404


@app.route('/<id>', methods=['PUT'])
def update_long_url(id):
    """Updates the URL behind the given ID."""
    print(request.data)
    data = json.loads(request.data.decode('utf-8'))
    new_url = data.get('url')
    if not new_url:
        return jsonify({'error': 'New URL is required in the request body'}), 400
    if id not in id_url_mapping.keys():
        return jsonify({'error': 'Given ID is not existed'}), 404
    if not is_valid_url(new_url):
        return jsonify({'error': 'Invalid URL format'}), 400
    # Update the URL behind the given ID
    with lock:
        id_url_mapping[id] = new_url
    return jsonify({'value': new_url}), 200


@app.route('/<id>', methods=['DELETE'])
def delete_url(id):
    """Deletes the given short URL/ID."""
    if id not in id_url_mapping.keys():
        return jsonify({'error': 'Short URL not found'}), 404
    # Delete the short URL/ID
    with lock:
        del id_url_mapping[id]
    return '', 204


@app.route('/', methods=['DELETE'])
def delete_all_urls():
    """Deletes all ID/URL pairs"""
    with lock:
        id_url_mapping.clear()
    return jsonify({'message': 'All ID/URL pairs have been deleted'}), 404


if __name__ == '__main__':
    app.run(debug=True)

