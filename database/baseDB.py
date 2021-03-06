#!/usr/bin/env python
#coding:utf-8

import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

BaseDb = declarative_base()

#FIXME
# Taskstable.update_time, UsersTable.last_login
# 时间使用字符串 ISO8601 (YYYY-MM-DD) 来保存仅为了兼容 sqlite
# 同时为了简单的时间过滤查询 但这绝对不是个好方法 在大量查询情况下非常影响性能

class UsersTable(BaseDb):
    __tablename__ = 'Users'
    uid = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(450), unique=True, nullable=False)
    password = Column(String(450), nullable=False)
    last_login = Column(Integer,)
    email = Column(String(450), unique=True)


class TasksTable(BaseDb):
    __tablename__ = 'Tasks'
    task_owner = Column(Integer, nullable=False)
    update_time = Column(String, nullable=False)
    tasks_text = Column(String, nullable=False)
    task_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

class WeeklyDB():
    def __init__(self,):
        ''' inheritance to mysql/sqlite '''
        self.BaseDb = BaseDb
        self.session = None     # fill it with sessionmaker()
        return BaseDb


    def init_databases(self, db_uri, debug=False):
        # @db_uri : 'sqlite:///metadata/weekly.db'
        engine = create_engine(db_uri)
        if debug:
            engine.echo = True
        else:
            engine.echo = False
        BaseDb.metadata.create_all(engine)
        BaseDb.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        return DBSession()

    def InsertUser(self, tmpUser):
        raise NotImplementedError
    def DelUser(self, tmpUser):
        raise NotImplementedError
    def QueryUser(self, withFilter=None):
        raise NotImplementedError

    def InsertTask(self):
        raise NotImplementedError
    def DelTask(self):
        raise NotImplementedError
    def QueryTask(self):
        raise NotImplementedError
    def QueryTaskWithFilter(self):
        raise NotImplementedError

    # insert, del, query 通用方法
    def __Insert__(self, obj):
        self.session.add(obj)
        self.session.commit()
        self.session.flush()
    def __Update__(self, obj):
        pass
    def __Del__(self, obj):
        self.session.delete(obj)
        self.session.flush()
    def __Query__(self, query_type):
        query_result = self.session.query(query_type)  #UserTable,TasksTable
        # .get_by(name='John')
        # session.query(Address).filter(Address.person == person).all()
        self.session.flush()
        return query_result


