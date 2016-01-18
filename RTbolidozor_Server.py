#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
from tornado import web
from tornado import ioloop
from tornado import websocket
import json
import sqlite3
import time
import datetime

cl = []
fits={'ZVPP-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/ZVPP/ZVPP-R3/meteors/',
     'OBSUPICE-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/OBSUPICE/OBSUPICE-R4/meteors/',
     'OBSUPICE-R4':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/OBSUPICE/OBSUPICE-R4/meteors/',
     'SVAKOV-R6':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/svakov/SVAKOV-R6/meteors/',
     'ZEBRAK-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/ZEBRAK/ZEBRAK-R3/meteors/',
     'NACHODSKO-R3':'http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/nachodsko/NACHODSKO-R3/meteors/'}

js9={'ZVPP-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/ZVPP/ZVPP-R3/meteors',
     'OBSUPICE-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/OBSUPICE/OBSUPICE-R4/meteors',
     'OBSUPICE-R4':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/OBSUPICE/OBSUPICE-R4/meteors',
     'SVAKOV-R6':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/svakov/SVAKOV-R6/meteors',
     'ZEBRAK-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/ZEBRAK/ZEBRAK-R3/meteors',
     'NACHODSKO-R3':'http://space.astro.cz/bolidozor/support/js9browser/#/bolidozor/nachodsko/NACHODSKO-R3/meteors'}


def _sql(query):
        dbPath = 'bolid.db'
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

class IndexHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, addres=None):
        self.render("index.html")

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
            month = datetime.datetime.utcnow().strftime('%Y%m')
        date_from = str(month[0:4]+month[5:7]+"00000000000")
        date_to  =  str(month[0:4]+str(int(month[5:7])+1).zfill(2)+"00000000000")
        #print date_from, date_to
        #print "webM", params, self.get_argument('month', None)
        items = ["Item 1", "Item 2", "Item 3"]
        event = _sql("SELECT rowid, * FROM meta WHERE meta.link != 0 AND meta.time > "+date_from+" AND meta.time <"+date_to+" GROUP BY meta.link ORDER BY meta.time DESC ")     # seznam jedtotlivých událostí
        query = _sql("SELECT rowid, * FROM meta WHERE meta.link != 0 AND meta.time > "+date_from+" AND meta.time <"+date_to+" ORDER BY meta.time DESC")                         # seznam vsech udalosti
        self.render("www/layout/MultiBolid.html", title="Bloidozor multi-bolid database", range=[date_from, date_to], data=[event, query], _sql = _sql, _sqlWeb = _sqlWeb, links=[fits, js9], parent=self)

class RTbolidozor(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        self.render("www/layout/realtime_layout.html", title="Bloidozor multi-bolid database", _sql = _sql, _sqlWeb = _sqlWeb, links=[fits, js9], parent=self)

class WebHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, addres=None):
        print "web", addres
        self.render("www/layout/index.html", title="My title")

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
            elif m_type == "midi":
                station = [ i for i in self.StationList if i[0] == self ][0][1]
                print "stanice je: ", station
                for client in cl:
                    client.write_message(u"Na stanici:"+station+ m_type +" -- " + message)
            elif m_type == "stanica":
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
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '.'}),
    (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
    (r"/(.*\.png)", tornado.web.StaticFileHandler,{"path": './www/media/' }),
    (r"/(.*\.jpg)", tornado.web.StaticFileHandler,{"path": './www/media/' }),
    (r"/(.*\.css)", tornado.web.StaticFileHandler,{"path": './www/css/' }),
    (r"/(.*\.wav)", tornado.web.StaticFileHandler,{"path": './www/wav/' }),
   #(r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
    (r"/(.*)", WebHandler),
], debug=True, autoreload=True)

def main():
    app.listen(5252)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()