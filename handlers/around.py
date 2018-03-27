#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.escape
from tornado import web
from . import _sql
import time
import datetime
import os
import arrow

class Around(web.RequestHandler):
    #@tornado.web.asynchronous
    def get(self, params=None):
        p_datetime = self.get_argument('datetime', None)
        p_date = self.get_argument('date', None)
        p_time = self.get_argument('time', None)
        p_delta = self.get_argument('delta', 120)

        if p_date and p_time:
            center_time = arrow.get(p_date+"T"+p_time)
            print(center_time.isoformat()[:19])
        elif p_datetime:
            center_time = arrow.get(p_datetime).naive
            print(center_time.isoformat()[:19])
        else:
            center_time = datetime.datetime.utcnow()

        d_min = center_time + datetime.timedelta(seconds=-float(p_delta))
        d_max = center_time + datetime.timedelta(seconds=float(p_delta))
    
        '''
{u'lastaccestime': datetime.datetime(2018, 2, 1, 2, 31, 13)
u'bolidozor_fileindex.id': 34118050
u'noise': 6.46515
u'peak_f': 26516.6
u'mag': 33.9979
u'indextime': datetime.datetime(2018, 2, 1, 1, 31, 25)
u'filepath': u'/storage/bolidozor/ddmtrebic/DDMTREBIC-R3/meteors/2018/02/01/01'
u'checksum': u'6df182d612916e0c123f394c65e4eb08'
u'bolidozor_fileindex.obstime': datetime.datetime(2018, 2, 1, 1, 31, 13)
u'uploadtime': datetime.datetime(2018, 2, 1, 1, 31, 13)
u'obstime': datetime.datetime(2018, 2, 1, 1, 30, 18)
u'filename': u'20180201013032034_DDMTREBIC-R3_met.fits'
u'filename_original': u'20180201013032034_DDMTREBIC-R3_met.fits'
u'file_raw': None
u'id_server': 1
u'id_observer': 27
u'file': 34118050
u'duration': 0.341333
u'id': 2690241}

        '''    
        if p_date and p_time:
            events = _sql("""
                SELECT bolidozor_fileindex.id as id, noise, peak_f, mag, duration, bolidozor_met.obstime, filepath as path,
                filename, filename_original, file, id_observer, bolidozor_observatory.namesimple as observatory_namesimple, bolidozor_station.name as station_name FROM `bolidozor_met`
                JOIN bolidozor_fileindex ON bolidozor_fileindex.id = bolidozor_met.file
                JOIN bolidozor_station ON bolidozor_station.id = bolidozor_fileindex.id_observer
                JOIN bolidozor_observatory ON bolidozor_observatory.id = bolidozor_station.observatory
                WHERE bolidozor_met.obstime BETWEEN '%s' AND '%s'
                ORDER BY bolidozor_met.obstime;
            """ %(d_min.isoformat()[:19], d_max.isoformat()[:19]) )
        else: events = None

        #print(events)

        self.render("around.hbs", title="Bolidozor | multi-bolid database | EVENT", data=events, target = center_time, parent=self)

        '''
        if params: MBtype = params.split('/')
        else: MBtype = []
        if len(MBtype) <= 1:
            if not month:
                date_from = datetime.date.today().replace(day=1).isoformat()
                #date_from = time.mktime(time.strptime(month, "%Y-%m")).isoformat()
                #date_to  =  time.mktime(time.strptime(month, "%Y-%m"))+60*60*24*30
                date_to = datetime.datetime.utcnow().isoformat()
                print "NM", month, date_from, date_to
            elif month == "all":
                date_from = 0
                date_to = datetime.datetime.now().isoformat()
                print "Al", month, date_from, date_to
            else:
                date_from = datetime.datetime.strptime(month, "%Y-%m").isoformat()
                date_to  =  (datetime.datetime.strptime(month, "%Y-%m")+datetime.timedelta(days=30))
                print "DA", month, date_from, date_to
            #date_from = (datetime.datetime.utcnow()-datetime.timedelta(days = 60)).isoformat()
            #date_to = datetime.datetime.utcnow().isoformat()
            self.render("multiBolid.hbs", title="Bolidozor | multi-bolid database", range=[date_from, date_to], _sql = _sql, parent=self, page=page, per_page=per_page)
        else:
            if MBtype[1]=="event":
                print "EVENT FOR "
                id_event = int(MBtype[2])
                compare_img = os.path.exists('/storage/bolidozor/indexer/multibolid/compare/multibolid_%s.png' %(id_event))
                self.render("multiBolidDetail.hbs", title="Bolidozor | multi-bolid database | EVENT", data=[id_event], _sql = _sql, parent=self, compare_img=compare_img, page=page, per_page=per_page)
        self.finish()   
        '''
        
        #self.write("Tohle jsou parametry: " + repr(events) )