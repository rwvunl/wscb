from flask import Flask
from shorten_url_service import shorten_url_service
from authentication_service import authentication_service

app = Flask(__name__)

app.register_blueprint(shorten_url_service)
app.register_blueprint(authentication_service,url_prefix='/users')

app.config['SECRET_KEY'] = "this_is_a_secret"


if __name__ == '__main__':
    app.run(Debug=True)

