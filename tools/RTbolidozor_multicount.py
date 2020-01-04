#!/usr/bin/python3
# -*- coding: utf-8 -*-


##
##
#
# Software pro vygenerovani multicounts histogramu
# Melo by to byl spousteno z cronu
#
# @reboot python /home/roman/repos/RTbolidozor/bolidFinder.py | tee /home/roman/RTbolidozorCron.log
#
# zatim jen takto, protoze jeste program neumi periodicke spousteni...
# /5 * * * * /home/roman/repos/RTbolidozor/bolidFinder.py | tee /home/roman/RTbolidozorCron.log
##
##

import MySQLdb as mdb
import pymysql.cursors
import time
import csv
import pyfits
import time
import math

from datetime import datetime, timedelta, date
import xml.etree.cElementTree as ET


def _sql(query, read=False, db="MLABvo"):
        connection = pymysql.connect(host="localhost", user="root", passwd="root", db=db, use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        try:
            cursorobj = connection.cursor()
            result = None
            cursorobj.execute(query)
            result = cursorobj.fetchall()
            if not read:
                connection.commit()
        except Exception as e:
                print("Err", e)
        connection.close()
        return result


class RTbolidozorCounts():
    def __init__(self):
        print("Generovani Multicounts grafu")
        stanice =  _sql("SELECT id, name, namesimple FROM MLABvo.bolidozor_station where status < 10;")
        
        print("dobre stanice, ktere budou analyzovany", stanice)
        self.plotMultiCounts(stanice, dnu=40)
        for station in stanice:
            try:
                self.plotIntensity(station = station, dnu = 40)
            except Exception as e:
                print(e)
            pass

    def rgb(self, minimum, maximum, value, hex = False):
        minimum, maximum = float(minimum), float(maximum)
        ratio = 2 * (value-minimum) / (maximum - minimum)
        b = int(max(0, 255*(1 - ratio)))
        r = int(max(0, 255*(ratio - 1)))
        g = 255 - b - r
        if hex:
            return '%02x%02x%02x' % (r, g, b)
        return r, g, b

    def plotMultiCounts(self, stations, dnu):
        print("mam {} stanic.".format(len(stations)))
        print(stations)

        pole = int(math.ceil(math.sqrt(len(stations)))) # velikost ctverce pro jednu hodinu
        space_pole_hodina = 0   # mezera mezi poly znacici jednu hodinu
        sz_ctverec_stanice = 4
        sz_pole_hodina = pole*sz_ctverec_stanice+space_pole_hodina
        sz_zakl_pole_w = space_pole_hodina+(sz_pole_hodina+space_pole_hodina)*dnu
        sz_zakl_pole_h = space_pole_hodina+(sz_pole_hodina+space_pole_hodina)*24
        last_day = datetime.now()
        first_day =  (last_day - timedelta(days=dnu-1)).date()

        print("dnes je", datetime.now())
        print("poslední den je", last_day)
        print("první den je", first_day)

        print("pole bude velike", pole)
        print("pole pro hodinu bude velke", sz_pole_hodina)

        svg = ET.Element("svg", style="background-color:white; opacity: 1; font-size: 7pt;", viewBox="0 -10 %i %i" %(10+space_pole_hodina+dnu*(sz_pole_hodina+space_pole_hodina)+10, 10+space_pole_hodina+24*(sz_pole_hodina+space_pole_hodina)+10+90))
        group_header = ET.SubElement(svg, "g")
        group = ET.SubElement(svg, "g")
        group_meta = ET.SubElement(svg, "g", transform="translate(0, "+str(24*(sz_pole_hodina+space_pole_hodina)+40)+")")
        group_footer = ET.SubElement(svg, "g")

        ET.SubElement(group_meta, "rect", style="fill:#000000;",id="svg_legend_back", width=str(15*pole+space_pole_hodina+1), height=str(15*pole+space_pole_hodina+1), x=str(25), y=str(0))

        for d in range(dnu):
            #if d % 5 == 0 or d == dnu:
            ET.SubElement(group, "text", x=str(10+1+space_pole_hodina+d*(sz_pole_hodina+space_pole_hodina)), y=str(sz_zakl_pole_h+20)).text = str((last_day.date()-timedelta(days=dnu-d-1)).day)
            
            for h in range(24):
                #ET.SubElement(group, "rect", style="fill:#aaa;",id="svg_pole_hodina", width=str(sz_pole_hodina), height=str(sz_pole_hodina), x=str(10+space_pole_hodina+d*(sz_pole_hodina+space_pole_hodina)), y=str(10+space_pole_hodina+h*(sz_pole_hodina+space_pole_hodina)))
                ET.SubElement(group, "rect", style="fill:#000030;",id="svg_pole_hodina", width=str(sz_pole_hodina), height=str(sz_pole_hodina), x=str(10+space_pole_hodina+d*(sz_pole_hodina+space_pole_hodina)), y=str(10+space_pole_hodina+h*(sz_pole_hodina+space_pole_hodina)))
                #ET.SubElement(group, "rect", style="fill:#111;",id="svg_pole_hodina", width=str(sz_pole_hodina), height=str(sz_pole_hodina), x=str(10+space_pole_hodina+d*(sz_pole_hodina+space_pole_hodina)), y=str(10+space_pole_hodina+h*(sz_pole_hodina+space_pole_hodina)))

        for i, station in enumerate(stations):
            print("Generovani stanice", station)
            
            data = _sql("SELECT COUNT(id) as 'count', DATE(MAX(obstime)) as 'date', HOUR(obstime) as 'hour' FROM MLABvo.bolidozor_v_met WHERE id_observer = '%s' AND obstime > '%s' GROUP BY MONTH(obstime) , DAY(obstime) , HOUR(obstime);" %(station['id'], first_day))
            min, max = 0, 0
            print("pro stanici mam %s zaznamu." %(len(data)))

            
            for row in data:            # tento for pouze najde maximalni hodnotu
                if row['count']> max:
                    max = row['count']

            group_overlay = ET.SubElement(svg, "g", id="overlay_"+station['namesimple'], style='fill-opacity:0')
            for row in data:
                print("+", end="")
                sloupec = (row['date']-first_day).days
                offset_x = i//pole
                offset_y = i%pole
                #print row['count'], row['date'], sloupec, row['hour']
                r, g, b = self.rgb(0, max, row['count'])
                hexc = '%02x%02x%02x' % (r, g, b)
                ET.SubElement(group, "rect", style="fill:#%s;"%(hexc), name="svg_stanice_hodina", date=str(row['date']), width=str(sz_ctverec_stanice), height=str(sz_ctverec_stanice), x=str((sloupec)*(sz_pole_hodina+space_pole_hodina)+10+space_pole_hodina+space_pole_hodina/2+sz_ctverec_stanice*offset_x), y=str(row['hour']*(sz_pole_hodina+space_pole_hodina)+10+space_pole_hodina+space_pole_hodina/2+sz_ctverec_stanice*offset_y))
                ET.SubElement(group_overlay, "rect", style="fill:#%s;"%(hexc), name=station['namesimple']+"_hour", date=str(row['date']), width=str(sz_pole_hodina), height=str(sz_pole_hodina), x=str((sloupec)*(sz_pole_hodina+space_pole_hodina)+10+space_pole_hodina+space_pole_hodina/2), y=str(row['hour']*(sz_pole_hodina+space_pole_hodina)+10+space_pole_hodina+space_pole_hodina/2))
            print("")

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

        ET.SubElement(group_meta, "text", x="10", y="10").text = datetime.utcnow().strftime("%Y/%m/%d, %H:%M:%S UT")
        tree = ET.ElementTree(svg)
        tree.write("../static/multicounts.svg")

    def plotIntensity(self, station, dnu):
        print(station)
        last_day = datetime.now()
        first_day =  (last_day - timedelta(days=dnu-1)).date()

        height = 24*10  # rozmery pole s meteory
        width = 40*10
        optn = 50 # optimalni pocet binu za den

        data = _sql("SELECT obstime FROM MLABvo.bolidozor_v_met WHERE id_observer = '%s' AND obstime > '%s' ORDER BY obstime;" %(station['id'], first_day))
        bind = int(len(data)/(dnu*optn))
        if bind < 5: bind = 5

        svg = ET.Element("svg", style="background-color:white; opacity: 1; font-size: 7pt;", viewBox="0 0 %s %s" %(width, height+20))
        group_header = ET.SubElement(svg, "g")

        group2 = ET.SubElement(svg, "g", transform="translate(10, 20)", name="intensity_soft")
        group = ET.SubElement(svg, "g", transform="translate(10, 20)", name="intensity_sharp")
        #group_footer = ET.SubElement(svg, "g")

        #ET.SubElement(group_meta, "rect", style="fill:#000000;",id="svg_legend_back", width=str(50), height=str(50), x=str(25), y=str(0))
        ET.SubElement(group_header, "text", x=str(10), y=str(10)).text = "Station %s (%s)" %(station['id'], station['name']) 

        ys = height/(24*60*60.0)
        xs = (width-20)/dnu

        old_day = date(2000, 1,1)
        mint = 60*60
        maxt = 1
        grad_dict = {}


        data = data[0::bind]
        for x in range(len(data)-1):
            if data[x+1]['obstime'].date() == data[x]['obstime'].date():
                dlen = (data[x+1]['obstime'] - data[x]['obstime']).seconds
                if dlen < maxt: maxt = dlen
                if dlen > mint: mint = dlen

        for x in range(len(data)-1):
            dlen = (data[x+1]['obstime'] - data[x]['obstime']).seconds

            column = (data[x]['obstime'].date() - first_day).days
            midnight = data[x]['obstime'].replace(hour=0, minute=0, second=0, microsecond=0)
            row = (data[x]['obstime'] - midnight).total_seconds()
            row_p1 = (data[x+1]['obstime'] - midnight).total_seconds()
            h = abs(row - row_p1)

            if old_day != data[x]['obstime'].date():
                old_day = data[x]['obstime'].date()
                print("Novy den....", midnight)
                ET.SubElement(group2, "rect", style="fill:url(#grad_%s_col_%s)" %(station['id'], column), width=str(xs), height=str(height), x=str(xs*column), y=str(0))
                grad = ET.SubElement(svg, "linearGradient", id = "grad_%s_col_%s" %(station['id'], column), gradientUnits="userSpaceOnUse", gradientTransform="scale(1,%s)" %height, x1="0", y1="0", x2="0", y2="1")

            if data[x+1]['obstime'].date() == data[x]['obstime'].date():
                row_avg = (row + row_p1) /2
                color = self.rgb(mint, maxt, dlen, hex=True)

                ET.SubElement(grad, "stop", offset = str(row_avg/(24*60*60)), style="stop-color:#%s" %(color))                
                ET.SubElement(group, "rect", style="fill:#%s;"%( color ), name="stanice_bin", count = str(dlen), bin = str(bind), t1 = str(data[x]['obstime']), t2 = str(data[x+1]['obstime']),
                                width=str(xs), height=str(dlen*ys), x=str(xs*column), y=str(row*ys))


        ET.SubElement(group_header, "text", x=str(10), y=str(18)).text = "Bin size: %s met.,  generated at %s." %(bind, datetime.now())
        tree = ET.ElementTree(svg)
        tree.write("/storage/bolidozor/indexer/RTbolidozor/counts/intensity_%s.svg" %station['id'])


if __name__ == '__main__':
    RTbolidozorCounts()























































