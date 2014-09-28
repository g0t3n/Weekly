#!/usr/bin/env python
#coding:utf-8

import os
import string
from urllib import unquote
from json import dumps as jsondumps

import tornado.ioloop
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    def get(self):
        self.write_error(404)
    def post(self):
        self.write_error(404)
    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html')
        else:
            self.write('error:' + str(status_code))

class LoginHandler(BaseHandler):
    def get(self):
        raise NotImplemented,""
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')
    def post(self):
        raise NotImplemented,""
        # 这里补充一个，获取用户输入
        self.get_argument("name")
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/index")

class MainHandler(tornado.web.RequestHandler):
    #@tornado.web.authenticated
    def get(self):
        self.render('index.html', title= 'Weekly ~~', AdminDelTask="AdminLogin")
    def post(self):
        pass

class AddTask(tornado.web.RequestHandler):
    def post(self):
        self.write("lalalal")

class ViewContentUnit(tornado.web.RequestHandler):
    def get(self):
        action = self.get_argument("action", False)
        if not action:
            self.render('ContentUnit/default.html', display_unit = 'default')
        elif action == 'ViewTask':
            self.render('ContentUnit/ViewTask.html', display_uint = 'ViewTask')
        elif action == 'AddTask':
            self.render('ContentUnit/AddTask.html', display_uint = 'AddTask')



settings = {
        "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        # "xsrf_cookies": True,
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path':  os.path.join(os.path.dirname(__file__), 'static'),
        # "login_url": "/login",
        }

application = tornado.web.Application([
    (r"/", MainHandler),
     # (r"/login", LoginHandler),
    (r"/index*", MainHandler),
    (r"/AddTask/*", AddTask),
    (r"/ViewContentUnit/*", ViewContentUnit),
    (r".*", BaseHandler),
    ], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
