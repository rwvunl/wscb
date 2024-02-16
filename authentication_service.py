from flask import current_app,Blueprint, request, jsonify, make_response
from utils import get_hash, generate_jwt, is_input_password_correct, validate_password_format
from functools import wraps
import secrets

authentication_service = Blueprint("authentication_service", __name__)

users = {}  # {username:password}
users_salt = {}  # {username:salt}


def validate_password(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.json
        if not data:
            return jsonify({'error': 'Bad request'}), 400
        username = data.get('username')
        input_password = get_hash(data.get('password'),users_salt[username])
        try:
            is_correct = is_input_password_correct(password=users[username], input_password=input_password,
                                             salt=users_salt[username])
        except KeyError:
            return jsonify({'error': 'Username doesn\'t exist'}), 400
        if is_correct is False:
            return jsonify({'error': 'Input password is wrong'}), 400
        return func(*args, **kwargs)
    return wrapper


@authentication_service.route('/', methods=['POST'])
def create_user():
    data = request.json
    if not data:
        return jsonify({'error': 'Bad request'}), 400
    username = data.get('username')
    password = data.get('password')
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400
    is_validated = validate_password_format(password)
    if is_validated is False:
        return jsonify({'error': 'Invalid Password: Minimum of 8 characters, consisting only of letters and numbers'}), 400
    salt = secrets.token_hex(16)  # salt length == 16
    users_salt[username] = salt
    users[username] = get_hash(password, salt)
    return jsonify({'message': 'User created successfully'}), 201


@authentication_service.route('/', methods=['PUT'])
@validate_password
def update_password():
    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')
    is_validated = validate_password_format(new_password)
    if is_validated is False:
        return jsonify({'error': 'Invalid New Password: Minimum of 8 characters, consisting only of letters and numbers'}), 400
    users[username] = get_hash(password=new_password, salt=users_salt[username])
    return jsonify({'message': 'Password updated successfully'}), 200


@authentication_service.route('/login', methods=['POST'])
@validate_password
def login():
    data = request.json
    username = data.get('username')
    jwt = generate_jwt(payload={'username': username},key=current_app.config['SECRET_KEY'])
    try:
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('jwt', jwt, max_age=3600)
        return response, 200
    except Exception as e:
        return jsonify({'error': 'Something went wrong while login', 'message': str(e)}), 500


@authentication_service.route('/logout', methods=['GET'])
def logout():
    jwt = request.cookies.get('jwt')
    if jwt is None:
        return jsonify({'error': 'You are not logged in'}), 401
    response = jsonify({'message': 'Logout successful'})
    try:
        response.delete_cookie('jwt')
        # response.set_cookie('jwt',expires=0) 也可以用这个
    except Exception as e:
        return jsonify({'error': 'Something went wrong while logout', 'message': str(e)}), 500
    return response, 200
