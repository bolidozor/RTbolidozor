#!/usr/bin/python
# -*- coding: utf-8 -*-


##
##
#
# Software pro roztztrideni dat v nove databazi MLAvo.... rozradi to soubory z tabulky 'bolidozor_fileindex' do tabulky met, snapshots atd .. u tabulky met to pri cteni fits souboru zapise jeho parametry.
# Melo by to byl spousteno z cronu
# vytvori grafy pro 'counts'
# a nasledne udela indexy jednotlivych souboru
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
#import paramiko
import time
import pandas as pd

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

'''
def _sql(query, read=False):
        #print "#>>>", query
        connection = mdb.connect(host="localhost", user="roman", passwd="Vibvoflar4", db="MLABvo", use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        cursorobj = connection.cursor()
        result = None
        try:
                cursorobj.execute(query)
                result = cursorobj.fetchall()
                if not read:
                    connection.commit()
        except Exception, e:
                print "Err", e
        connection.close()
        return result
'''

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




class RTbolidozorAnalyzer():
    def __init__(self):
        print "Tvorba grafu"
        self.stanice =  _sql("SELECT id, name, namesimple FROM MLABvo.bolidozor_station where status < 10;")
        print "dobre stanice", self.stanice
        #for x in xrange(1,100):
        while True:
            pass
            #for station in self.stanice:
            #    self.plotYearTrend(station)
            self.indexProjectFiles()
            time.sleep(10)


    def plotYearTrend(self, station):
            # station is array in form [id, namesimple, name, ...]
        try:
            counts = np.array(_sql("SELECT DAYOFYEAR(obstime) as d,  count(obstime) as c FROM bolidozor_v_met WHERE YEAR(obstime) = YEAR(CURDATE()) and id_observer = '%s' GROUP BY d ORDER BY MIN(obstime);" %(station['id']), True))

            path_img = "/home/roman/repos/RTbolidozor/static/graphs/yeartrend_%s.svg" %(station['namesimple'])
            counts = pd.DataFrame.from_records(counts)

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(counts['d'], counts['c'])
            ax.set_xlim([0,366])
            cmap = plt.cm.jet
            cmap.set_under('#FAFAFA', 0)
            plt.tight_layout()
            ax.grid(color='white', linestyle='solid')
            fig.autofmt_xdate()
            plt.savefig(path_img)
            plt.close()
            print  "dokoncen %s graf" %(path_img)
        except Exception, e:
            print e, path_img
        

    def indexProjectFiles(self):
        start_time = time.time()
        print "zacatek indexProjectFiles"

        connection = pymysql.connect(host="localhost", user="roman", passwd="Vibvoflar4", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        cur = connection.cursor()


        cur.execute("SELECT * FROM bolidozor_fileindex WHERE indextime < '2000-01-01 00:00:00' AND uploadtime > '2017-00-00 00:00:00' ORDER BY id DESC LIMIT 1000;")
        #cur.execute("SELECT * FROM bolidozor_fileindex WHERE indextime < '2000-01-01 00:00:00' AND uploadtime > '2017-08-00 00:00:00' and filename_original NOT LIKE '%snap%' ORDER BY id DESC LIMIT 3000;")
        #cur.execute("SELECT * FROM bolidozor_fileindex ORDER BY id DESC LIMIT 5000")
        #cur.execute("SELECT * FROM bolidozor_fileindex WHERE indextime < '2000-01-01 00:00:00' AND filename_original LIKE '%HFN%' ORDER BY id DESC LIMIT 50000;")
        data = cur.fetchall()
        rowlen = len(data)
        print "mam data:", len(data)
        for rownum, row in enumerate(data):
            print rownum, '/', rowlen
            try:

                if '.fits' in row['filename_original']:
                    if 'snap.' in row['filename_original']:
                        print 'snap', row['filename_original']
                        
                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = CURRENT_TIMESTAMP WHERE id = '%s';" %(row['id']))

                        if row['id_server'] == 1: # je to ulozeno na space?
                        #    pass
                            ##snap = self.space_astro.file(row['filepath']+'/'+row['filename_original'])
                            snap = row['filepath']+'/'+row['filename_original']
                            hdulist = pyfits.open(snap)  # open a FITS file
                            prihdr = hdulist[1].header           # the primary HDU header
                            #sechdr = hdulist[1].header           # the primary HDU header

                            file_length = 60
                            file_length = prihdr['NAXIS2']*prihdr['CDELT2']/1000.0
                            obstime = datetime.datetime.strptime(prihdr['DATE'] , "%Y-%m-%dT%H:%M:%S")-datetime.timedelta(seconds=file_length)
                            orgin = prihdr['ORIGIN']
                            print obstime, orgin, file_length


                        #obstime = datetime.datetime.strptime(row['filename'].split('_')[0][:14], '%Y%m%d%H%M%S')
                        cur.execute("REPLACE INTO `MLABvo`.`bolidozor_snapshot` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                        #_sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        

                    elif 'met.' in row['filename_original']:
                        print "meteor", row['filename_original']
                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        #print "update DONE"
                        
                        if row['id_server'] == 1: # je to ulozeno na space?
                            #hdulist = pyfits.open(self.space_astro.file(row[5]+'/'+row['filename_original']))  # open a FITS file
                            hdulist = pyfits.open(row['filepath']+'/'+row['filename_original'].replace('met', 'raws'))  # open a FITS file
                            print hdulist
                            prihdr = hdulist[0].header           # the primary HDU header
                            #sechdr = hdulist[1].header           # the primary HDU header

                            obstime =  datetime.datetime.strptime(prihdr['DATE'], "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(seconds=prihdr['NAXIS2']*1/96000)
                            orgin =  prihdr['ORIGIN']
                            print obstime, prihdr['DATE'], orgin
                            
                        print "######################################################"
                        print ("REPLACE INTO `MLABvo`.`bolidozor_met` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                        cur.execute("REPLACE INTO `MLABvo`.`bolidozor_met` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        
                        print " "

                    elif 'raws.' in row['filename_original']:
                        print 'raw', row['filename_original']

                        if row['id_server'] == 1: # je to ulozeno na space?
                            hdulist = pyfits.open(row['filepath']+'/'+row['filename_original'])  # open a FITS file
                            prihdr = hdulist[0].header           # the primary HDU header

                            obstime =  datetime.datetime.strptime(prihdr['DATE'], "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(seconds=prihdr['NAXIS2']*1/96000)
                            orgin =  prihdr['ORIGIN']
                            print obstime, prihdr['DATE'], orgin

                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP(), obstime = '%s' WHERE id = '%s';" %(obstime, row['id']))
                        pass
                elif '.csv' in row['filename_original']:
                    print 'csv', row['filename_original']

                    if 'meta' in row['filename_original']:
                        
                        if row['id_server'] == 1: # je to ulozeno na space?
                            #meta = self.space_astro.file(row[5]+'/'+row['filename_original'])
                            meta = row['filepath']+'/'+row['filename_original']

                            try:
                                with open(meta, 'rb') as csvfile:
                                    meteors = csv.reader(csvfile)
                                    #print meteors
                                    print "==============================================================================="
                                    for meteor in meteors:
                                        if 'met' in meteor[0]:
                                            meteor = meteor[0].split(';')
                                            print meteor
                                            cur.execute("UPDATE `MLABvo`.`bolidozor_v_met` SET noise = '%s', peak_f = '%s', mag = '%s', duration = '%s' WHERE filename_original = '%s';" %(meteor[1], meteor[2], meteor[3], meteor[4], meteor[0]))
                            except Exception as e:
                                print e
                        #cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        
                        #id, filename_original, filename, id_observer, id_server, filepath, obstime, noise, peak_f, mag, duration
                        # file name; noise; peak f.; mag.; duration

                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))

                    elif 'freq' in row['filename_original']: 
                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        pass
                else:
                    print "err", row['filename_original']
                    cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))


            except Exception, e:
                if e[0] == 2:
                    cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                else:
                    print e, repr(e), e[0]
                    time.sleep(2)

        connection.commit()

        connection.close()

        print "konec"
        print "cas:", (time.time()-start_time)/60, "min"


if __name__ == '__main__':
    RTbolidozorAnalyzer()
