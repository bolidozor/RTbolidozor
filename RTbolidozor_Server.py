#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
from tornado import web
from tornado import ioloop
from tornado import websocket
from tornado import auth
from tornado import escape
from tornado import httpserver
from tornado import options
from tornado import web
import json
#import sqlite3
import MySQLdb as mdb
import time
import datetime

cl = []
fits={'ZVPP-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/ZVPP/ZVPP-R3/meteors/',
      'ZVPP-R4':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/ZVPP/ZVPP-R4/meteors/',
     'OBSUPICE-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/OBSUPICE/OBSUPICE-R3/meteors/',
     'OBSUPICE-R4':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/OBSUPICE/OBSUPICE-R4/meteors/',
     'SVAKOV-R7':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/svakov/SVAKOV-R7/meteors/',
     'SVAKOV-R6':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/svakov/SVAKOV-R6/meteors/',
     'TEST-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/svakov/TEST-R3/meteors/',
     'ZEBRAK-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/ZEBRAK/ZEBRAK-R3/meteors/',
     'NACHODSKO-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/nachodsko/NACHODSKO-R3/meteors/',
     'ZVOLENEVES-R1':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/ZVOLENEVES/ZVOLENEVES-R1/meteors/'}

js9={'ZVPP-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/ZVPP/ZVPP-R3/meteors',
     'ZVPP-R4':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/ZVPP/ZVPP-R4/meteors',
     'OBSUPICE-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/OBSUPICE/OBSUPICE-R3/meteors',
     'OBSUPICE-R4':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/OBSUPICE/OBSUPICE-R4/meteors',
     'SVAKOV-R6':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/svakov/SVAKOV-R6/meteors',
     'SVAKOV-R7':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/svakov/SVAKOV-R7/meteors',
     'TEST-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/svakov/TEST-R3/meteors',
     'ZEBRAK-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/ZEBRAK/ZEBRAK-R3/meteors',
     'NACHODSKO-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/nachodsko/NACHODSKO-R3/meteors',
     'ZVOLENEVES-R1':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/ZVOLENEVES/ZVOLENEVES-R1/meteors'}

space={'ZVPP-R3':'http://space.astro.cz/bolidozor/ZVPP/ZVPP-R3/meteors',
     'ZVPP-R4':'http://space.astro.cz/bolidozor/ZVPP/ZVPP-R4/meteors',
     'OBSUPICE-R3':'http://space.astro.cz/bolidozor/OBSUPICE/OBSUPICE-R3/meteors',
     'OBSUPICE-R4':'http://space.astro.cz/bolidozor/OBSUPICE/OBSUPICE-R4/meteors',
     'SVAKOV-R6':'http://space.astro.cz/bolidozor/svakov/SVAKOV-R6/meteors',
     'SVAKOV-R7':'http://space.astro.cz/bolidozor/svakov/SVAKOV-R7/meteors',
     'TEST-R3':'http://space.astro.cz/bolidozor/svakov/TEST-R3/meteors',
     'ZEBRAK-R3':'http://space.astro.cz/bolidozor/ZEBRAK/ZEBRAK-R3/meteors',
     'NACHODSKO-R3':'http://space.astro.cz/bolidozor/nachodsko/NACHODSKO-R3/meteors',
     'ZVOLENEVES-R1':'http://space.astro.cz/bolidozor/ZVOLENEVES/ZVOLENEVES-R1/meteors'}

def _sql(query):
        #dbPath = 'bolid.db'
        #connection = sqlite3.connect(dbPath)
        #cursorobj = connection.cursor()
        connection = mdb.connect(host="localhost", user="root", passwd="root", db="bolid", use_unicode=True, charset="utf8")
        cursorobj = connection.cursor()
        result = None
        try:
                cursorobj.execute(query)
                result = cursorobj.fetchall()
                connection.commit()
        except Exception, e:
                print "Err", e
        connection.close()
        return result


def _sqlWeb(query):
        dbPath = 'web.db'
        connection = sqlite3.connect(dbPath)
        cursorobj = connection.cursor()
        try:
                cursorobj.execute(query)
                result = cursorobj.fetchall()
                connection.commit()
        except Exception:
                raise
        connection.close()
        return result


class WebHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, addres=None):
        print "web", addres
        self.render("www/layout/index.html", title="My title", user=self.get_secure_cookie("name"))

class ClientsHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        print cl
        self.render("index.html")

class MultiBolid(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        month = self.get_argument('month', None)
        if not month:
            month = datetime.datetime.utcnow().strftime('%Y-%m')
            date_from = time.mktime(time.strptime(month, "%Y-%m"))
            date_to  =  time.mktime(time.strptime(month, "%Y-%m"))+60*60*24*30
        elif month == "all":
            date_from = 0
            date_to = time.time()
        else:
            date_from = time.mktime(time.strptime(month, "%Y-%m"))
            date_to  =  time.mktime(time.strptime(month, "%Y-%m"))+60*60*24*30

        #print "webM", params, self.get_argument('month', None)

        items = ["Item 1", "Item 2", "Item 3"]

        event = _sql("SELECT * FROM meta WHERE link != 0 AND time > %s AND time < %s GROUP BY link ORDER BY time DESC;" %(str(date_from), str(date_to)))     # seznam jedtotlivých událostí
        print("SELECT * FROM meta WHERE link != 0 AND time > %s AND time < %s GROUP BY link ORDER BY time DESC;" %(str(date_from), str(date_to)))     # seznam jedtotlivých událostí
        query = _sql("SELECT * FROM meta WHERE link != 0 AND time > %s AND time < %s ORDER BY time DESC;" %(str(date_from), str(date_to)))    # seznam vsech udalosti
        print "ssssssss", event, "oooooooo", query
        self.render("www/layout/MultiBolid.html", title="Bloidozor multi-bolid database", range=[date_from, date_to], data=[event, query], _sql = _sql, _sqlWeb = _sqlWeb, links=[fits, js9, space], parent=self)

class ZooBolid(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("www/layout/ZooBolid.html", title="Bloidozor game")

class AstroTools(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("www/layout/AstroTools/index.html", title="Astro tools")

class RTbolidozor(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        self.render("www/layout/realtime_layout.html", title="Bloidozor multi-bolid database", _sql = _sql, _sqlWeb = _sqlWeb, links=[fits, js9], parent=self)

class JSweb(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        self.render("www/layout/js.html", title="Bloidozor multi-bolid database", _sql = _sql, _sqlWeb = _sqlWeb, links=[fits, js9], parent=self)

class AuthLoginHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        try:
            errormessage = self.get_argument("error")
        except:
            errormessage = ""
        self.render("www/layout/login.html", errormessage = errormessage)

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.check_permission(password, username)
        if auth:
            self.set_current_user(username)
            self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + tornado.escape.url_escape("Login incorrect")
            self.redirect(u"/auth/login/" + error_msg)

    def check_permission(self, password, username):
        if username == "admin" and password == "admin":
            return True
        return False

    def set_current_user(self, user):
        if user:
            print "set_secure_user", tornado.escape.json_encode(user)
            self.set_secure_cookie("name", "Roman Dvořák")
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")


class AuthLogoutHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.clear_cookie("name")
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))

class AuthNewHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def post(self, type):
        print "new type data,", type
        if type == "user":
            print "ADD DATA:", _sql("INSERT INTO user (name, pass, r_name, email, text) VALUES ('%s', '%s', '%s', '%s', '%s')" %(self.get_argument('user', ''), self.get_argument('name', ''), self.get_argument('r_name', ''), self.get_argument('email', ''), self.get_argument('describe', '')))
            return self.write("done")

        elif type == "observatory":
            print "ADD DATA:",  _sql("INSERT INTO observatory (name, lat, lon, alt, id_owner, text, id_astrozor) VALUES ('%s', '%f', '%f', '%i', '%i', '%s', '%s')" %(self.get_argument('name', ''), float(self.get_argument('lat', '')), float(self.get_argument('lon', '')), int(self.get_argument('alt', '')), int(self.get_argument('owner', '')), self.get_argument('describe', ''), self.get_argument('link', '')))
            return self.write("done")

        elif type == "station":
            print "ADD DATA:",  _sql("INSERT INTO station (name, id_observatory, map) VALUES ('%s', '%i', '%s')" %(self.get_argument('name', ''), int(self.get_argument('observatory', '')), self.get_argument('describe', '')))
            return self.write("done")

        else:
            return self.write("err")

class AuthSettingHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("www/layout/admin.html", title="Administration page", s_cookie=self.get_secure_cookie, _sql = _sql, _sqlWeb = _sqlWeb)
        

class SocketHandler(websocket.WebSocketHandler): 
    def initialize(self):
        self.StationList = []

    def check_origin(self, origin):
        return True

    def open(self):
        print "Opened new port: ", self
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)

    def on_message(self, message):
        self.write_message(u"ACK")
        if message[0] == "$":
            m_type = message[1:message.find(";")]
            if m_type == "HI":
                self.StationList.append([self] + message[message.find(";")+1:].split(";") )
                print self.StationList
            elif m_type == "stanica":       # inicializacializacni sprava od stanice (obsahoje o sobe informace)
                jsonstation = json.loads(message.split(";")[1])
                _sqlWeb("INSERT INTO stations (time, name, ident, handler, time_last, lat, lon, url_space, url_js9, url_rmob) VALUES (" +str(time.time())+ ",'" +str(jsonstation['name'])+ "', '" +str(jsonstation['ident'])+"', '" +str(self)+"'," +str(time.time())+ ", " +str(jsonstation['lat'])+ "," +str(jsonstation['lon'])+ ",'URL', 'URL', 'URL'" + ")")
            elif m_type == "event":
                query = _sqlWeb("SELECT name FROM stations WHERE handler = '"+str(self)+"';")[0]
                print "EVENT", query[0]
                for client in cl:
                    client.write_message(u"$meta;" + str(query[0])+ ";" +"{aa}")
        elif message[0] == '#':
            print "multicast"
            for client in cl:
                client.write_message(u"multicast: " + message)
        else:
            print "Prijata zprava: ", message


app = web.Application([
        (r'/', WebHandler),
        (r'/ws', SocketHandler),
        (r'/clients', ClientsHandler),
        (r'/multibolid(.*)', MultiBolid),
        (r'/multibolid', MultiBolid),
        (r'/realtime(.*)', RTbolidozor),
        (r'/realtime', RTbolidozor),
        (r'/astrotools(.*)', AstroTools),
        (r'/astrotools', AstroTools),
        (r'/zoo', ZooBolid),
        (r'/zoo(.*)', ZooBolid),
        (r"/auth/login/", AuthLoginHandler),
        (r"/auth/logout/", AuthLogoutHandler),
        (r"/auth/setting/", AuthSettingHandler),
        (r"/auth/new/(.*)", AuthNewHandler),
        (r'/js(.*)', JSweb),
        (r'/js', JSweb),
        
        (r'/(favicon.ico)', web.StaticFileHandler, {'path': '.'}),
        (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
        (r"/(.*\.png)", tornado.web.StaticFileHandler,{"path": './www/media/' }),
        (r"/(.*\.jpg)", tornado.web.StaticFileHandler,{"path": './www/media/' }),
        (r"/(.*\.css)", tornado.web.StaticFileHandler,{"path": './www/css/' }),
        (r"/(.*\.wav)", tornado.web.StaticFileHandler,{"path": './www/wav/' }),
       #(r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
        (r"/(.*)", WebHandler),
    ],
    cookie_secret="ROT13IrehaxnWrArwyrcfvQvixnAnFirgr",
    debug=True,
    autoreload=True)

def main():
    app.listen(5252)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
