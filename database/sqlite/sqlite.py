#!/usr/bin/env python
#coding:utf-8
# sqlalchemy orm method copy by:
#  http://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
import os,sys,time,hashlib


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.orm import sessionmaker

from database.baseDB import UsersTable,TasksTable,WeeklyDB,PrivilegeTable,PrivilegeToUserTable
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

    def SubmitUserInfo(self, User_Name, User_Pwd, User_Email, User_Level, User_ID=None):
        # 如果 User_id 存在则更新 否者插入
        query_result = self.QueryTask()
        User_ID = int(User_ID)
        import pdb;pdb.set_trace()
        if User_ID and isinstance(User_ID, int):
            query_result = query_result.filter(UsersTable.User_ID == User_ID)
            if query_result.count() ==1:
                query_result.update({
                    "User_Name": User_Name,
                    "User_Pwd": User_Pwd,
                    "User_Email": User_Email,
                    "User_Level": User_Level
                    })
                self.session.commit()
                return True
        else:
            # insert new content
            tmpUser = UsersTable(User_Name=User_Name, User_Pwd=User_Pwd,
                                 User_Email=User_Email,User_Level=User_Level)
            self.__Insert__(tmpUser)
            return True
    def QueryAllUserList(self, withFilter=None):
        query_result = self.__Query__(UsersTable)
        result_list=[]
        for item in query_result:
            result_list.append({
                'User_ID' : item.User_ID,
                'User_Name' : item.User_Name,
                'User_Email' : item.User_Email,
                'User_Level' : item.User_Level,
                'User_Lastlogin' : item.User_Lastlogin,
                })
        return result_list
    def QueryUserWithEQFilter(self, **kargs):
        query_result = self.QueryUser()
        result_list = []
        for (k,v) in kargs.items():
            if k == 'User_ID':
                k = UsersTable.User_ID
            elif k == 'User_Name':
                k = UsersTable.User_Name
            elif k == 'User_Pwd':
                k = UsersTable.User_Pwd
            query_result = query_result.filter(k==v)
        query_result = query_result.all()
        for item in query_result:
            result_list.append({
                'User_ID' : item.User_ID,
                'User_Name' : item.User_Name,
                'User_Email' : item.User_Email,
                'User_Level' : item.User_Level,
                'User_Lastlogin' : item.User_Lastlogin,
                })
        return result_list
    def DelUser(self, UserID):
        try:
            tempUser=self.QueryUser().filter(UsersTable.User_ID == UserID)
            self.__Del__(tempUser)
            return 1
        except Exception as err:
            return 0
    def ResetPwd(self,UserID):
        try:
            tempUser=self.QueryUser().filter(UsersTable.User_ID == UserID)
            User_Pwd=hashlib.sha512("123456").hexdigest().upper()
            tempUser.update(
                {
                    'User_Pwd' : User_Pwd
                }
            )
            self.session.commit()
            return 1
        except Exception as err:
            return 0
    def QueryUser(self, **kargs):
        return self.__Query__(UsersTable)
    def InsertTask(self, task_owner, task_text,task_id=None):
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

    def GetMenu(self):
        query_result = self.__Query__(PrivilegeTable)
        result_list=[]
        for item in query_result:
            result_list.append({
                'Privilege_ID' : item.Privilege_ID,
                'Privilege_Name' : item.Privilege_Name,
                'Privilege_Action' : item.Privilege_Action,
                'Privilege_Parent' : item.Privilege_Parent,
                'Privilege_Handler' : item.Privilege_Handler,
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
