#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.escape
from tornado import web
from tornado.concurrent import run_on_executor

from . import _sql
import time
import datetime
import os
import arrow
import json

class Timeline(web.RequestHandler):
    #@tornado.web.asynchronous
    def get(self, params=None):
        self.render('timeline.layout.hbs', title = "Timeline")

    def to_serializable(self, val):
        if isinstance(val, datetime.datetime):
            return val.isoformat()
        return str(val)

    #@run_on_executor
    def post(self, params=None):
        self.set_header('Content-Type', 'application/json')
        
        p_date = self.get_argument('date', None)
        p_time = self.get_argument('time', None)
        
        d_min = arrow.get(p_date+"T"+p_time)+ datetime.timedelta(minutes = -15)
        d_max = d_min + datetime.timedelta(minutes = 30+15) 

        print("Pozaduji data mezi", d_min, d_max)

        events = _sql("""
                SELECT bolidozor_fileindex.id as id, bolidozor_met.id as id_met, noise, peak_f, mag, duration, bolidozor_met.obstime, filepath as path,
                filename, file, id_observer, bolidozor_observatory.namesimple as observatory_namesimple FROM `bolidozor_met`
                JOIN bolidozor_fileindex ON bolidozor_fileindex.id = bolidozor_met.file
                JOIN bolidozor_station ON bolidozor_station.id = bolidozor_fileindex.id_observer
                JOIN bolidozor_observatory ON bolidozor_observatory.id = bolidozor_station.observatory
                WHERE bolidozor_met.obstime BETWEEN '%s' AND '%s'
                ORDER BY bolidozor_met.obstime;
            """ %(d_min.isoformat()[:19], d_max.isoformat()[:19]) )
        stations = set()
        for event in events:
            stations.add(event['id_observer'])
        #print(events)
        self.write(json.dumps({'stations': list(stations), 'events': events}, default=self.to_serializable))
        #self.write("HI")