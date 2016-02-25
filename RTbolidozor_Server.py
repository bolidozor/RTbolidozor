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
import calendar
import svgwrite
import crypt
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import mpld3
from mpld3 import plugins, utils
from matplotlib.dates import MONDAY
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter


cl = []

def wwwCleanName(string):
    return ''.join( c for c in string if c not in '?:!/;-_#$%^!@., (){}[]' )


def _sqlo(query, read=False):
        #dbPath = 'bolid.db'
        #connection = sqlite3.connect(dbPath)
        #cursorobj = connection.cursor()
        print ">>", query
        connection = mdb.connect(host="localhost", user="root", passwd="root", db="bolid", use_unicode=True, charset="utf8")
        cursorobj = connection.cursor()
        result = None
        try:
                cursorobj.execute(query)
                result = cursorobj.fetchall()
                if not read:
                    connection.commit()
        except Exception, e:
                print "Err", e
        connection.close()
        return result

def _sql(query, read=False):
        print "#>", query
        connection = mdb.connect(host="localhost", user="root", passwd="root", db="RTbolidozor", use_unicode=True, charset="utf8")
        cursorobj = connection.cursor()
        result = None
        try:
                cursorobj.execute(query)
                result = cursorobj.fetchall()
                if not read:
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
        MBtype = params.split('/')
        if len(MBtype) <= 1:
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
            self.render("www/layout/MultiBolid.html", title="Bloidozor multi-bolid database", range=[date_from, date_to], _sql = _sql, parent=self)
        else:
            if MBtype[1]=="event":
                print "EVENT FOR "
                id_event = int(MBtype[2])
                self.render("www/layout/MultiBolid_one_event.html", title="Bloidozor multi-bolid database | EVENT", data=[id_event], _sql = _sql, parent=self)

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
                red = 0
                green = 255
                blue = (self.maxVal*3.0 - val*3.0) * 255.0/self.maxVal - 254

            elif val < self.maxVal:                               #    2/3 ... 3/3
                red = val*3 * 255.0/self.maxVal
                green = (self.maxVal*3.0 - val*3.0)*255.0/self.maxVal
                blue = 0

            else:
                red = 100
                green = 100
                blue = 100
        else:
            red = val*255/self.maxVal
            green = val*255/self.maxVal
            blue = val*255/self.maxVal
        return "rgb(%i,%i,%i)"%(int(red), int(green), int(blue))

    def get(self, params=None):
        pwr_start_time = time.time()
        d_month = self.get_argument('month', 'last')

        self.maxVal = int(self.get_argument('max', 100))
        self.color = int(self.get_argument('color', 1))
        height = int(self.get_argument('height', 250))-20
        width = int(self.get_argument('width', 700))
        step = int(self.get_argument('step', 0))
        print params, d_month

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
                now = time.time() + (86400-(int(time.time()) - calendar.timegm((today.replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()) )) + 86400 # cas dnesni pulnoci
                print "dnes bude datum", now
                # time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
                #tomidnight = (86400000-(now - today.replace(hour=0, minute=0, second=0, microsecond=0).time().microsecond)/1000)
                #d_month = now-3600*24*60
                date_from = now-3600*24*60
                date_to   = now
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
            if d[2] == 'all':
                print "aaa", float(date_from), float(date_to)
                counts = np.array(_sql("select (meta.time div 3600), count(*) from meta JOIN station ON station.id = meta.id_station WHERE (time BETWEEN %f AND %f) GROUP BY meta.time div 3600 ORDER BY time DESC;" %(float(date_from), float(date_to)), True))
            else:
                counts = np.array(_sql("select (meta.time div 3600), count(*) from meta JOIN station ON station.id = meta.id_station WHERE station.name = '%s' AND (time BETWEEN %f AND %f) GROUP BY meta.time div 3600 ORDER BY time DESC;" %(d[2], float(date_from), float(date_to)), True))
            
            #if counts:
            '''
            xmax, ymax = np.amax(counts, axis=0)
            self.maxVal = ymax
            print counts.shape
            #counts = counts.reshape((counts.shape[0]/24, 24))
            svg = svgwrite.Drawing(size=(width,height+20))
            pixH = float(height)/24.0
            #pixW = float(width)/31.0
            pixW = pixH
            maxday = ((int(time.time())//3600)//24)+1
            
            for hour in np.nditer(counts):
                #print hour
                dataTime = datetime.datetime.fromtimestamp(hour[0])
                svg.add(svg.rect(insert=( int(width) - int(pixW) - int(pixW)*int((maxday-hour[0]//3600//24)), pixH*int(dataTime.hour)), size=(pixW, pixH), stroke = self.calc_colour(hour[1]), fill = self.calc_colour(hour[1])) )
            Ssvg = svg.tostring()
            #print Ssvg
            print "################ CAS ....", pwr_start_time-time.time()
            self.write(Ssvg)
            '''
            # every monday
            mondays = WeekdayLocator(MONDAY)

            # every 3rd month
            months = MonthLocator(range(1, 13), bymonthday=1, interval=3)
            monthsFmt = DateFormatter("%b '%y")
  
            maxday = ((int(time.time())//3600)//24)+1
            size = (24,  int(maxday-counts[0][0]//86400))
            #data = np.array.null(size=size)
            data = np.zeros(size)

            print "velikosti", np.amin(counts,axis=0)[0], np.amax(counts,axis=0)[0]
            mini = np.amin(counts,axis=0)[0]
            for x in range (np.amin(counts,axis=0)[0], np.amax(counts,axis=0)[0]):
                try:
                    k = x-mini
                    a = counts[k][0]
                    b = counts[k][1]
                    print k-(k//24)*24, (k//24)*24, k//24, k, a, b, x
                    data[k-(k//24)*24][k]=b
                except Exception, e:
                    pass
            print "velikosti", np.amin(counts,axis=0)[0], np.amax(counts,axis=0)[0], size
            
            
            #print counts.shape
            #print dates

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.imshow(data, cmap=plt.cm.jet, interpolation='nearest', aspect='auto')
            ax.grid(color='white', linestyle='solid')
            ax.xaxis.set_major_locator(months)
            ax.xaxis.set_major_formatter(monthsFmt)
            ax.xaxis.set_minor_locator(mondays)
            fig.autofmt_xdate()
            
            self.write(mpld3.fig_to_html(fig))


        elif "yeartrend" in params:
            d = params.split('/')

            #now = datetime.datetime.utcnow()
            
            start_time = time.mktime(datetime.date(2016, 1, 1).timetuple())
            end_time = time.mktime(datetime.date(2017, 1, 1).timetuple())
            if d[2] == 'all':
                counts = np.array(_sql("select (86400)*(meta.time div (86400)), count(*) from meta JOIN station ON station.id = meta.id_station WHERE (time BETWEEN %f AND %f) GROUP BY meta.time div (86400) ORDER BY time;" %(float(start_time), float(end_time)), True))
            else:
                counts = np.array(_sql("select (86400)*(meta.time div (86400)), count(*) from meta JOIN station ON station.id = meta.id_station WHERE (station.name = '%s') AND (time BETWEEN %f AND %f) GROUP BY meta.time div (86400) ORDER BY time;" %(d[2], float(start_time), float(end_time)), True))
            xmax, ymax = np.amax(counts, axis=0)
            self.maxVal = ymax

            svg = svgwrite.Drawing(size=(width,height+20))
            pointH = float(height)/ymax
            poinW = float(width)/(366)

            
            #svg.add(svg.rect(insert=( 190, 100), size=(50, 50), stroke = "#101010", fill = "#707070" ))
            """
            for hour in counts:
                dataTime = datetime.datetime.fromtimestamp(int(hour[0]))
                #svg.add(svg.rect(insert=( int(width) - int(pixW) - int(pixW)*int((maxday-hour[0]//3600//24)), pixH*int(dataTime.hour)), size=(pixW, pixH), stroke = self.calc_colour(hour[1]), fill = self.calc_colour(hour[1])) )
                x=(int(hour[0])-start_time)/48600*poinW
                y=height-int(hour[1])*pointH
                try:
                    svg.add(svg.line((x_o, y_o),(x, y), style="stroke:rgb(255,0,0);stroke-width:2"))
                except Exception, e:
                    pass
                x_o = x
                y_o = y
            Ssvg = svg.tostring()
            print "################ CAS ....", pwr_start_time-time.time()
            """
            # every monday
            mondays = WeekdayLocator(MONDAY)

            # every 3rd month
            months = MonthLocator(range(1, 13), bymonthday=1, interval=3)
            monthsFmt = DateFormatter("%b '%y")

            dates = [q[0] for q in counts]
            values = [q[1] for q in counts]

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(dates, values)
            ax.set_xlim([start_time,end_time])
            ax.grid(color='white', linestyle='solid')
            ax.xaxis.set_major_locator(months)
            ax.xaxis.set_major_formatter(monthsFmt)
            ax.xaxis.set_minor_locator(mondays)
            fig.autofmt_xdate()

            self.write(mpld3.fig_to_html(fig))

        else:
            self.render("www/layout/browser.html", title="Bloidozor data browser", _sql = _sql, parent=self)



######################################################################################################################
######################################################################################################################
########
######################################################################################################################
######################################################################################################################


class DBreader(web.RequestHandler):
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

            print from_date, to_date
        else:
            self.render("www/layout/DBreader/mainpage.html", title="DBreader", _sql=_sql, parent=self, argv = self.get_argument)



class AstroTools(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
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
                _sql("UPDATE station SET handler = '" + str(self)+"' WHERE name='"+jsonstation['ident']+"';")
            elif m_type == "event":
                print "type event", message
                query = _sql("SELECT name FROM station WHERE handler = '"+str(self)+"';")[0]
                print "EVENT", query[0]
                for client in cl:
                    client.write_message(u"$meta;" + str(query[0])+ ";" +"{message}")
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
        (r'/map(.*)', RTbolidozor),
        (r'/map', RTbolidozor),
        (r'/browser(.*)', Browser),
        (r'/browser', DBreader),
        (r'/database(.*)', DBreader),
        (r'/database', Browser),
        (r'/astrotools(.*)', AstroTools),
        (r'/astrotools', AstroTools),
        (r'/zoo', ZooBolid),
        (r'/zoo(.*)', ZooBolid),
        (r"/auth/login/", AuthLoginHandler),
        (r"/auth/logout/", AuthLogoutHandler),
        (r"/auth/setting/", AuthSettingHandler),
        (r"/auth/new/(.*)", AuthNewHandler),
        (r"/auth/update/(.*)", AuthUpdateHandler),
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
