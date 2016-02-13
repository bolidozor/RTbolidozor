#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# sudo apt-get install python-websocket
#

import sys
import time
import datetime
import websocket
import binascii

exitapp = False
met = False
metData = u""
midiTime = 0

class mWS(websocket.WebSocket):
    def on_connect(self):
        print "connected"
        self.connected=True

    def on_open(self):
        self.send("ahoj")

    def on_message(self, data):
        print data

    def on_ping(self):
        print 'I was pinged'

    def on_pong(self):
        print 'I was ponged'

    def on_close(self):
        print 'Socket closed.'

    def setStation(self, config):
        self.config=config
        self.send("$stanica;"+str(self.config)+";")

    def sendEvent(self, pipe = None):
        self.send("$event;"+str(pipe)+";")

    def sendInfe(self, info = None):
	self.send("$info;"+str(info)+";")

def main():
    client = mWS()
    client.connect("ws://62.77.113.30:5252/ws")
    client.setStation('{"name":"ZVPP","ident":"ZVPP-R4"}')
    client.sendEvent("mmm")
    while 1:
        print "-"
        pipe = sys.stdin.read(10)        
        if "met" in pipe:
            client.sendEvent(pipe)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exitapp = True
        raise 0
