#!/usr/bin/env python
#coding:utf-8

import os
import pdb
import hashlib
import string
from urllib import unquote
from json import dumps as jsondumps

import tornado.ioloop
import tornado.web

from libs.libs import get_time_as_string

__DEBUG__ = True
if __DEBUG__:
    from json import dumps as jsondumps
webui_config = {
        'WeeklyDb' : None,
        # ''
        }


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("User_ID")
    def CheckPrivilege(self,Handler):
        return ""
    def get(self):
        self.write_error(404)
    def post(self):
        self.write_error(404)
    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html')
        else:
            self.write('error:' + str(status_code))


class MainHandler(tornado.web.RequestHandler):
    #@tornado.web.authenticated
    def get(self):
        MenuList = webui_config['WeeklyDb'].GetMenu()
        UserName = self.get_secure_cookie("UName")
        self.render('index.html', title= 'Weekly ~~', MenuList = MenuList , UserName = UserName)
    def post(self):
        pass

class AddTask(tornado.web.RequestHandler):
    def post(self):
        taskcontent = self.get_argument('taskcontent', None)
        uid = self.get_argument('uid', 53)
        if __DEBUG__:
            assert taskcontent is not None
            assert isinstance(taskcontent, unicode)
            assert uid is not None
            assert isinstance(uid, int)
        task_id = self.get_argument('taskId', None)
        if webui_config['WeeklyDb'].InsertTask(uid, taskcontent, task_id):
            self.write("'success':'done'")
        else:
            self.write("'error' : 'some thing happend.. WTF'")
''' old function
class ControlUnit(tornado.web.RequestHandler):
    def get(self):
        action = self.get_argument("action", None)
        if not action:
            self.render('ContentUnit/default.html', display_unit = 'default')
        elif action == 'ViewTask':
            fromDate = self.get_argument("fromDate", None)
            task_owner = self.get_argument("taskOwn", 53)
            if not fromDate:
                fromDate = get_time_as_string()
            display_content = webui_config['WeeklyDb'].QueryTaskWithEQFilter(update_time=fromDate,
                    task_owner=task_owner)
            result = ""
            for i in display_content:
                result += jsondumps(i, indent=4) +"\n"
            self.render('ContentUnit/ViewTask.html', display_uint = 'ViewTask',
                   TaskContent=result )
        elif action == 'AddTask':
            self.render('ContentUnit/AddTask.html', display_uint = 'AddTask', 
                    taskContent="default")
'''
class LoginHandler(tornado.web.RequestHandler):
      def get(self):
          self.render('ContentUnit/Login.html',display_uint='Login')
      def post(self):
          User_Name = self.get_argument("User_Name")
          User_Pwd = self.get_argument("User_Pwd")
          if(len(User_Pwd) & len(User_Pwd)):
              User_Pwd = hashlib.sha512(User_Pwd).hexdigest().upper()
              UserModel = webui_config['WeeklyDb'].QueryUserWithEQFilter(User_Name=User_Name,User_Pwd=User_Pwd)
              if(len(UserModel)):
                  self.write("<script>alert('Success!')</script>")
                  self.set_secure_cookie("UName", UserModel[0]["User_Name"],expires_days=1)
                  self.set_secure_cookie("UID", str(UserModel[0]["User_ID"]),expires_days=1)
                  self.redirect("/index")
              else:
                  self.write("<script>alert('Pwd Wrong!')</script>")
          else:
              self.write("<script>Everyone know that pwd&username can't be null</script>")
class UserHandler(tornado.web.RequestHandler):
    def get(self):
        def GetAllUserList():
            user_list= webui_config['WeeklyDb'].QueryAllUserList()
            result = "["
            for i in user_list:
                result += jsondumps(i, indent=4)+","
            result = result[:-1] + "]"
            self.write(result)
        def GetUserInfo():
            UserID=int(self.get_argument("UserID", None))
            if UserID and isinstance(UserID, int):
                UserModel = webui_config['WeeklyDb'].QueryUserWithEQFilter(User_ID=UserID)
            result=jsondumps(UserModel)
            self.write(result)
        def DelUser():
            UserID=int(self.get_argument("UserID", None))
            if UserID and isinstance(UserID, int):
                if webui_config['WeeklyDb'].DelUser(UserID) > 0:
                    self.write('{"success":true,"msg":"Delete success"}')
                else:
                    self.write('{"wrong":true,"msg":"Something wrong"}')
            else:
                self.write('{"success":true,"msg":"UserID is wrong"}')
        def ResetPwd():
            UserID=int(self.get_argument("UserID", None))
            if UserID and isinstance(UserID, int):
                if webui_config['WeeklyDb'].ResetPwd(UserID) > 0:
                   self.write('{"success":true,"msg":"Reset success"}')
                else:
                    self.write('{"wrong":true,"msg":"Reset wrong"}')
            else:
                 self.write('{"success":true,"msg":"UserID is wrong"}')

        action = self.get_argument("action", None)
        todo = {
            "GetAllUserList":GetAllUserList,
            "GetUserInfo":GetUserInfo,
            "DelUser":DelUser,
            "ResetPwd":ResetPwd,
            }
        todo.get(action)()
    def post(self):
        User_Name = self.get_argument("User_Name")
        User_Pwd = self.get_argument("User_Pwd")
        User_Email = self.get_argument("User_Email")
        User_Level = self.get_argument("User_Level")
        if(len(self.get_argument("User_ID"))>0):
            User_ID=self.get_argument("User_ID")
        else:
            User_ID=0
        if webui_config['WeeklyDb'].SubmitUserInfo(User_Name, hashlib.sha512(User_Pwd).hexdigest().upper(), User_Email, User_Level,User_ID):
            self.write("<script>alert('success!');parent.$.colorbox.close();parent.getUserList()</script>")
        else:
            self.write("<script>alert('erorr!');parent.$.colorbox.close()</script>")

class PrivilegeHandler(tornado.web.RequestHandler):
    def get(self):
        def GetPrivilege():
            UserID=int(self.get_argument("UserID", None))
            privilege_list = webui_config['WeeklyDb'].QueryUserPrivilege(UserID)
            result = ""
            for i in privilege_list:
                result += str(i["Privilege_PID"]) + ","
            result = result[:-1]
            self.write(result)
        action = self.get_argument("action", None)
        todo = {
            "GetPrivilege":GetPrivilege
            }
        todo.get(action)()

    def post(self):
        def UpdatePrivilege():
            UserID=int(self.get_argument("UserID", None))
        action = self.get_argument("action", None)
        todo = {
            "UpdatePrivilege":UpdatePrivilege
            }
        todo.get(action)()

class ControlUnit(tornado.web.RequestHandler):
    def get(self):
        def ViewTask():
            fromDate = self.get_argument("fromDate", None)
            task_owner = self.get_argument("taskOwn", 53)
            if not fromDate:
                fromDate = get_time_as_string()
            display_content = webui_config['WeeklyDb'].QueryTaskWithEQFilter(update_time=fromDate,
                    task_owner=task_owner)
            result = ""
            for i in display_content:
                result += jsondumps(i, indent=4) +"\n"
            self.render('ContentUnit/ViewTask.html', display_uint = 'ViewTask',
                   TaskContent=result )
        def AddTask():
            self.render('ContentUnit/AddTask.html', display_uint = 'AddTask',
                    taskContent="default")
        def UserManage():
            MenuList = webui_config['WeeklyDb'].GetMenu()
            self.render('UserManage/UserManage.html', display_uint = 'UserManage',
                    taskContent="default",MenuList = MenuList)
        def AddUser():
            self.render('UserManage/AddUser.html', display_uint = 'AddUser',
                    taskContent="default")
        def Logout():
            self.clear_all_cookies()
            self.redirect("/Login")
        action = self.get_argument("action", None)
        todo = {
            "UserManage": UserManage,
            "AddTask": AddTask,
            "ViewTask": ViewTask,
            "AddUser": AddUser,
            "Logout":Logout
            }
        if not action:
            self.render('ContentUnit/default.html', display_unit = 'default')
        else:
            todo.get(action)()

settings = {
        "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        # "xsrf_cookies": True,
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path':  os.path.join(os.path.dirname(__file__), 'static'),
        "login_url": "/Login",
        }

application = tornado.web.Application([
    (r"/", MainHandler),
    # (r"/login", LoginHandler),
    (r"/index*", MainHandler),
    (r"/AddTask/*", AddTask),
    (r"/ViewContentUnit/*", ControlUnit),
    (r"/UserHandler/*", UserHandler),
    (r"/Login/*", LoginHandler),
    (r"/PrivilegeHandler/*", PrivilegeHandler),
    (r".*", BaseHandler),
    ], **settings)

def main(**kargs):
    webui_config.update(kargs)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
