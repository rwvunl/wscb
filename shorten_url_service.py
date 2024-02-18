from flask import Blueprint, request, jsonify, make_response
import random
import string
import threading
from functools import wraps  # used before wrapper function
from utils import base62_encode, is_valid_url, get_username_from_jwt

shorten_url_service = Blueprint("shorten_url_service", __name__)

db_dict = dict()
global increment
increment = 0
lock = threading.Lock()


def generate_id(username):
    """Generates ID."""
    # Generate random part
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    # Generate incremental part
    if random_part in db_dict[username]:
        increment += 1
        return random_part + base62_encode(increment)
    return random_part


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        jwt = request.cookies.get("jwt")
        if jwt is None:
            return jsonify({'error': '403 Forbidden'}), 403
        request.current_user = get_username_from_jwt(jwt)
        if request.current_user not in db_dict:
            db_dict[request.current_user] = dict()
        return func(*args, **kwargs)

    return wrapper


@shorten_url_service.route('/', methods=['POST'])
@require_auth
def create_short_url():
    """Creates a new short URL/ID for the given long URL."""
    long_url = request.json.get('value')
    if not long_url:
        return jsonify({'error': '400 Bad request', 'message': 'Long URL is required in the request body'}), 400
    if not is_valid_url(long_url):
        return jsonify({'error': '400 Bad request', 'message': 'Invalid Long URL'}), 400
    id_for_long_url = generate_id(request.current_user)
    with lock:
        db_dict[request.current_user][id_for_long_url] = long_url
    # short_url = 'http://127.0.0.1:5000/{id}'.format(id=id)
    return jsonify({'id': id_for_long_url}), 201


@shorten_url_service.route('/', methods=['GET'])
@require_auth
def list_urls():
    return jsonify(db_dict[request.current_user]), 200


@shorten_url_service.route('/<id>', methods=['GET'])
@require_auth
def get_long_url(id):
    """Redirect the user to the long URL corresponding to the given ID."""
    if id not in db_dict[request.current_user]:
        return jsonify({'error': 'Given ID is not existed'}), 404
    with lock:
        long_url = db_dict[request.current_user][id]
    return jsonify({'value': long_url}), 301


@shorten_url_service.route('/<id>', methods=['PUT'])
@require_auth
def update_long_url(id):
    """Updates the URL behind the given ID."""
    # data = json.loads(request.data.decode('utf-8'))
    # new_url = data.get('url')
    data = request.json
    new_url = data.get("value")
    if not new_url:
        return jsonify({'error': '400 Bad request', 'message': 'Invalid new url'}), 400
    if not is_valid_url(new_url):
        return jsonify({'error': '400 Bad request', 'message': 'Invalid new url'}), 400
    if id not in db_dict[request.current_user]:
        return jsonify({'error': '404 Not Found', 'message': 'Given ID is not found'}), 404
    with lock:
        db_dict[request.current_user][id] = new_url
    return jsonify({'value': new_url}), 200


@shorten_url_service.route('/<id>', methods=['DELETE'])
@require_auth
def delete_url(id):
    """Deletes the given short URL/ID."""
    if id not in db_dict[request.current_user]:
        return jsonify({'error': '404 Not Found', 'message': 'Given ID is not found'}), 404
    with lock:
        del db_dict[request.current_user][id]
    response = make_response(jsonify({'message': f'{id} has been deleted successfully'}))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = 204
    return response


@shorten_url_service.route('/', methods=['DELETE'])
@require_auth
def delete_all_urls():
    """Deletes all ID/URL pairs"""
    with lock:
        db_dict[request.current_user].clear()
    return jsonify({'message': 'ALL deleted successfully'}), 404
