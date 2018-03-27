#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.escape
from tornado import web
from . import _sql, wwwCleanName
import time
import os
import os.path
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
    #@tornado.web.asynchronous

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
        print "######################"
        print params
        pwr_start_time = time.time()
        d_month = self.get_argument('month', 'last')

        self.maxVal = int(self.get_argument('max', 10))
        self.color = int(self.get_argument('color', 1))
        height = int(self.get_argument('height', 250))-20
        width = int(self.get_argument('width', 700))
        step = int(self.get_argument('step', 0))
        print params, d_month

        self.render("count.hbs", title="Bolidozor | meteor counts", _sql = _sql, parent=self, multicount = open("/home/roman/repos/RTbolidozor/static/multicounts.svg").read())

        '''
        if params:
            d = params.split('/')

            if 'plotJS' in params:
                try:
                    #path = "tmp/plotJS_%s.pickle" %(d[2])
                    path_img = "/static/graphs/plotJS_%s.svg" %(d[2])
                    print "Loading PICKLE"
                    #fig = pickle.load(open(path, 'rb'))
                    #self.write(open(path_img, 'rb'))
                    self.write(path_img)

                except Exception, e:
                    self.write("Err - pickle missing")

            elif "yeartrend" in params:
                try:
                    #path = "tmp/yeartrend_%s.pickle" %(d[2])
                    path_img = "/static/graphs/yeartrend_%s.svg" %(d[2])
                    print "Loading PICKLE"
                    #fig = pickle.load(open(path, 'rb'))
                    self.write(open(path_img, 'rb'))

                except Exception, e:
                    self.write("Err - pickle missing")

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

        '''


class intensity(web.RequestHandler):    

    def get(self, name = None):
        stations = _sql("SELECT id, name, namesimple FROM MLABvo.bolidozor_station where status < 10;")

        self.render("count.intensity.hbs", title="Bolidozor | meteor intensity", stations = stations)

