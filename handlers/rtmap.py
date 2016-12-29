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

cl = []

class SocketHandler(websocket.WebSocketHandler):
    
    def check_origin(*args, **kwargs):
        return True

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
        print "MESSAGE>>", message
        self.write_message(u"ACK")
        try:
            if message[0] == "$":
                m_type = message[1:message.find(";")]
                if m_type == "HI":
                    self.StationList.append([self] + message[message.find(";")+1:].split(";") )
                    print "type: HI", self.StationList
                elif m_type == "stanica" or  m_type == "stanice":       # inicializacializacni sprava od stanice (obsahoje o sobe informace)
                    jsonstation = json.loads(message.split(";")[1])
                    print "type stanica", jsonstation['name']
                    _sql("UPDATE bolidozor_station SET RTbolidozor = '" + str(self)+"' WHERE namesimple='"+jsonstation['name']+"';")
                elif m_type == "event":
                    print "type event", message
                    query = _sql("SELECT namesimple FROM bolidozor_station WHERE RTbolidozor = '"+str(self)+"';")[0]
                    print "EVENT", query
                    for client in cl:
                        client.write_message(u"$meta;" + str(query[0])+ ";" +"{message}")
            elif message[0] == '#':
                print "multicast"
                for client in cl:
                    client.write_message(u"multicast: " + message)
            else:
                print "Prijata zprava: ", message
                pass
        except Exception, e:
            print "ERROR1>>",e