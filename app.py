from flask import Flask, request, jsonify, redirect
import random
import string
import json
import re
app = Flask(__name__)  # 用于存储URL映射关系的字典
url_id_mapping = dict()
id_url_mapping = dict()

def generate_id():
    """Generates ID."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))  # Generating a 6-character long ID

def is_valid_url(url):
    """Check if the provided URL is valid."""
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

@app.route('/', methods=['POST'])
def create_short_url():
    """Creates a new short URL/ID for the given long URL."""
    long_url = request.json.get('value')
    if not long_url:
        return jsonify({'error': 'Long URL is required in the request body'}), 400

    if not is_valid_url(long_url):
        return jsonify({'error': 'Invalid URL format'}), 400

    id = generate_id()

    url_id_mapping[long_url] = id
    id_url_mapping[id] = long_url

    short_url = 'http://127.0.0.1:5000/{id}'.format(id=id)
    return jsonify({'id': id}), 201


@app.route('/', methods=['GET'])
def list_urls():
    """Returns a list of all keys (IDs) or all long URLs."""
    all_keys = list(url_id_mapping.keys())
    all_urls = list(url_id_mapping.values())
    return jsonify({'keys': all_keys, 'urls': all_urls}), 200


@app.route('/<id>', methods=['GET'])
def redirect_to_long_url(id):
    """Redirect the user to the long URL corresponding to the given ID."""
    try:
        long_url = id_url_mapping[id]
        return redirect(long_url, code=301)
    except KeyError:
        return jsonify({'error': 'Short URL not found'}), 404


@app.route('/<id>', methods=['PUT'])
def update_long_url(id):
    """Updates the URL behind the given ID."""
    new_url = json.loads(request.data.decode('utf-8')).get('url')
    try:
        if not new_url:
            return jsonify({'error': 'New URL is required in the request body'}), 400

        if id not in id_url_mapping.keys():
            return '', 404

        # Update the URL behind the given ID
        url_id_mapping[new_url] = id
        id_url_mapping[id] = new_url
        return jsonify({'message': 'URL updated successfully'}), 200
    except Exception as e:
        print(f'err:{e},new_url:{new_url}')


@app.route('/<id>', methods=['DELETE'])
def delete_url(id):
    """Deletes the given short URL/ID."""
    if id not in id_url_mapping.keys():
        return jsonify({'error': 'Short URL not found'}), 404

    # Delete the short URL/ID
    del url_id_mapping[id_url_mapping[id]]
    del id_url_mapping[id]
    return '', 204


@app.route('/', methods=['DELETE'])
def delete_all_urls():
    """Deletes all ID/URL pairs"""
    url_id_mapping.clear()
    id_url_mapping.clear()
    return jsonify({'message': 'All ID/URL pairs have been deleted'}), 404


if __name__ == '__main__':
    app.run(debug=True)

