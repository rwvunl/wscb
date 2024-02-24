from flask import request, jsonify, make_response
import random
import string
import json
from functools import wraps  # used before wrapper function

import app_short
from utils import base62_encode, is_valid_url, get_username_from_jwt, validate_jwt
from app_short.models_short import UrlMappingDao

# shorten_url_service = Blueprint("shorten_url_service", __name__)

def generate_id(username):
    """Generates ID."""
    # Generate random part
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    # Generate incremental part
    data = UrlMappingDao.get_by_short_url(random_part)
    if data:
        increment_part = base62_encode(UrlMappingDao.get_max_id())
        return random_part + increment_part
    return random_part


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            jwt = request.headers['Authorization']
            if jwt is None:
                return jsonify({'error': '403 Forbidden'}), 403
            else:
                if validate_jwt(jwt) is False:
                    return jsonify({'error': '403 Forbidden'}), 403
        else:
            jwt = request.cookies.get('jwt')
            if jwt is None:
                return jsonify({'error': '403 Forbidden'}), 403
            else:
                if validate_jwt(jwt) is False:
                    return jsonify({'error': '403 Forbidden'}), 403
        # old
        # jwt = request.cookies.get("jwt")
        # if jwt is None:
        #     if 'Authorization' in request.headers:
        #         jwt = request.headers['Authorization']
        #         if jwt is None:
        #             return jsonify({'error': '403 Forbidden'}), 403
        #         else:
        #             if validate_jwt(jwt) is False:
        #                 return jsonify({'error': '403 Forbidden'}), 403
        #     else:
        #         return jsonify({'error': '403 Forbidden'}), 403
        # else:
        #     if validate_jwt(jwt) is False:
        #         return jsonify({'error': '403 Forbidden'}), 403
        return func(*args, **kwargs)
    return wrapper

def get_current_user():
    jwt = request.cookies.get("jwt")
    if jwt is not None:
        current_user = get_username_from_jwt(jwt)
    else:
        jwt = request.headers['Authorization']
        current_user = get_username_from_jwt(jwt)
    return current_user

@app_short.route('/', methods=['POST'])
@require_auth
def create_short_url():
    """Creates a new short URL/ID for the given long URL."""
    current_user = get_current_user()
    long_url = request.json.get('value')
    if not long_url:
        return jsonify({'error': '400 Bad request', 'message': 'Long URL is required in the request body'}), 400
    if not is_valid_url(long_url):
        return jsonify({'error': '400 Bad request', 'message': 'Invalid Long URL'}), 400
    id_for_long_url = generate_id(current_user)
    res = UrlMappingDao.create_url_mapping(username=current_user,short_url=id_for_long_url,long_url=long_url)
    if not res:
        return jsonify({'error': 'Fail to create a new mapping. Try again.'}), 500
    # short_url = 'http://127.0.0.1:5000/{id}'.format(id=id)
    return jsonify({'id': id_for_long_url}), 201


@app_short.route('/', methods=['GET'])
@require_auth
def list_urls():
    current_user = get_current_user()
    res = UrlMappingDao.get_by_username(current_user)
    return jsonify(res), 200


@app_short.route('/<id>', methods=['GET'])
@require_auth
def get_long_url(id):
    """Redirect the user to the long URL corresponding to the given ID."""
    res = UrlMappingDao.get_by_short_url(short_url=id)
    if not res:
        return jsonify({'error': 'Given ID is not existed'}), 404
    else:
        return jsonify({'value': res.get(id)}), 301


@app_short.route('/<id>', methods=['PUT'])
@require_auth
def update_long_url(id):
    """Updates the URL behind the given ID."""
    # mysql = json.loads(request.mysql.decode('utf-8'))
    # new_url = mysql.get('url')
    data = json.loads(request.data.decode('utf-8'))
    if data.get("url") is None:
        return jsonify({'error': '400 Bad request', 'message': 'No url field'}), 400
    else:
        new_url = data.get("url")
        if not new_url:
            return jsonify({'error': '400 Bad request', 'message': 'Invalid new url'}), 400
        if not is_valid_url(new_url):
            return jsonify({'error': '400 Bad request', 'message': 'Invalid new url'}), 400
        res = UrlMappingDao.update_url_mapping(short_url=id, new_long_url=new_url)
        if not res:
            return jsonify({'error': '404 Not Found', 'message': 'Given ID is not found'}), 404
        return jsonify({'value': res.get(id)}), 200


@app_short.route('/<id>', methods=['DELETE'])
@require_auth
def delete_url(id):
    """Deletes the given short URL/ID."""
    current_user = get_current_user()
    res = UrlMappingDao.delete_by_short_url(short_url=id)
    if res:
        response = make_response(jsonify({'message': f'{id} has been deleted successfully'}))
        response.headers['Content-Type'] = 'application/json'
        response.status_code = 204
        return response
    else:
        return jsonify({'error': '404 Not Found', 'message': 'Given ID is not found'}), 404



@app_short.route('/', methods=['DELETE'])
@require_auth
def delete_all_urls():
    """Deletes all ID/URL pairs"""
    current_user = get_current_user()
    UrlMappingDao.delete_by_username(username=current_user)
    return jsonify({'message': 'ALL deleted successfully'}), 404
