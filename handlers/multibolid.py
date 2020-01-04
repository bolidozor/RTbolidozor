#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.escape
from tornado import web
from . import _sql
import time
import datetime
import os

class MultiBolid(web.RequestHandler):
    #@tornado.web.asynchronous
    def get(self, params=None):


        test = _sql('''
            SELECT
                min(bolidozor_met_match.id) as id,
                bolidozor_met_match.match_id as match_id,
                min(bolidozor_met.obstime) as obstime
            FROM bolidozor_met_match
                LEFT JOIN bolidozor_met ON bolidozor_met.id = bolidozor_met_match.met_id
            GROUP BY bolidozor_met_match.match_id
            ORDER BY min(bolidozor_met.obstime) DESC LIMIT 10;''')
        print(test)


        month = self.get_argument('month', None)
        page = int(self.get_argument('page', 1))
        per_page = int(self.get_argument('per_page', 50))
        #if not month:
        #    self.redirect('/multibolid/?month=%s' %datetime.datetime.utcnow().strftime('%Y-%m'))
        if params: MBtype = params.split('/')
        else: MBtype = []
        if len(MBtype) <= 1:
            if not month:
                date_from = datetime.date.today().replace(day=1).isoformat()
                #date_from = time.mktime(time.strptime(month, "%Y-%m")).isoformat()
                #date_to  =  time.mktime(time.strptime(month, "%Y-%m"))+60*60*24*30
                date_to = datetime.datetime.utcnow().isoformat()
                print("NM", month, date_from, date_to)
            elif month == "all":
                date_from = 0
                date_to = datetime.datetime.now().isoformat()
                print("Al", month, date_from, date_to)
            else:
                date_from = datetime.datetime.strptime(month, "%Y-%m").isoformat()
                date_to  =  (datetime.datetime.strptime(month, "%Y-%m")+datetime.timedelta(days=30))
                print("DA", month, date_from, date_to)
            #date_from = (datetime.datetime.utcnow()-datetime.timedelta(days = 60)).isoformat()
            #date_to = datetime.datetime.utcnow().isoformat()
            self.render("multiBolid.hbs", title="Bolidozor | multi-bolid database", range=[date_from, date_to], _sql = _sql, parent=self, page=page, per_page=per_page)
        else:
            if MBtype[1]=="event":
                print("EVENT FOR ")
                id_event = int(MBtype[2])
                compare_img = os.path.exists('/storage/bolidozor/indexer/multibolid/compare/multibolid_%s.png' %(id_event))
                self.render("multiBolidDetail.hbs", title="Bolidozor | multi-bolid database | EVENT", data=[id_event], _sql = _sql, parent=self, compare_img=compare_img, page=page, per_page=per_page)

class ShowSelected(web.RequestHandler):
    def get(self, params = None):

        ids = set(self.get_arguments('id'))
        where_query = ', '.join(ids)
        print(where_query)
        events = _sql("SELECT id as met_id, file_id as id, noise, peak_f, mag, duration, obstime, filepath as path, filename, filename_original, id_observer, namesimple, station_name FROM MLABvo.bolidozor_v_met WHERE id IN (%s) LIMIT 200;"%(where_query), True)
        print(events)

        self.render("around.hbs", title="Bolidozor | compare", data = events, parent = self, search = False)
        
