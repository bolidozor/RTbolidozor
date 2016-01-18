#!/usr/bin/python
# -*- coding: utf-8 -*-

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

    def sendEvent(self):
        self.send("$event;"+str('{}')+";")



def main():
    client = mWS()
    client.connect("ws://62.77.113.30:5252/ws")
    client.setStation('{"name":"TEST","ident":"TEST-R3","lat":50,"lon":15, "prew":"http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/ZVPP/ZVPP-R3/", "space":"http://space.astro.cz/bolidozor/ZVPP/ZVPP-R3/"}')
    while True:
        time.sleep(3)
        client.sendEvent()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exitapp = True
        raise 0