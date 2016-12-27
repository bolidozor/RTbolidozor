#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.escape
from tornado import web
from . import _sql, wwwCleanName
import time
import os
import pickle
import mpld3
from mpld3 import plugins, utils
from matplotlib.dates import MONDAY
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter

import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl

class Browser(web.RequestHandler):
    @tornado.web.asynchronous

    def calc_colour(self, val):
        if self.color == 1:
            if val < self.maxVal/3:    #    0/3 ... 1/3
                red = 0
                green = val*3.0 * 255.0/self.maxVal
                blue = 255

            elif val < self.maxVal/3*2:    #    1/3 ... 2/3
                red = 0
                green = 255
                blue = (self.maxVal*3.0 - val*3.0) * 255.0/self.maxVal - 254

            elif val < self.maxVal:                               #    2/3 ... 3/3
                red = val*3 * 255.0/self.maxVal
                green = (self.maxVal*3.0 - val*3.0)*255.0/self.maxVal
                blue = 0

            else:
                red = 100
                green = 100
                blue = 100
        else:
            red = val*255/self.maxVal
            green = val*255/self.maxVal
            blue = val*255/self.maxVal
        return "rgb(%i,%i,%i)"%(int(red), int(green), int(blue))

    def get(self, params=None):
        print "######################33"
        print params
        pwr_start_time = time.time()
        d_month = self.get_argument('month', 'last')

        self.maxVal = int(self.get_argument('max', 10))
        self.color = int(self.get_argument('color', 1))
        height = int(self.get_argument('height', 250))-20
        width = int(self.get_argument('width', 700))
        step = int(self.get_argument('step', 0))
        print params, d_month

        d = params.split('/')

        if 'plotJS' in params:
            path = "tmp/plotJS_%s.pickle" %(d[2])
            if not os.path.exists(path) or os.path.getatime(path) < time.time()-5*60:
            #if True:
    

                print params, d
                if d[2] == 'all':
                    counts = np.array(_sql("SELECT MONTH(obstime) as m,DAY(obstime) as d, HOUR(obstime) as h, count(*) FROM bolidozor_v_met WHERE MONTH(obstime) = MONTH(CURDATE()) GROUP BY m, d, h ORDER BY obstime;", True))
                else:
                    id_station = _sql("SELECT id FROM bolidozor_station WHERE namesimple = '%s'" %(d[2]), db="MLABvo")[0][0]
                    counts = np.array(_sql("SELECT MONTH(obstime) as m,DAY(obstime) as d, HOUR(obstime) as h, count(*) FROM bolidozor_v_met WHERE MONTH(obstime) = MONTH(CURDATE()) and id_observer = '%s' GROUP BY m, d, h ORDER BY obstime;" %(id_station), True))
                

                data = np.zeros((24,32))
                for x in counts:
                    data[x[2],x[1]] = x[3]

                fig = plt.figure()
                ax = fig.add_subplot(111)
                cmap = plt.cm.jet
                cmap.set_under('#FAFAFA', 1)
                norm = mpl.colors.Normalize(vmin=1, vmax=np.amax(data))
                img = ax.imshow(data, cmap=cmap, interpolation='nearest', aspect='auto', norm=norm)
                
                plt.colorbar(img)
                plt.tight_layout()

                fig.autofmt_xdate()
                pickle.dump(fig, open(path, 'wb'))

            else:
                print "Loading PICKLE"
                fig = pickle.load(open(path, 'rb'))
            
            self.write(mpld3.fig_to_html(fig))

        elif "yeartrend" in params:
            path = "tmp/yeartrend_%s.pickle" %(d[2])
            if not os.path.exists(path) and os.path.getatime(path) < time.time()-5*60:
            #if True:

                #now = datetime.datetime.utcnow()
                

                if d[2] == 'all':
                    #print "aaa", float(date_from), float(date_to)
                    counts = np.array(_sql("SELECT DAYOFYEAR(obstime) as d, count(*) FROM bolidozor_v_met WHERE YEAR(obstime) = YEAR(CURDATE()) GROUP BY d ORDER BY obstime;", True, db="MLABvo"))
                else:
                    id_station = _sql("SELECT id FROM bolidozor_station WHERE namesimple = '%s'" %(d[2]), db="MLABvo")[0][0]
                    counts = np.array(_sql("SELECT DAYOFYEAR(obstime) as d, count(*) FROM bolidozor_v_met WHERE YEAR(obstime) = YEAR(CURDATE()) and id_observer = '%s' GROUP BY d ORDER BY obstime;" %(id_station), True, db="MLABvo"))

                print counts
                counts = np.rot90(counts)
                print counts

                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.plot(counts[1], counts[0])
                ax.set_xlim([0,366])
                cmap = plt.cm.jet
                cmap.set_under('#FAFAFA', 1)
                plt.tight_layout()
                ax.grid(color='white', linestyle='solid')
                #ax.xaxis.set_major_locator(months)
                #ax.xaxis.set_major_formatter(monthsFmt)
                #ax.xaxis.set_minor_locator(mondays)
                fig.autofmt_xdate()
                pickle.dump(fig, open(path, 'wb'))

            else:
                print "Loading PICKLE"
                fig = pickle.load(open(path, 'rb'))

            self.write(mpld3.fig_to_html(fig))

        elif "yearduration" in params:
            path = "tmp/yearduration.pickle"
            #if not os.path.exists(path) and os.path.getatime(path) < time.time()-5*60:
            if True:
            

                counts = np.array(_sql("SELECT obstime, duration FROM bolidozor_v_met WHERE YEAR(obstime) = YEAR(CURDATE());", True, db="MLABvo"))
               
                counts = np.rot90(counts)
                print counts

                fig = plt.figure()
                ax = fig.add_subplot(111)
                cmap = plt.cm.jet
                cmap.set_under('#FAFAFA', 1)
                plt.tight_layout()
                ax.plot(counts[1], counts[0], 'bx')
                #ax.set_xlim([0,366])
                #ax.grid(color='white', linestyle='solid')
                #ax.xaxis.set_major_locator(months)
                #ax.xaxis.set_major_formatter(monthsFmt)
                #ax.xaxis.set_minor_locator(mondays)
                fig.autofmt_xdate()
                pickle.dump(fig, open(path, 'wb'))

            else:
                print "Loading PICKLE"
                fig = pickle.load(open(path, 'rb'))

            self.write(mpld3.fig_to_html(fig))
            

        else:
            self.render("count.hbs", title="Bolidozor | meteor counts", _sql = _sql, parent=self)

