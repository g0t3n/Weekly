#!/usr/bin/env python
#coding:utf-8

import os
import pdb
import hashlib
import string
from urllib import unquote
from json import dumps as jsondumps
import time
import datetime
import tornado.ioloop
import tornado.web
import copy
import tempfile
import logging
from PIL import Image
from tornado.httpserver import HTTPServer
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
        return self.get_secure_cookie("UID")
    def CheckPrivilege(self,Handler):
        PrivilegeList = webui_config['WeeklyDb'].QueryUserPrivilegeList(self.current_user)
        HasPrivileg = False
        for Privilege in PrivilegeList:
            if(Handler in Privilege["Privilege_ControlAction"]):
                HasPrivileg = True
                break
        return HasPrivileg
    def GetUserLevel(self):
        Users=webui_config['WeeklyDb'].QueryUserWithEQFilter(User_ID=self.get_current_user())
        if len(Users)>0:
            return Users[0]["User_Level"]
        else:
            return 100
    def get(self):
        self.write_error(404)
    def post(self):
        self.write_error(404)
    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html')
        else:
            self.write('error:' + str(status_code))

# def CheckPrivilege(cls,Handler):
#         def handle_func(func):
#             if(cls.get_secure_cookie("User_ID")==""):
#                 pdb.set_trace()
#                 cls.redirect("/Login")
#             return func()
#         return handle_func

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        UserName = self.get_secure_cookie("UName")
        UserID = int(self.get_secure_cookie("UID"))
        MenuList = webui_config['WeeklyDb'].GetMenu()
        AllList = copy.deepcopy(MenuList)
        PrivilegeList = webui_config['WeeklyDb'].QueryUserPrivilege(UserID).split(",")
        for Menu in AllList:
            if Menu["Privilege_Parent"]!=0 and PrivilegeList.count(str(Menu["Privilege_ID"]))==0:
                MenuList.remove(Menu)
        self.render('index.html', title= 'Weekly ~~', MenuList = MenuList , UserName = UserName)
    @tornado.web.authenticated
    def post(self):
        pass

class AddTask(BaseHandler):
    @tornado.web.authenticated
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
class LoginHandler(BaseHandler):
    def get(self):
        def Login():
             self.render('ContentUnit/Login.html',display_uint='Login')
        def Logout():
            self.clear_all_cookies()
            self.redirect("/Login/")
        action = self.get_argument("action", "Login")
        todo = {
            "Login": Login,
            "Logout":Logout,
        }
        todo.get(action)()
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
             self.write("<script>Everyone know that pwd&username can't be null</script>")

class UserHandler(BaseHandler):
    @tornado.web.authenticated
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
        if(self.CheckPrivilege("UserManage")):
           todo.get(action)()
    @tornado.web.authenticated
    def post(self):
        if(self.CheckPrivilege("UserManage")):
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

class DailyHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        def GetDaily():
            UserID = int(self.get_argument("UserID", None))
            if int(self.GetUserLevel()) > 2:
                UserID = self.get_current_user()
            Start = self.get_argument("Start","")
            End = self.get_argument("End","")
            Page = int(self.get_argument("Page","1"))
            Rows = 4
            DailyList = webui_config['WeeklyDb'].QueryDailyByUserAndDate(UserID,Start,End)
            if len(DailyList)>0:
                result = '{"page":'+ str(Page)
                result += ',"count":'+str(len(DailyList))
                result += ',"rows":'+str(Rows)
                result += ',"data":['
                for i in DailyList[(Page-1)*Rows:(Page)*Rows]:
                    result += jsondumps(i, indent=4)+","
                result = result[:-1] + "]}"
                self.write(result)
            else:
                self.write('{"page":0,"count":0}')
        action = self.get_argument("action", None)
        todo = {
            "GetDaily":GetDaily
            }
        todo.get(action)()
    @tornado.web.authenticated
    def post(self):
        DailyContent = tornado.escape.xhtml_escape(self.get_argument('DailyContent', None))
        DailyQuestion = tornado.escape.xhtml_escape(self.get_argument('DailyQuestion', None))
        now = datetime.datetime.now()
        DailyDate = now.strftime('%Y-%m-%d')
        uid = self.current_user
        TodayDaily=webui_config['WeeklyDb'].QueryDailyByUserAndDate(uid,DailyDate,DailyDate)
        if(len(TodayDaily)>0):
            DailyID = TodayDaily[0]["Daily_ID"]
            if webui_config['WeeklyDb'].UpdateDaily(DailyContent,DailyQuestion,DailyID):
                self.write("'success':'done'")
            else:
                self.write("'error' : 'some thing happend.. WTF'")
        else:
            if webui_config['WeeklyDb'].AddDaily(DailyContent,DailyQuestion,DailyDate,uid):
                self.write("'success':'done'")
            else:
                self.write("'error' : 'some thing happend.. WTF'")


class PrivilegeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        def GetPrivilege():
            UserID=int(self.get_argument("UserID", None))
            result = webui_config['WeeklyDb'].QueryUserPrivilege(UserID)
            self.write(result)
        action = self.get_argument("action", None)
        todo = {
            "GetPrivilege":GetPrivilege
            }
        todo.get(action)()
    @tornado.web.authenticated
    def post(self):
        def SubmitPrivilege():
            UserID=int(self.get_argument("UserID", None))
            PrivilegeList=self.get_arguments("privileges")
            Privilege=",".join(PrivilegeList)
            if(webui_config['WeeklyDb'].UpdateUserPrivilege(UserID,Privilege)):
                self.write('{"success":true,"msg":"Update success"}')
        action = self.get_argument("action", None)
        todo = {
            "SubmitPrivilege":SubmitPrivilege
            }
        todo.get(action)()

### 个人信息
class PersonalHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        if(self.CheckPrivilege("Personal")):
            User_Name = self.get_argument("User_Name")
            User_Pwd = self.get_argument("User_Pwd")
            User_Email = self.get_argument("User_Email")
            User_ID=int(self.get_current_user())
            if webui_config['WeeklyDb'].SubmitPersonalInfo(User_Name, hashlib.sha512(User_Pwd).hexdigest().upper(), User_Email,User_ID):
                self.write("<script>alert('success!'); self.location='/ViewContentUnit/?action=Personal'</script>")
            else:
                self.write("<script>alert('something wrong!'); self.location='/ViewContentUnit/?action=Personal'</script>")
class UploadHandler(BaseHandler):
      @tornado.web.authenticated
      def post(self):
         def UploadImage():
             if self.request.files["imgFile"]:
                image_type_list = ['image/gif', 'image/jpeg','image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
                Img = self.request.files['imgFile'][0]
                if Img['content_type'] not in image_type_list:
                    #类型错误
                    self.write("{\"error\" : 1,\"message\" : \"图片类型错误\"}")
                    return
                if len(Img['body']) > 2 * 1024 * 1024:
                    #太大了
                    self.write("{\"error\" : 1,\"message\" : \"图片太大了\"}")
                    return
                tmp_file = tempfile.NamedTemporaryFile(delete=False)
                tmp_file.write(Img['body'])
                tmp_file.seek(0)
                try:
                    image_one = Image.open(tmp_file.name)
                except IOError, error:
                    logging.info(error)   # 进行日志记录。
                    logging.info('+'*30 + '\n')
                    logging.info(self.request.headers)
                    tmp_file.close()
                    os.remove(tmp_file.name)
                    #图片不合法！
                    self.write("{\"error\" : 1,\"message\" : \"图片不合法\"}")
                    return

                # 判断图片尺寸，不在尺寸内拒绝操作
                if image_one.size[0] > 2000 or image_one.size[1] > 2000:
                      tmp_file.close()
                      os.remove(tmp_file.name)
                      self.write('{\"error\" : 1,\"message\" : \"图片太大了\"}')
                      return

                # 进行存储。
                # 指定存储目录，产生新的文件名。
                image_path = self.get_template_path()+("/../static/upload/")
                image_format = Img['filename'].split('.').pop().lower()
                tmp_name = image_path + str(int(time.time()))+ "." + image_format
                op_path= ("/../static/upload/") + str(int(time.time()))+ "." + image_format
                image_one.save(tmp_name)

                #关闭临时文件，关闭后临时文件自动删除
                tmp_file.close()
                os.remove(tmp_file.name)
                self.write('{\"error\" : 0,\"url\" : \"'+ op_path +'\"}')
         dir = self.get_argument("dir", None)
         todo = {
             "image":UploadImage
             }
         todo.get(dir)()
class NoticeHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        NoticeContent = tornado.escape.xhtml_escape(self.get_argument('NoticeContent', None))
        NoticeTitle = tornado.escape.xhtml_escape(self.get_argument('NoticeTitle', None))
        NoticeID = int(self.get_argument('Notice',0))
        ControlUser = self.get_argument('ControlUser', '')
        now = datetime.datetime.now()
        NoticeTime = now.strftime('%Y-%m-%d')
        uid = self.current_user
        if(NoticeID > 0):
            if webui_config['WeeklyDb'].UpdateNotice(NoticeContent,NoticeTitle,NoticeID):
                self.write("'success':'done'")
            else:
                self.write("'error' : 'some thing happend.. WTF'")
        else:
            if webui_config['WeeklyDb'].AddNotice(NoticeContent,NoticeTitle,NoticeTime,ControlUser,uid):
                self.write("'success':'done'")
            else:
                self.write("'error' : 'some thing happend.. WTF'")
class WorkTreeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        UserName = self.get_secure_cookie("UName")
        def GetTreeList():
            self.write("")
        action = self.get_argument("action", None)
        todo = {
            "GetTreeList": GetTreeList,
            }
        if not action:
            self.render('ContentUnit/WorkTree/WorkTree.html', UserName = UserName)
    def post(self):
        NoticeContent = tornado.escape.xhtml_escape(self.get_argument('NoticeContent', None))
        NoticeTitle = tornado.escape.xhtml_escape(self.get_argument('NoticeTitle', None))
        NoticeID = int(self.get_argument('Notice',0))
        ControlUser = self.get_argument('ControlUser', '')
        now = datetime.datetime.now()
        NoticeTime = now.strftime('%Y-%m-%d')
        uid = self.current_user
        if(NoticeID > 0):
            if webui_config['WeeklyDb'].UpdateNotice(NoticeContent,NoticeTitle,NoticeID):
                self.write("'success':'done'")
            else:
                self.write("'error' : 'some thing happend.. WTF'")
        else:
            if webui_config['WeeklyDb'].AddNotice(NoticeContent,NoticeTitle,NoticeTime,ControlUser,uid):
                self.write("'success':'done'")
            else:
                self.write("'error' : 'some thing happend.. WTF'")

class ControlUnit(BaseHandler):
    @tornado.web.authenticated
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
                   TaskContent=result)
        def AddTask():
            self.render('ContentUnit/AddTask.html', display_uint = 'AddTask',
                    taskContent="default")
        def UserManage():
            MenuList = webui_config['WeeklyDb'].GetMenu()
            self.render('UserManage/UserManage.html', display_uint = 'UserManage',MenuList = MenuList)
        def AddUser():
            self.render('UserManage/AddUser.html', display_uint = 'AddUser')
        def AddDaily():
            now = datetime.datetime.now()
            date = now.strftime('%Y-%m-%d')
            TodayDaily=webui_config['WeeklyDb'].QueryDailyByUserAndDate(self.current_user,date,date)
            if(len(TodayDaily)>0):
                DailyContent=tornado.escape.xhtml_unescape(TodayDaily[0]["Daily_Content"])
                DailyQuestion=tornado.escape.xhtml_unescape(TodayDaily[0]["Daily_Question"])
            else:
                DailyContent=""
                DailyQuestion=""
            self.render('ContentUnit/Daily/AddDaily.html', display_uint = 'AddDaily',date=date,DailyQuestion=DailyQuestion,DailyContent=DailyContent)
        def ViewDaily():
            if int(self.GetUserLevel()) > 2:
                user_list= webui_config['WeeklyDb'].QueryUserWithEQFilter(User_ID=self.get_current_user())
            else:
                user_list= webui_config['WeeklyDb'].QueryAllUserList()
            self.render('ContentUnit/Daily/ViewDaily.html', display_uint = 'ViewDaily' , UserList=user_list)
        def Personal():
            UserID=int(self.get_current_user())
            UserModel = webui_config['WeeklyDb'].QueryUserWithEQFilter(User_ID=UserID)
            self.render('ContentUnit/PersonalInfo/EditInfo.html', display_uint = 'EditInfo',UserModel=UserModel[0])
        def AddNotice():
            UserList= webui_config['WeeklyDb'].QueryAllUserList()
            NoticeID = int(self.get_argument("NoticeID",0))
            if(NoticeID!=0):
                NoticeModel = webui_config['WeeklyDb'].QueryDailyByUserAndDate(self.current_user)
            else:
                NoticeModel = None
            self.render('ContentUnit/Notice/AddNotice.html',NoticeModel=NoticeModel,UserList=UserList)
        def ViewNotice():
            self.render('ContentUnit/Notice/ViewNotice.html')
        action = self.get_argument("action", None)
        todo = {
            "UserManage": UserManage,
            "AddTask": AddTask,
            "ViewTask": ViewTask,
            "AddUser": AddUser,
            "AddDaily":AddDaily,
            "ViewDaily":ViewDaily,
            "Personal":Personal,
            "AddNotice":AddNotice,
            "ViewNotice":ViewNotice,
            }
        if not action:
            self.render('ContentUnit/default.html', display_unit = 'default')
        elif(self.CheckPrivilege(action)):
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
    (r"/WorkTree*", WorkTreeHandler),
    (r"/AddTask/*", AddTask),
    (r"/ViewContentUnit/*", ControlUnit),
    (r"/UserHandler/*", UserHandler),
    (r"/Login/*", LoginHandler),
    (r"/PrivilegeHandler/*", PrivilegeHandler),
    (r"/PersonalHandler/*", PersonalHandler),
    (r"/DailyHandler/*", DailyHandler),
    (r"/NoticeHandler/*", NoticeHandler),
    (r"/UploadHandler/*", UploadHandler),
    (r".*", BaseHandler),
    ], **settings)

def main(**kargs):
    webui_config.update(kargs)
    server = HTTPServer(application,ssl_options={
       "certfile": os.path.join(os.path.abspath("."), "server.crt"),
       "keyfile": os.path.join(os.path.abspath("."), "server.key"),
    })
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
#    application.listen(8888)
#   tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    server = HTTPServer(application,ssl_options={
       "certfile": os.path.join(os.path.abspath("."), "server.crt"),
       "keyfile": os.path.join(os.path.abspath("."), "server.key"),
    })
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
