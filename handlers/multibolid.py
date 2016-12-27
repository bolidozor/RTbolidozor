#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.escape
from tornado import web
from . import _sql
import time
import datetime

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
            self.render("multiBolid.hbs", title="Bolidozor | multi-bolid database", range=[date_from, date_to], _sql = _sql, parent=self)
        else:
            if MBtype[1]=="event":
                print "EVENT FOR "
                id_event = int(MBtype[2])
                self.render("multiBolidDetail.hbs", title="Bolidozor | multi-bolid database | EVENT", data=[id_event], _sql = _sql, parent=self)
