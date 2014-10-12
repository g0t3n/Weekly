#!/usr/bin/env python
#coding:utf-8
# sqlalchemy orm method copy by:
#  http://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
import os,sys,time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.orm import sessionmaker

from database.baseDB import UsersTable,TasksTable,WeeklyDB
import database.baseDB as basedb
from libs.libs import get_time_as_string
__DEBUG__ = True
BaseDb = declarative_base()

class WeeklySqliteDB(WeeklyDB):
    def __init__(self, db_path='sqlite:///metadata/weekly.db'):
        # self.BaseDb = BaseDb
        # engine = create_engine('sqlite:///metadata/weekly.db')
        # self.engine = engine
        # self.BaseDb.metadata.create_all(engine)
        # self.BaseDb.metadata.bind = engine
        # DBSession = sessionmaker(bind=engine)
        self.session = self.init_databases(db_path)
    def InsertUser(self, uid, username, password, last_login, email):
        tmpUser = UsersTable(uid, username, password, last_login,email)
        self.__Insert__(tmpUser)
        raise NotImplementedError
    def QueryUser(self, withFilter=None):
        self.__Query__(UsersTable, withFilter)
        raise NotImplementedError
    def DelUser(self, tmpUser):
        raise NotImplementedError

    def InsertTask(self, task_owner,  task_text, task_id=None):
        update_time = get_time_as_string()
        # 如果 task_id 存在则更新 update_time 和 tasks_text 否者插入
        query_result = self.QueryTask()
        if task_id and isinstance(task_id, int):
            task_id = int(task_id)
            query_result = query_result.filter(TasksTable.task_id == task_id)
            if __DEBUG__:
                assert query_result.count() < 2
            import IPython;IPython.embed()
            if query_result.count() ==1:
                # exist task and i just update some element
                query_type.update({
                    "task_time" : update_time,
                    "tasks_text" : tasks_text
                    })
                return True
        else:
            # insert new content
            tmpTask = TasksTable(task_owner=task_owner, update_time=update_time, 
                    tasks_text=task_text)
            self.__Insert__(tmpTask)
            return True

    def DelTask(self):
        raise NotImplementedError
    def QueryTask(self, **kargs):
        return self.__Query__(TasksTable)

    def QueryTaskWithEQFilter(self, **kargs):
        # query task as equal filter
        # 'task_owner', 'update_time', 'task_id'
        query_result = self.QueryTask()
        result_list = []
        for (k,v) in kargs.items():
            if k == 'task_id':
                k = TasksTable.task_id
            elif k == 'task_owner':
                k = TasksTable.task_owner
            elif k == 'update_time':
                k = TasksTable.update_time
            query_result = query_result.filter(k==v)
        query_result = query_result.all()
        for item in query_result:
            result_list.append({
                'task_id' : item.task_id,
                'tasks_text' : item.tasks_text,
                'update_time' : item.update_time,
                'task_owner' : item.task_owner
                })
        return result_list


def test_main():
    from random import randrange
    # tmpUser = UsersTable( username=str(randrange(1,3000000)), password='123',
            # last_login=123,)
    # newDb = WeeklySqliteDB()
    # newDb.session.add(tmpUser)
    # newDb.session.commit()

if __name__ == '__main__':
    test_main()
