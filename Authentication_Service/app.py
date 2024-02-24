from flask import Flask, request, jsonify, make_response
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from mysql_config import BaseConfig
from utils import get_hash, generate_jwt, is_input_password_correct
from functools import wraps  # used before wrapper function
import secrets  # to generate a good salt value for each user when storing password
from models import UserDao

app = Flask(__name__)

app.config['SECRET_KEY'] = "this_is_a_secret"
app.config.from_object(BaseConfig)

Base = declarative_base()

# 创建一个带连接池的引擎，引擎是与特定数据库的连接
engine = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI,
                       max_overflow=15,  # 超过连接池大小外最多创建的连接
                       pool_size=10,  # 连接池大小
                       pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
                       pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
                       )
Base.metadata.create_all(engine)  # 通过基类与数据库进行交互创建表结构，此时表内还没有数据

def validate_username_and_password(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.json
        if not data:
            return jsonify({'error': '400 Bad request'}), 400
        username = data.get('username')
        # jwt = request.cookies.get('jwt')
        # if jwt is not None:
        #     if get_username_from_jwt(jwt) != username:
        #         return jsonify({'detail': 'forbidden'}), 403
        # else:
        #     jwt = request.headers['jwt']
        #     if jwt is not None:
        #         if get_username_from_jwt(jwt) != username:
        #             return jsonify({'detail': 'forbidden'}), 403
        res = UserDao.get_user_by_username(username=username)
        if not res:
            return jsonify({'detail': 'forbidden','message':'Username not found'}), 403
        salt = res.get('salt')
        password = res.get('password')
        input_password = get_hash(password=data.get('password'), salt=salt)
        is_correct = is_input_password_correct(password=password, input_password=input_password, salt=salt)
        if is_correct is False:
            return jsonify({'detail': 'forbidden'}), 403
        return func(*args, **kwargs)

    return wrapper


@app.route('/', methods=['POST'])
def create_user():
    data = request.json
    if not data:
        return jsonify({'error': '400 Bad request'}), 400
    username = data.get('username')
    password = data.get('password')
    res = UserDao.get_user_by_username(username=username)
    if res:
        return jsonify({'detail': 'duplicate', 'message': 'Username already exists'}), 409
    # is_validated = validate_password_format(password)
    # if is_validated is False:
    #     return jsonify({'error': '400 Bad request', 'message': 'Invalid Password: Minimum of 8 characters, consisting only of letters and numbers'}), 400
    salt = secrets.token_hex(16)  # salt length == 16
    res = UserDao.create_user(username=username,password=get_hash(password, salt),salt=salt)
    if not res:
        return jsonify({'error':'Fail to create user. Try again.'}), 500
    else:
        return jsonify({'message': f"User {res.get('username')} created successfully"}), 201


@app.route('/', methods=['PUT'])
@validate_username_and_password
def update_password():
    # jwt = request.cookies.get('jwt')
    # if jwt is None:
    #     return jsonify({'error': '403 Forbidden'}), 403
    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')
    # is_validated = validate_password_format(new_password)
    # if is_validated is False:
    #     return jsonify({'error': '400 Bad request', 'message': 'Invalid Password: Minimum of 8 characters, consisting only of letters and numbers'}), 400
    user = UserDao.get_user_by_username(username=username) # get salt
    res = UserDao.update_password(username=username,new_password=get_hash(password=new_password, salt=user.get('salt')))
    if not res:
        return jsonify({'error': 'Fail to update password. Try again.'}), 500
    return jsonify({'message': 'Password updated successfully'}), 200


@app.route('/login', methods=['POST'])
@validate_username_and_password
def login():
    data = request.json
    username = data.get('username')
    jwt = generate_jwt(payload={'username': username}, key=app.config['SECRET_KEY'])
    try:
        response = make_response(jsonify({'message': 'Login successful','token':jwt}))
        response.delete_cookie('jwt')
        response.set_cookie('jwt', jwt, path='/')  # set JWT lifetime == 3600 seconds
    except Exception as e:
        return jsonify({'error': '500 Something went wrong while login', 'message': str(e)}), 500
    return response, 200

@app.route('/logout', methods=['GET'])
def logout():
    jwt = request.cookies.get('jwt')
    if jwt is None:
        return jsonify({'error': '401 Unauthorized', 'message': 'You are not logged in'}), 401
    response = jsonify({'message': 'Logout successfully'})
    try:
        # response.set_cookie('jwt', jwt, expires=0)
        response.delete_cookie('jwt')
    except Exception as e:
        return jsonify({'error': '500 Something went wrong while logout', 'message': str(e)}), 500
    return response, 200



if __name__ == '__main__':
    app.run(Debug=True, host='0.0.0.0', port=5002)