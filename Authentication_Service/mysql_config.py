import os
class BaseConfig(object):

    # 数据库的配置
    DIALCT = 'mysql'
    DRITVER = 'pymysql'
    HOST = 'mysql-db' # 0.0.0.0
    PORT = '3306'
    USERNAME = os.environ.get('DB_USERNAME')
    PASSWORD = os.environ.get('DB_PASSWORD')
    DBNAME = 'wscb_db'

    SQLALCHEMY_DATABASE_URI = f'{DIALCT}+{DRITVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True