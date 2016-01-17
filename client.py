
#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import datetime

import jack
import websocket
import thread



class mWS2():

    def __init__(self):
        self.ws = websocket.WebSocketApp("ws://62.77.113.30:5252/ws",
                              on_message = self.on_message,
                              on_error = self.on_error,
                              on_close = self.on_close,
                              on_open = self.on_open)

    def on_message(self, message):
        print("message: ", message)


    def on_error(self, error):
        print("error: ", error)


    def on_close(self):
        print("### closed ###")


    def on_open(self):
        self.send("AOEoe")
        print "opened"
        def run(*args):
            for i in range(3):
                # send the message, then wait
                # so thread doesnt exit and socket
                # isnt closed
                self.send("Hello %d" % i)
                time.sleep(1)


        thread.start_new_thread(run, ())



class mWS(websocket.WebSocket):

    def on_message(self, message):
        print("message: ", message)


    def on_error(self, error):
        print("error: ", error)


    def on_close(self):
        print("### closed ###")


    def on_open(self):
        self.send("AOEoe")
        print "opened"
        def run(*args):
            for i in range(3):
                # send the message, then wait
                # so thread doesnt exit and socket
                # isnt closed
                self.send("Hello %d" % i)
                time.sleep(1)


        thread.start_new_thread(run, ())


class mWS3(websocket.WebSocketApp):

    def setCallback(self):
        self.on_message = self.Mon_message
        self.on_open = self.Mon_open

    def on_message(self, message):
        print("message: ", message)

    def Mon_message(self, message):
        print("message: ", message)


    def on_error(self, error):
        print("error: ", error)


    def on_close(self):
        print("### closed ###")


    def on_open(self):
        self.send("AOEoe")
        print "opened"
        def run(*args):
            for i in range(3):
                # send the message, then wait
                # so thread doesnt exit and socket
                # isnt closed
                self.send("Hello %d" % i)
                time.sleep(1)

        thread.start_new_thread(run, ())


    def Mon_open(self):
        self.send("AOEoe")
        print "opened"
        def runb(*args):
            for i in range(3):
                # send the message, then wait
                # so thread doesnt exit and socket
                # isnt closed
                self.send("Hello %d" % i)
                time.sleep(1)

        thread.start_new_thread(runb, ())




def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print "port opened"
    ws.send("HI;ZVPP;ZVPP-R2;N;;E;;")

def midi_process(frames):
    try:
        for offset, data in Jport.incoming_midi_events():
            midiTime = datetime.datetime.utcnow()
            print (offset, str(midiTime), data)
            try:
                OutData = str(""+str(midiTime)+";"+str(offset)+";"+str(data)+";").decode('utf-8', errors='ignore')
                if ws.connected:
                    print "Odchozi data:", OutData
                    ws.send(OutData)
                else:
                    pass

            except Exception, e:
                print e

    except Exception, e:
        print e
    finally:
        return jack.CALL_AGAIN


class RTbolidozorClient(object):
    def __init__(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp("ws://62.77.113.30:5252/ws",
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close,
                                on_open = self.on_open)

    def on_message(self, ws, message):
        print "message: ", message

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        print "### closed ###"

    def on_open(self, ws):
        print "opened"
        ws.send("HI;ZVPP;ZVPP-R2;N;;E;;")

    def send(self, data):
        self.ws.send(str(data).decode('utf-8', errors='ignore'))

    def JackInit(self):
        self.Jclient = jack.Client("RTbolidozorSender")
        self.Jport = self.Jclient.midi_inports.register("RTbolidozor_1")
        self.Jclient.set_process_callback(self.midi_process)
        self.Jclient.activate()

    def midi_process(self, frames):
        try:
            for offset, data in self.Jport.incoming_midi_events():
                midiTime = datetime.datetime.utcnow()
                print (offset, str(midiTime), data)
                try:
                    OutData = str(""+str(midiTime)+";"+str(offset)+";"+str(data)+";").decode('utf-8', errors='ignore')
                    #if ws.connected:
                    print "Odchozi data:", OutData
                    self.ws.send(OutData)
                    #else:
                    #    pass

                except Exception, e:
                    print "chyba midi_process #1:", e

        except Exception, e:
            print e
        finally:
            return jack.CALL_AGAIN


if __name__ == "__main__":
    
    #websocket.enableTrace(False)
    while True:
        ws = RTbolidozorClient()
        ws.JackInit()
        ws.ws.run_forever()
        del ws
        time.sleep(15000)
        #ws.connect("ws://62.77.113.30:5252/ws")

