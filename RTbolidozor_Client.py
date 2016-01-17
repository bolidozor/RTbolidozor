"""
import websocket

class HelloSocket(websocket.WebSocket):

    def on_open(self):
        self.write('hello, world')

    def on_message(self, data):
        print data

    def on_ping(self):
        print 'I was pinged'

    def on_pong(self):
        print 'I was ponged'

    def on_close(self):
        print 'Socket closed.'


ws = HelloSocket()
ws.connect("ws://62.77.113.30:5252/ws")
"""

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
        #self.send("$stanica;"+str(self.config))
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
        self.send("$event;"+str('{AAAAA}')+";")




class MidiToRTBolidozor(object):
    def __init__(self):
        self.connected = False

    def start(self):
        self.Jclient = jack.Client("RTbolidozorSender")
        self.Jport = self.Jclient.midi_inports.register("RTbolidozor_1")
        self.Jclient.set_process_callback(self.midi_process)
        self.Jclient.activate()

    def connectWS(self):
        print "Prodict"
        self.ws = websocket.WebSocketApp("ws://62.77.113.30:5252/ws",
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close)
        self.ws.connect()
        self.ws.on_open    = self.on_open
        self.connected=True
        #self.ws.run_forever()

    def test(self):
        pass
        #self.ws.send("AHOJ")

    def midi_process(self, frames):
        try:
            for offset, data in self.Jport.incoming_midi_events():
                midiTime = datetime.datetime.utcnow()
                print (offset, str(midiTime), data)
                try:
                    OutData = str(""+str(midiTime)+";"+str(offset)+";"+str(data)+";").decode('utf-8', errors='ignore')
                    if self.connected:
                        print "Odchozi data:", OutData
                        self.ws.send(OutData)
                    else:
                        self.connectWS()

                except Exception, e:
                    print e

        except Exception, e:
            print e
        finally:
            return jack.CALL_AGAIN

    def on_open(self):
        print "0"
        print "1"

    def on_message(self, data):
        print data

    def on_ping(self):
        print 'I was pinged'

    def on_pong(self):
        print 'I was ponged'

    def on_close(self):
        print 'Socket closed.'

    def on_error(self):
        print 'Socket closed.'


def main():
    client = mWS()
    client.connect("ws://62.77.113.30:5252/ws")
    client.setStation('{"name":"ZVPP","ident":"ZVPP-R3","lat":49.00001,"lon":14.543001, "prew":"http://meteor1.astrozor.cz/f.png?http://space.astro.cz/bolidozor/ZVPP/ZVPP-R3/", "space":"http://space.astro.cz/bolidozor/ZVPP/ZVPP-R3/"}')
    while True:
        time.sleep(3)
        client.sendEvent()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exitapp = True
        raise 0

'''
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://62.77.113.30:5252/ws",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = on_open)
    ws.run_forever()
'''