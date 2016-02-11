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
import svgwrite


cl = []

def wwwCleanName(string):
    return ''.join( c for c in string if c not in '?:!/;-_#$%^!@' )


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

        event = _sql("SELECT * FROM meta WHERE link != 0 AND time > %s AND time < %s GROUP BY link ORDER BY time DESC;" %(str(date_from), str(date_to)))     # seznam jedtotlivých událostí
        query = _sql("SELECT * FROM meta WHERE link != 0 AND time > %s AND time < %s ORDER BY time DESC;" %(str(date_from), str(date_to)))    # seznam vsech udalosti
        self.render("www/layout/MultiBolid.html", title="Bloidozor multi-bolid database", range=[date_from, date_to], data=[event, query], _sql = _sql, parent=self)

class ZooBolid(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("www/layout/ZooBolid.html", title="Bloidozor game")


######################################################################################################################
######################################################################################################################
########
######################################################################################################################
######################################################################################################################


class Browser(web.RequestHandler):
    def calc_colour(self, val):
        if self.color == 1:
            if val < self.maxVal/3:    #    0/3 ... 1/3
                red = 0
                green = val*3.0 * 255.0/self.maxVal
                blue = 255

            elif val < self.maxVal/3*2:    #    1/3 ... 2/3
                red = val*3 * 255.0/self.maxVal
                green = 255
                blue = (self.maxVal*3.0 - val*3.0) * 255.0/self.maxVal - 254

            else:                               #    2/3 ... 3/3
                red = 255
                green = (self.maxVal*3.0 - val*3.0)*255.0/self.maxVal
                blue = 0
        else:
            red = val*255/self.maxVal
            green = val*255/self.maxVal
            blue = val*255/self.maxVal
        return "rgb(%i,%i,%i)"%(int(red), int(green), int(blue))

    def get(self, params=None):
        d_month = self.get_argument('month', None)

        self.maxVal = self.get_argument('max', 100)
        self.color = self.get_argument('color', 1)
        height = self.get_argument('height', 250)
        width = self.get_argument('width', 700)
        step = self.get_argument('step', 0)

        if 'plotJS' in params:

            if d_month and d_month != "last" and d_month != "LAST":
                d_month = time.mktime(time.strptime(d_month, "%Y-%m"))
            d_from = self.get_argument('from', None)
            if d_from:
                d_from = time.mktime(time.strptime(d_from, "%Y-%m"))
            d_to = self.get_argument('to', None)
            if d_to:
                d_to = time.mktime(time.strptime(d_to, "%Y-%m"))

            if d_month == "last" or d_month == "LAST":
                today = datetime.datetime.now()
                now = time.time()
                # time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
                #tomidnight = (86400000-(now - today.replace(hour=0, minute=0, second=0, microsecond=0).time().microsecond)/1000)
                d_month = now-3600*24*(int((int(width)//int(int(height)/24)))-3)
                date_from = d_month
                date_to   = time.time()
            elif not d_month and not d_from and not d_to:
                d_month = time.time()
                date_from = d_month
                date_to  =  d_month+60*60*24*30
            elif d_month == "all":
                date_from = 0
                date_to = time.time()
            elif d_month:
                date_from = d_month
                date_to  =  d_month+60*60*24*30
            elif d_from and d_to:
                date_from = d_month
                date_to  =  d_month+60*60*24*30
            if d_from and d_to:
                date_from = d_from
                date_to = d_to
            d = params.split('/')
            #print params, d
            
            counts = _sql("select 3600*(meta.time div 3600), count(*) from meta LEFT JOIN station ON station.id = meta.id_station WHERE station.name = '%s' AND time > '%s' AND time < '%s' GROUP BY meta.time div 3600;" %(d[2], str(date_from), str(date_to)))
            if counts:
                self.maxVal = max(item[1] for item in counts)
            svg = svgwrite.Drawing(size=(width,height))
            pixH = float(height)/24.0
            pixW = float(width)/31.0
            pixW = pixH
            for hour in counts:
                dataTime = datetime.datetime.fromtimestamp(hour[0])
                svg.add(svg.rect( insert=(pixW*((hour[0]-date_from)//86400), pixH*dataTime.hour-1), size=(pixW, pixH), stroke = self.calc_colour(hour[1]), fill = self.calc_colour(hour[1])) )
            Ssvg = svg.tostring()
            #print Ssvg

            self.write(Ssvg)
        else:
            self.render("www/layout/browser.html", title="Bloidozor data browser", _sql = _sql, parent=self)








class AstroTools(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("www/layout/AstroTools/index.html", title="Astro tools")

class RTbolidozor(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        self.render("www/layout/realtime_layout.html", title="Bloidozor multi-bolid database", _sql = _sql, parent=self, CleanName = wwwCleanName)

class JSweb(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        self.render("www/layout/js.html", title="Bloidozor multi-bolid database", _sql = _sql, parent=self)

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
        self.render("www/layout/admin.html", title="Administration page", s_cookie=self.get_secure_cookie, _sql = _sql)
        

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
                print "type: HI", self.StationList
            elif m_type == "stanica":       # inicializacializacni sprava od stanice (obsahoje o sobe informace)
                jsonstation = json.loads(message.split(";")[1])
                print "type stanica", jsonstation['ident']
                print("UPDATE station SET handler = '" + str(self)+"' WHERE name='"+jsonstation['ident']+"';")
                _sql("UPDATE station SET handler = '" + str(self)+"' WHERE name='"+jsonstation['ident']+"';")
            elif m_type == "event":
                print "type event", message
                query = _sql("SELECT name FROM station WHERE handler = '"+str(self)+"';")[0]
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
        (r'/browser(.*)', Browser),
        (r'/browser', Browser),
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
