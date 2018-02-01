#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.escape
from tornado import web
from tornado import websocket
from . import _sql, wwwCleanName, BaseHandler
import json

class RTbolidozor(BaseHandler):
    @tornado.web.asynchronous
    def get(self, params=None):
        self.render("realtime.hbs", title="Bolidozor | Real-time map", _sql = _sql, parent=self, CleanName = wwwCleanName)

cl = set()

class MeteorRtHandler(BaseHandler):
    def get(self, params=None):
        global cl
        station=self.get_argument("station", "None")
        for client in cl:
            try:
                print client
                client.write_message(u"$met;" + station+ ";" +"{message}")
            except Exception as e:
                print e
        self.write("connected clients: "+str(len(cl)))

class SocketHandler(websocket.WebSocketHandler):
    connections = set()
    
    def check_origin(*args, **kwargs):
        return True

    def initialize(self):
        self.StationList = []

    def check_origin(self, origin):
        return True

    def open(self):
        global cl
        self.connections.add(self)
        print "Opened new port: ", self, self.connections
        for client in self.connections:
            client.write_message(u"New listener")
        cl.add(self)

    def on_close(self):
        self.connections.remove(self)
        global cl
        cl.remove(self)


    def on_message(self, message):
        print "MESSAGE>>", message
        self.write_message(u"ACK")
        try:
            if message[0] == "$":
                #m_type = message.split[";"][0]
                m_type = message[1:message.find(";")]
                print "m_type je:", m_type
                if m_type == "HI":
                    self.StationList.append([self] + message[message.find(";")+1:].split(";") )
                    print "type: HI", self.StationList
                elif  m_type == "stanice":
                    jsonstation = json.loads(message.split(";")[1])
                    print "typ stanice", jsonstation['name']
                    _sql("UPDATE bolidozor_station SET RTbolidozor = '" + str(self)+"' WHERE namesimple='"+jsonstation['name']+"';")
                elif m_type == "event":
                    msg_data =  message.split(';')
                    print "type event", message, msg_data
                    #query = _sql("SELECT namesimple FROM bolidozor_station WHERE RTbolidozor = '"+str(self)+"';")[0]
                    #print "EVENT", query
                    for client in self.connections:
                        client.write_message(u"$met;" + msg_data[1]+ ";" +"{message}")
            elif message[0] == '#':
                print "multicast"
                for client in self.connections:
                    client.write_message(u"multicast: " + message)
            else:
                print "Prijata zprava: ", message
                pass
        except Exception, e:
            print "ERROR1>>", repr(e)

    