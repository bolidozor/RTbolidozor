#!/usr/bin/python
# -*- coding: utf-8 -*-


##
##
#
# Software pro vygenerovani multicounts histogramu
# Melo by to byl spousteno z cronu
#
# @reboot python /home/roman/repos/RTbolidozor/bolidFinder.py | tee /home/roman/RTbolidozorCron.log
#
##
##

import MySQLdb as mdb
import pymysql.cursors
import time
import datetime
import csv
import pyfits
import time
import math

from datetime import datetime, timedelta, date
import xml.etree.cElementTree as ET


def _sql(query, read=False, db="MLABvo"):
        print "#>", query
        connection = pymysql.connect(host="localhost", user="roman", passwd="Vibvoflar4", db=db, use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        try:
            cursorobj = connection.cursor()
            result = None
            cursorobj.execute(query)
            result = cursorobj.fetchall()
            if not read:
                connection.commit()
        except Exception, e:
                print "Err", e
        connection.close()
        return result


class RTbolidozorCounts():
    def __init__(self):
        print "Tvorba grafu"
        stanice =  _sql("SELECT id, name, namesimple FROM MLABvo.bolidozor_station where status < 10;")
        print "dobre stanice", stanice
        self.plotMultiCounts(stanice, dnu=40)

    def rgb(self, minimum, maximum, value):
        minimum, maximum = float(minimum), float(maximum)
        ratio = 2 * (value-minimum) / (maximum - minimum)
        b = int(max(0, 255*(1 - ratio)))
        r = int(max(0, 255*(ratio - 1)))
        g = 255 - b - r
        return r, g, b

    def plotMultiCounts(self, stations, dnu):
        print "mam tolik stanic:", 
        print len(stations)
        print stations

        pole = int(math.ceil(math.sqrt(len(stations)))) # velikost ctverce pro jednu hodinu
        space_pole_hodina = 0   # mezera mezi poly znacici jednu hodinu
        sz_ctverec_stanice = 4
        sz_pole_hodina = pole*sz_ctverec_stanice+space_pole_hodina
        sz_zakl_pole_w = space_pole_hodina+(sz_pole_hodina+space_pole_hodina)*dnu
        sz_zakl_pole_h = space_pole_hodina+(sz_pole_hodina+space_pole_hodina)*24
        last_day = datetime.now()
        first_day =  (last_day - timedelta(days=dnu-1)).date()

        print "dnes je", datetime.now()
        print "poslední den je", last_day
        print "první den je", first_day

        print "pole bude velike", pole
        print "pole pro hodinu bude velke", sz_pole_hodina

        svg = ET.Element("svg", style="background-color:white; opacity: 1; font-size: 7pt;", viewBox="0 -10 %i %i" %(10+space_pole_hodina+dnu*(sz_pole_hodina+space_pole_hodina)+10, 10+space_pole_hodina+24*(sz_pole_hodina+space_pole_hodina)+10+90))
        group_header = ET.SubElement(svg, "g")
        group = ET.SubElement(svg, "g")
        group_meta = ET.SubElement(svg, "g", transform="translate(0, "+str(24*(sz_pole_hodina+space_pole_hodina)+40)+")")
        group_footer = ET.SubElement(svg, "g")

        #ET.SubElement(group, "rect", style="fill:#ddd; stroke:#000000;",id="svg_obrys", width=str(sz_zakl_pole_w), height=str(sz_zakl_pole_h), x=str(10), y=str(10))
    #    ET.SubElement(group, "rect", style="fill:#555; stroke:#000000;",id="svg_obrys", width=str(sz_zakl_pole_w), height=str(sz_zakl_pole_h), x=str(10), y=str(10))
        #ET.SubElement(group, "rect", style="fill:#555; stroke:#000000;",id="svg_obrys", width=str(sz_zakl_pole_w), height=str(sz_zakl_pole_h), x=str(10), y=str(10))
        ET.SubElement(group_meta, "rect", style="fill:#000000;",id="svg_legend_back", width=str(15*pole+space_pole_hodina+1), height=str(15*pole+space_pole_hodina+1), x=str(25), y=str(0))

        for d in range(dnu):
            #if d % 5 == 0 or d == dnu:
            ET.SubElement(group, "text", x=str(10+1+space_pole_hodina+d*(sz_pole_hodina+space_pole_hodina)), y=str(sz_zakl_pole_h+20)).text = str((last_day.date()-timedelta(days=dnu-d-1)).day)
            
            for h in range(24):
                #ET.SubElement(group, "rect", style="fill:#aaa;",id="svg_pole_hodina", width=str(sz_pole_hodina), height=str(sz_pole_hodina), x=str(10+space_pole_hodina+d*(sz_pole_hodina+space_pole_hodina)), y=str(10+space_pole_hodina+h*(sz_pole_hodina+space_pole_hodina)))
                ET.SubElement(group, "rect", style="fill:#000030;",id="svg_pole_hodina", width=str(sz_pole_hodina), height=str(sz_pole_hodina), x=str(10+space_pole_hodina+d*(sz_pole_hodina+space_pole_hodina)), y=str(10+space_pole_hodina+h*(sz_pole_hodina+space_pole_hodina)))
                #ET.SubElement(group, "rect", style="fill:#111;",id="svg_pole_hodina", width=str(sz_pole_hodina), height=str(sz_pole_hodina), x=str(10+space_pole_hodina+d*(sz_pole_hodina+space_pole_hodina)), y=str(10+space_pole_hodina+h*(sz_pole_hodina+space_pole_hodina)))

        for i, station in enumerate(stations):
            print station
            data = _sql("SELECT COUNT(id) as 'count', DATE(MAX(obstime)) as 'date', HOUR(obstime) as 'hour' FROM MLABvo.bolidozor_v_met WHERE id_observer = '%s' AND obstime > '%s' GROUP BY MONTH(obstime) , DAY(obstime) , HOUR(obstime);" %(station['id'], first_day))
            min, max = 0, 0
            print("pro stanici mam %s zaznamu." %(len(data)))

            
            for row in data:            # tento for pouze najde maximalni hodnotu
                if row['count']> max:
                    max = row['count']

            group_overlay = ET.SubElement(svg, "g", id="overlay_"+station['namesimple'], style='fill-opacity:0')
            for row in data:
                print "+",
                sloupec = (row['date']-first_day).days
                offset_x = i//pole
                offset_y = i%pole
                #print row['count'], row['date'], sloupec, row['hour']
                r, g, b = self.rgb(0, max, row['count'])
                hexc = '%02x%02x%02x' % (r, g, b)
                ET.SubElement(group, "rect", style="fill:#%s;"%(hexc), name="svg_stanice_hodina", date=str(row['date']), width=str(sz_ctverec_stanice), height=str(sz_ctverec_stanice), x=str((sloupec)*(sz_pole_hodina+space_pole_hodina)+10+space_pole_hodina+space_pole_hodina/2+sz_ctverec_stanice*offset_x), y=str(row['hour']*(sz_pole_hodina+space_pole_hodina)+10+space_pole_hodina+space_pole_hodina/2+sz_ctverec_stanice*offset_y))
                ET.SubElement(group_overlay, "rect", style="fill:#%s;"%(hexc), name=station['namesimple']+"_hour", date=str(row['date']), width=str(sz_pole_hodina), height=str(sz_pole_hodina), x=str((sloupec)*(sz_pole_hodina+space_pole_hodina)+10+space_pole_hodina+space_pole_hodina/2), y=str(row['hour']*(sz_pole_hodina+space_pole_hodina)+10+space_pole_hodina+space_pole_hodina/2))
            print ""

            text_x = 100 * (i//3) + 100
            text_y = 5 + 10*(i%3)
            ET.SubElement(group_meta, "text", x=str(text_x), y=str(text_y)).text = "%s - %s" %(i+1, station['name'])

            legend_x = 30 + (i//pole)*15
            legend_y = 15*(i%pole)+13
            ET.SubElement(group_meta, "rect", style="fill:#ddd;",id="svg_legend", width=str(15), height=str(15), x=str(legend_x-3), y=str(legend_y-11))
            ET.SubElement(group_meta, "text", x=str(legend_x), y=str(legend_y)).text = str(i+1)
            ET.SubElement(group_meta, "rect", style="fill-opacity:0",id="svg_legend", onclick="showStation('%s')"%(station['namesimple']), width=str(15), height=str(15), x=str(legend_x-3), y=str(legend_y-11))

        eomX = str(sz_zakl_pole_w+10-last_day.day*(sz_pole_hodina+space_pole_hodina)-2)
        days_to_last = (last_day.date() - date(last_day.year, last_day.month, 1))
        eomX2 = str(sz_zakl_pole_w+10-(days_to_last.days+1)*(sz_pole_hodina+space_pole_hodina)-2)
        ET.SubElement(group, "line", x1=eomX, y1="0", x2=eomX, y2=str(sz_zakl_pole_h+20+10), style="stroke:rgb(255,200,200);stroke-width:4")
        ET.SubElement(group, "line", x1=eomX2, y1="0", x2=eomX2, y2=str(sz_zakl_pole_h+20+10), style="stroke:rgb(255,200,200);stroke-width:4")
        ET.SubElement(group, "text", x=str(float(eomX)+5), y=str(9)).text = str(date(last_day.year, last_day.month,  1))
        ET.SubElement(group, "text", x=str(float(eomX2)+5),y=str(9)).text = str(date(last_day.year, last_day.month,1))

        tree = ET.ElementTree(svg)
        tree.write("../static/multicounts.svg")



if __name__ == '__main__':
    RTbolidozorCounts()
