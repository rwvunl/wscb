import threading
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
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


class Url_Mapping(Base):
    __tablename__ = "url_mapping"
    id = Column(Integer, default=None, nullable=False, autoincrement=True, primary_key=True, unique=True)
    username = Column(String(256), default=None, nullable=False, index=True)
    short_url = Column(String(512), default=None, nullable=False, unique=True)
    long_url = Column(String(512), default=None, nullable=False)


class UrlMappingDao(threading.Thread):
    def __init__(self):
        super(UrlMappingDao, self).__init__()

    @staticmethod
    def get_by_short_url(short_url):
        res = {}
        session = DBSession()
        data = session.query(Url_Mapping).filter(Url_Mapping.short_url == short_url).first()
        if data is not None:
            res = {data.short_url: data.long_url}
        DBSession.remove()
        return res

    @staticmethod
    def get_by_username(username):
        res = {}
        session = DBSession()
        data = session.query(Url_Mapping).filter(Url_Mapping.username == username).all()
        if len(data) > 0:
            for item in data:
                res[item.short_url] = item.long_url
        DBSession.remove()
        return res

    @staticmethod
    def get_max_id():
        session = DBSession
        max_id = session.query(func.max(Url_Mapping.id)).scalar()
        DBSession.remove()
        return max_id

    @staticmethod
    def create_url_mapping(username, short_url, long_url):
        res = {}
        session = DBSession
        new_mapping = Url_Mapping(username=username, short_url=short_url, long_url=long_url)
        try:
            session.add(new_mapping)
            session.commit()
            res = {short_url: long_url}
        except SQLAlchemyError as e:
            session.rollback()
            print(f"error:{e}")
        finally:
            DBSession.remove()
        return res

    @staticmethod
    def update_url_mapping(short_url, new_long_url):
        res = {}
        session = DBSession()
        try:
            nupdate = session.query(Url_Mapping).filter(Url_Mapping.short_url == short_url).update(
                {"long_url": f"{new_long_url}"})
            if nupdate == 1:
                res = {short_url: new_long_url}
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"error:{e}")
        finally:
            DBSession.remove()
        return res

    @staticmethod
    def delete_by_short_url(short_url):
        res = {}
        session = DBSession()
        data = session.query(Url_Mapping).filter(Url_Mapping.short_url == short_url).first()
        if data is not None:
            res[short_url] = data.long_url
            session.delete(data)
            session.commit()
        DBSession.remove()
        return res

    @staticmethod
    def delete_by_username(username):
        res = {}
        session = DBSession()
        data = session.query(Url_Mapping).filter(Url_Mapping.username == username).all()
        if len(data) > 0:
            for item in data:
                res[item.short_url] = item.long_url
                session.delete(item)
            session.commit()
        DBSession.remove()
        return res


if __name__ == '__main__':
    pass
    # #test script
    # Base.metadata.drop_all(engine)  # 删除数据库的表


    # # 添加
    # print(
    #     UrlMappingDao.create_url_mapping(username="Jason", short_url="abc1", long_url="long_url"))  # 添加成功返回new mapping
    # print(
    #     UrlMappingDao.create_url_mapping(username="Jason", short_url="abc2", long_url="long_url"))  # 添加成功返回new mapping
    # print(UrlMappingDao.create_url_mapping(username="Mary", short_url="abc3", long_url="long_url"))  # 添加成功返回new mapping
    # print(
    #     UrlMappingDao.create_url_mapping(username="Mary", short_url="abc555", long_url="long_url"))  # 添加成功返回new mapping
    # print(
    #     UrlMappingDao.create_url_mapping(username="Mary", short_url="abc666", long_url="long_url"))  # 添加成功返回new mapping
    #
    # # 查找存在的shorturl
    # print(UrlMappingDao.get_by_short_url(short_url="abc1"))
    #
    # # 查找不存在的shorturl
    # print(f"查找不存在的shorturl:{UrlMappingDao.get_by_short_url(short_url='abc0')}")
    #
    # print(UrlMappingDao.get_max_id())
    #
    # # 删除不存在的username
    # print(UrlMappingDao.delete_by_username(username="Tom"))
    # # 删除存在的username
    # print(UrlMappingDao.delete_by_username(username="Jason"))
    #
    # # 删除存在的指定映射
    # print(UrlMappingDao.delete_by_short_url(short_url="abc3"))
    # # 删除不存在的指定映射
    # print(UrlMappingDao.delete_by_short_url(short_url="abc0"))
    #
    # # 查看不存在的
    # print(UrlMappingDao.get_by_username(username="Jason"))
    # # 查看存在的
    # print(UrlMappingDao.get_by_username(username="Mary"))
