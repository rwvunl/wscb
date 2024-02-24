import threading
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session  # 线程安全
from sqlalchemy import create_engine
from mysql_config import BaseConfig
Base = declarative_base()

# 创建一个带连接池的引擎，引擎是与特定数据库的连接
engine = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI,
                       max_overflow=15,  # 超过连接池大小外最多创建的连接
                       pool_size=10,  # 连接池大小
                       pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
                       pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
                       )

# 多线程利用数据库连接池创建session
session_factory = sessionmaker(bind=engine)
DBSession = scoped_session(session_factory)


class User(Base):
    __tablename__ = "user"
    username = Column(String(256), default=None, nullable=False, primary_key=True, index=True, unique=True)
    userpassword = Column(String(512), default=None, nullable=False)
    usersalt = Column(String(32), default=None, nullable=False)


class UserDao(threading.Thread):

    def __init__(self):
        super(UserDao, self).__init__()

    @staticmethod
    def create_user(username, password, salt):
        res = {}
        session = DBSession()  # 每个线程都可以直接使用定义的Session
        new_user = User(username=username, userpassword=password, usersalt=salt)
        try:
            session.add(new_user)
            session.commit()
            res = {'username':new_user.username,
                   'password':new_user.userpassword,
                   'salt':new_user.usersalt,}
        except SQLAlchemyError as e:
            session.rollback()
            print(f"error:{e}")
        finally:
            DBSession.remove()
        return res

    @staticmethod
    def get_user_by_username(username):
        res = {}
        session = DBSession()
        data = session.query(User).filter(User.username == username).first()
        if data is not None:
            res = {'username': data.username,
                   'password': data.userpassword,
                   'salt': data.usersalt}
        DBSession.remove()
        return res

    @staticmethod
    def update_password(username, new_password):
        res = {}
        session = DBSession()
        try:
            result_user = session.query(User).filter(User.username == username).update(
                {"userpassword": f"{new_password}"})
            res = {'username':username}
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"error:{e}")
        finally:
            DBSession.remove()
        return res


if __name__ == '__main__':
    # pass
    # #test script
    Base.metadata.drop_all(engine)  # 删除数据库的表
    Base.metadata.create_all(engine)  # 通过基类与数据库进行交互创建表结构，此时表内还没有数据
    # 开10个线程测试多线程
    arr = []
    for i in range(10):
        arr.append(UserDao())
    for i in arr:
        i.start()
        i.create_user(username=f"user{str(i)}", password='1234', salt='salt')
        i.join()

    # 添加
    print(UserDao.create_user(username="Jason", password="12345678910", salt="salt"))  # 添加成功返回User
    print(UserDao.create_user(username="Alex", password="12345678910", salt="salt"))  # 添加成功返回User
    print(UserDao.create_user(username="Billy", password="12345678910", salt="salt"))  # 添加成功返回User

    print(f'重复添加：{UserDao.create_user(username="Jason", password="12345678910", salt="salt")}')  # 添加不成功，返回None

    print(f'按条件查询：{UserDao.get_user_by_username(username="Mary")}')  # 不存在的用户，返回None

    print(f'按条件查询：{UserDao.get_user_by_username(username="Jason")}')  # 不存在的用户，返回None

    # 修改密码
    result = UserDao.update_password(username="Jason", new_password="abcdefgh")  # 成功则返回True
    print(result)

    # 按条件查询
    print(UserDao.get_user_by_username(username="Jason"))  # 新密码abcdefgh