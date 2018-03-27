#!/usr/bin/python
# -*- coding: utf-8 -*-
import tornado
#from tornado import web
from tornado import ioloop
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
import calendar
import svgwrite
import crypt
import os


from handlers import rtmap, count, multibolid, auth, admin, stations, around, timeline
from handlers import _sql, BaseHandler


def wwwCleanName(string):
    return ''.join( c for c in string if c not in '?:!/;-_#$%^!@., (){}[]' )


class WebHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, addres=None):
        print "web", addres
        self.render("home.hbs", title="Bolidozor", user=self.get_secure_cookie("login"))

class ClientsHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        #print cl
        self.render("index.html")


######################################################################################################################
######################################################################################################################
########
######################################################################################################################
######################################################################################################################


class DBreader(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        print params, params.split('/')
        if 'data' in params:
            if self.get_argument('from_date', '') != '':
                from_date = time.mktime(time.strptime(self.get_argument('from_date', ''), "%Y-%m-%d")),
            else:
                from_date = time.time()-3600*24

            if self.get_argument('to_date', '') != '':
                to_date = time.mktime(time.strptime(self.get_argument('to_date', ''), "%Y-%m-%d")),
            else:
                to_date = time.time()


            print from_date, to_date, table
            table = self.get_argument('table', 'snap')
        else:
            table = self.get_argument('table', 'snap')
            self.render("www/layout/DBreader/mainpage.html", title="DBreader", _sql=_sql, parent=self, argv = self.get_argument, table=table)



class SimpleData(web.RequestHandler):
    def get(self, params = None):
        parametry = params.split('/')
        if "txt" in parametry:
            self.write("hi, jak je? "+ repr(parametry))
            day = self.get_argument('date', '')
        else:
            self.write("hi, jak je?")



class AstroTools(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        self.render("www/layout/AstroTools/index.html", title="Astro tools")


class JSweb(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        self.render("js.hbs", title="Bolidozor multi-bolid database", _sql = _sql, parent=self)

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
    #@tornado.web.asynchronous
    def post(self, type):
        print "new type data,", type
        if type == "user":
            print "ADD DATA:", _sqlo("INSERT INTO user (name, pass, r_name, email, text) VALUES ('%s', '%s', '%s', '%s', '%s')" %(self.get_argument('user', ''), self.get_argument('name', ''), self.get_argument('r_name', ''), self.get_argument('email', ''), self.get_argument('describe', '')))
            return self.write("done")

        elif type == "observatory":
            print "ADD DATA:",  _sqlo("INSERT INTO observatory (name, lat, lon, alt, id_owner, text, id_astrozor) VALUES ('%s', '%f', '%f', '%i', '%i', '%s', '%s')" %(self.get_argument('name', ''), float(self.get_argument('lat', '')), float(self.get_argument('lon', '')), int(self.get_argument('alt', '')), int(self.get_argument('owner', '')), self.get_argument('describe', ''), self.get_argument('link', '')))
            return self.write("done")

        elif type == "station":
            print "ADD DATA:",  _sqlo("INSERT INTO station (name, id_observatory, map) VALUES ('%s', '%i', '%s')" %(self.get_argument('name', ''), int(self.get_argument('observatory', '')), self.get_argument('describe', '')))
            return self.write("done")
        #self.dbc.execute('CREATE TABLE server (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(30) UNIQUE KEY, lat FLOAT, lon FLOAT, alt FLOAT, type INT(3), text VARCHAR(255), id_owner INT, id_station INT, id_astrozor INT);')

        elif type == "server":
            print "ADD DATA:",  _sqlo("INSERT INTO server (name, lat, lon, alt, type, text, id_owner, id_astrozor) VALUES ('%s', '%f', '%f', '%f', '%i', '%s', '%i', '%i')" %(self.get_argument('name', ''), float(self.get_argument('lat', 0)), float(self.get_argument('lon', 0)), float(self.get_argument('alt', -1)),  int(self.get_argument('type', 0)), self.get_argument('describe', ''), int(self.get_argument('id_owner', -1)), int(self.get_argument('id_astrozor', -1)) ))
            return self.write("done")

        else:
            return self.write("err")

class AuthSettingHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("www/layout/admin.html", title="Administration page", s_cookie=self.get_secure_cookie, _osql = _sqlo, _sql = _sql)

class AuthUpdateHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, type):
        path = type.split('/')
        print path
        self.render("www/layout/adminUpdate.html", title="update page", s_cookie=self.get_secure_cookie, _sql = _sql, path=path)

    #@tornado.web.asynchronous
    def post(self, type):
        print "GET", type
        type = type.split('/')
        print "new type data,", type
        if type[0] == "update":
            if type[1] == "observatory":
                print ("UPDATE observatory SET name = '%s', lat = %f, lon = %f, alt = %f, text = '%s', id_owner = %i, id_astrozor = %i WHERE id = %i;" %( self.get_argument('name', ''), float(self.get_argument('lat', '')), float(self.get_argument('lon', '')), float(self.get_argument('alt', '-1')), self.get_argument('text', ''), int(self.get_argument('id_owner', '-1')), int(self.get_argument('id_astrozor', '-1')), int(self.get_argument('id',''))   ))
                print "ADD DATA:",  _sql("UPDATE observatory SET name = '%s', lat = %f, lon = %f, alt = %f, text = '%s', id_owner = %i, id_astrozor = %i WHERE id = %i;" %( self.get_argument('name', ''), float(self.get_argument('lat', '')), float(self.get_argument('lon', '')), float(self.get_argument('alt', '-1')), self.get_argument('text', ''), int(self.get_argument('id_owner', '-1')), int(self.get_argument('id_astrozor', '-1')), int(self.get_argument('id',''))   ))
                return self.write("done")

            elif type[1] == "station":
                # id, name, id_observatory, id_stationstat, id_stationtype, handler, text
                out = _sql("UPDATE station SET name = '%s', id_stationstat = '%s', id_stationtype = '%s', handler = '%s', text = '%s' WHERE id = %i;" %( self.get_argument('name', ''), str(self.get_argument('id_stationstat', '')), str(self.get_argument('id_stationtype','')), str(self.get_argument('handler','')), str(self.get_argument('text','')), int(self.get_argument('id','')) ))
                return self.write("done Station update" + str(out))

            elif type[1] == "server":
                print "ADD DATA:",  _sql("UPDATE server SET name = '%s', lat = %f, lon = %f, id_owner = %i, id_station = %i, id_astrozor = %i WHERE id = %i;" %( self.get_argument('name', ''), float(self.get_argument('lat', '')), float(self.get_argument('lon', '')), int(self.get_argument('id_owner', '-1')), int(self.get_argument('id_observatory', '-1')), int(self.get_argument('id_astrozor', '-1')), int(self.get_argument('id',''))  ))
                return self.write("done")
            
            elif type[1] == "user":
                print "ADD DATA:", _sql("UPDATE user SET name = '%s', r_name = '%s', permission = %i, email = '%s', text = '%s', id_astrozor = %i WHERE id = %i;" %( self.get_argument('name', ''), self.get_argument('r_name', ''), int(self.get_argument('permission', '')), self.get_argument('email', ''), self.get_argument('text', ''), int(self.get_argument('id_astrozor', '-1')), int(self.get_argument('id','')) ))
                return self.write("done")

            else:
                return self.write("err")
        
        if type[0] == "add":
            if type[1] == "user":#IrehaxnRinFzbyxbinwrfhcreQvixn
                if self.get_argument('pass', '')==self.get_argument('passv', ''):
                    passv = crypt.crypt(self.get_argument('pass', ''), "IrehaxnRinFzbyxbinwrfhcreQvixn")
                    print "ADD DATA:", _sql("INSERT INTO user (name, r_name, email, pass, id_permission, id_astrozor, www, text) VALUES ('%s', '%s', '%s', '%s', %s, '%s', '%s', '%s')" %(self.get_argument('name', ''), self.get_argument('r_name', ''), self.get_argument('email', ''), passv, self.get_argument('id_permission', ''), self.get_argument('id_astrozor', ''), self.get_argument('www', ''), self.get_argument('text', '')))
                    return self.write("done")
                else:
                    return self.write("Hesla se neshodují")

            elif type[1] == "observatory":
                print "ADD DATA:",  _sql("INSERT INTO observatory (name, id_obstype, id_user, lat, lon, alt, text) VALUES ('%s', %s, %s, '%s', '%s', '%s', '%s')" %(self.get_argument('name', ''), self.get_argument('id_obstype', ''), self.get_argument('id_user', ''), self.get_argument('lat', ''), self.get_argument('lon', ''), self.get_argument('alt', ''), self.get_argument('text', '')) )
                return self.write("done")

            elif type[1] == "station":
                print "ADD DATA:",  _sql("INSERT INTO station (name, id_observatory, id_stationstat, id_stationtype, handler, text) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" %(self.get_argument('name', ''), self.get_argument('id_observatory', ''), self.get_argument('id_stationstat', ''), self.get_argument('id_stationtype', ''), self.get_argument('handler', ''), self.get_argument('text', '')))
                return self.write("done")

            elif type[1] == "server":
                print "ADD DATA:",  _sql("INSERT INTO server (name, lat, lon, alt, type, text, id_owner, id_astrozor) VALUES ('%s', '%f', '%f', '%f', '%i', '%s', '%i', '%i')" %(self.get_argument('name', ''), float(self.get_argument('lat', 0)), float(self.get_argument('lon', 0)), float(self.get_argument('alt', -1)),  int(self.get_argument('type', 0)), self.get_argument('describe', ''), int(self.get_argument('id_owner', -1)), int(self.get_argument('id_astrozor', -1)) ))
                return self.write("done")

            else:
                return self.write("err")


tornado.options.define("port", default=10004, help="port", type=int)
tornado.options.define("debug", default=True, help="debug mode")
tornado.options.parse_config_file("/home/roman/rtbolidozor.conf")

class WebApp(tornado.web.Application):

    def __init__(self, config={}):

        name = 'ZVPP'
        server = 'arom-weather.local'

        server_url = '{}:{}'.format(server, tornado.options.options.port)

        handlers =[
            (r'/', WebHandler),
            (r'/ws', rtmap.SocketHandler),
            (r'/event', rtmap.MeteorRtHandler),
            (r'/bolid', rtmap.SocketHandler),

            (r'/multibolid', multibolid.MultiBolid),
            (r'/multibolid/', multibolid.MultiBolid),
            (r'/multibolid(.*)', multibolid.MultiBolid),

            (r'/around', around.Around),
            (r'/around/', around.Around),
            (r'/around(.*)', around.Around),


            (r'/timeline', timeline.Timeline),
            (r'/timeline/', timeline.Timeline),
            (r'/timeline(.*)', timeline.Timeline),

            (r'/realtime(.*)', rtmap.RTbolidozor),
            (r'/realtime', rtmap.RTbolidozor),
            (r'/map(.*)', rtmap.RTbolidozor),
            (r'/map', rtmap.RTbolidozor),

            (r'/stations.kml', stations.station_kml),
            (r'/stations.kml/', stations.station_kml),
            (r'/stations/kml', stations.station_kml),
            (r'/stations/kml/', stations.station_kml),

            (r'/browser(.*)', count.Browser),
            (r'/counts(.*)', count.Browser),
            (r'/database', count.Browser),
            (r'/intensity/', count.intensity),
            (r'/intensity', count.intensity),


            #(r'/browser', DBreader),
            (r'/database(.*)', DBreader),

            (r'/admin/add/(.*)', admin.new),
            (r'/admin/sendEmail/(.*)', admin.sendEmail),
            (r'/admin(.*)', admin.admin),
            (r'/admin/(.*)', admin.admin),
            
            #(r'/astrotools(.*)', AstroTools),
            #(r'/astrotools', AstroTools),
            #(r'/data(.*)', SimpleData),
            #(r'/data', SimpleData),
            #(r"/auth/login/", AuthLoginHandler),
            #(r"/auth/logout/", AuthLogoutHandler),
            #(r"/auth/setting/", AuthSettingHandler),
            #(r"/auth/new/(.*)", AuthNewHandler),
            #(r"/auth/update/(.*)", AuthUpdateHandler),
            (r'/js(.*)', JSweb),
            (r'/js', JSweb),

            (r'/login/oauth/github', auth.O_github),
            (r'/login/', auth.O_login),
            (r'/login', auth.O_login),
            (r'/logout/', auth.O_logout),
            (r'/logout', auth.O_logout),
            (r'/newuser', auth.newuser),
            
            (r'/(favicon.ico)', web.StaticFileHandler, {'path': '.'}),
            (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
            (r"/(.*\.png)", tornado.web.StaticFileHandler,{"path": './www/media/' }),
            (r"/(.*\.jpg)", tornado.web.StaticFileHandler,{"path": './www/media/' }),
            (r"/(.*\.css)", tornado.web.StaticFileHandler,{"path": './www/css/' }),
            (r"/(.*\.wav)", tornado.web.StaticFileHandler,{"path": './www/wav/' }),
           #(r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
            (r"/(.*)", WebHandler),
        ]
        settings = dict(
            cookie_secret="ROT13IrehaxnWrArwyrcfvQvixnAnFirgr",
            template_path= "/home/roman/repos/RTbolidozor/template/",
            static_path= "/home/roman/repos/RTbolidozor/static/",
            #xsrf_cookies=True,
            xsrf_cookies=False,
            name="RTbolidozor",
            server_url="rtbolidozor.astro.cz",
            site_title="RTbolidozor",
            login_url="/login",
            #ui_modules=modules,
            port=tornado.options.options.port,
            compress_response=True,
            debug=tornado.options.options.debug,
            autoreload=True
        )

        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(WebApp())
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
