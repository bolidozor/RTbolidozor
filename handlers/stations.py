#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.escape
from tornado import web
from . import _sql, wwwCleanName
import time
import simplekml

import numpy as np

class station_kml(web.RequestHandler):
    #@tornado.web.asynchronous

    def get(self, name=None):
		self.set_header('Content-Type', 'text/xml')
		kml = simplekml.Kml()
		kml.document.name = "Bolidozor"


		for station in _sql("SELECT * FROM bolidozor_station INNER JOIN bolidozor_observatory ON bolidozor_observatory.id = bolidozor_station.observatory WHERE bolidozor_station.status < 90;"):  
			print station
			pnt = kml.newpoint(name=station['namesimple'], coords=[(station['lon'],station['lat'],station['alt'])])
			pnt.description = station['name']
			pnt.snippet.content = station['name']
			pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/target.png'
			pnt.style.iconstyle.color = 'ff0000ff'
			pnt.style.iconstyle.scale = 2
	
		for station in _sql("SELECT * FROM vo_servers;"):  
			print station
			pnt = kml.newpoint(name=station['namesimple'], coords=[(station['lon'],station['lat'],station['alt'])])
			pnt.description = station['name']+"<br><a href='%s'>%s</a>" %(station['url'], station['url'])
			pnt.snippet.content = station['name']
			pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_square.png'
			pnt.style.iconstyle.color = 'ff0000ff'
			pnt.style.iconstyle.scale = 2

		pnt = kml.newpoint(name="Graves radar", coords=[(5.5151,47.3480)])
		#pnt.description = station['name']+"<br><a href='%s'>%s</a>" %(station['url'], station['url'])
		#pnt.snippet.content = station['name']
		pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/star.png'
		pnt.style.iconstyle.color = 'ff0000ff'
		pnt.style.iconstyle.scale = 2


		#kml.save("botanicalgarden.kml")
		#print kml.kml(format = True)
		#self.clear()
		self.write(kml.kml(format = True))