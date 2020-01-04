#!/usr/bin/python
# -*- coding: utf-8 -*-


##
##
#
# Software pro roztztrideni dat v nove databazi MLABvo.... rozradi to soubory z tabulky 'bolidozor_fileindex' do tabulky met, snapshots atd .. u tabulky met to pri cteni fits souboru zapise jeho parametry.
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
from astropy.io import fits
import time
import pandas as pd

import pickle
from matplotlib.dates import MONDAY
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter

import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl


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


class RTbolidozorAnalyzer():
    def __init__(self):
        print("RTbolidozor_analyzer")
        
        self.stanice =  _sql("SELECT id, name, namesimple FROM MLABvo.bolidozor_station where status < 10;")
        print("dobre stanice", self.stanice)

        while True:
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
            print("dokoncen %s graf" %(path_img))
        except Exception as e:
            print(e, path_img)
        

    def indexProjectFiles(self):
        start_time = time.time()
        print("zacatek indexProjectFiles")

        connection = pymysql.connect(host="localhost", user="root", passwd="root", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        cur = connection.cursor()

        cur.execute("SELECT * FROM bolidozor_fileindex WHERE indextime < '2000-01-01 00:00:00' AND uploadtime > '2019-10-01 00:00:00' ORDER BY id DESC LIMIT 4000;")
        #cur.execute("SELECT * FROM bolidozor_fileindex WHERE obstime > '2019-12-30 00:00:00' LIMIT 5000;")
        
        #cur.execute("SELECT * FROM bolidozor_fileindex WHERE indextime < '2019-01-01 00:00:00' AND uploadtime > '2017-08-00 00:00:00' and filename_original LIKE '%csv%' ORDER BY id DESC LIMIT 3000;")
        #cur.execute("SELECT * FROM bolidozor_fileindex ORDER BY id DESC LIMIT 10000")
        #cur.execute("SELECT * FROM bolidozor_fileindex WHERE filename_original LIKE '%meta%' ORDER BY id DESC LIMIT 5000000;")
        #cur.execute("SELECT * FROM bolidozor_fileindex WHERE filename_original LIKE '20180306%' ORDER BY id DESC LIMIT 50000;")
        
        data = cur.fetchall()
        rowlen = len(data)
        print("mam data:", len(data))
        for rownum, row in enumerate(data):
            print(rownum, '/', rowlen)
            try:

                if '.fits' in row['filename_original']:
                    if 'snap.' in row['filename_original']:
                        print('snap', row['id'], row['filename_original'], end=" ")

                        if row['id_server'] == 1: # je to ulozeno na space?

                            #
                            # Jestli je to snapshot a je na space, tak ho otevru a nactu hlavicku souboru.
                            # Tam najdu delku souboru a odectu to od 'DATE' (sys-time zápisu), to ulozim do obstime v DB.
                            #

                            snap = row['filepath']+'/'+row['filename_original']
                            print(row)
                            hdulist = fits.open(snap)  # open a FITS file
                            prihdr = hdulist[1].header
                            file_length = prihdr['NAXIS2']*prihdr['CDELT2']/1000.0
                            obstime = datetime.datetime.strptime(prihdr['DATE'] , "%Y-%m-%dT%H:%M:%S")-datetime.timedelta(seconds=file_length)
                            cur.execute("REPLACE INTO `MLABvo`.`bolidozor_snapshot` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                            print(obstime, file_length, prihdr['ORIGIN'])

                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))

                    elif 'met.' in row['filename_original']:
                        print("meteor", row['id'], row['filename_original'])
                        
                        if row['id_server'] == 1: # je to ulozeno na space?
                            #
                            # Jestli je to 'met' soubor, tak z odpovidajiciho RAWu si najdu obstime
                            #

                            hdulist = fits.open(row['filepath']+'/'+row['filename_original'].replace('met', 'raws'))  # open a FITS file
                            prihdr = hdulist[0].header
                            obstime =  datetime.datetime.strptime(prihdr['DATE'], "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(seconds=prihdr['NAXIS2']*1/96000)
                            print(obstime, prihdr['DATE'], prihdr['ORIGIN'])
                            
                        print("######################################################")
                        
                        cur.execute("REPLACE INTO `MLABvo`.`bolidozor_met` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        
                        print(" ")

                    elif 'raws.' in row['filename_original']:
                        print('raw', row['id'], row['filename_original'])

                        if row['id_server'] == 1: # je to ulozeno na space?
                            #
                            # Pokud mam raw, tak take nactu jeho hlavicku a opravim cas v DB, nasledne zaindexuji
                            #
                            #

                            hdulist = fits.open(row['filepath']+'/'+row['filename_original'])  # open a FITS file
                            prihdr = hdulist[0].header           # the primary HDU header
                            obstime =  datetime.datetime.strptime(prihdr['DATE'], "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(seconds=prihdr['NAXIS2']*1/96000)
                            print(obstime, prihdr['DATE'], prihdr['ORIGIN'], row['filename_original'])

                        #cur.execute("UPDATE `MLABvo`.`bolidozor_v_met` SET `raw_file_id` = '%s' WHERE filename_original = '%s'" %(row['id'], row['filename_original'].replace('raws', 'met')))
                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP(), obstime = '%s' WHERE id = '%s';" %(obstime, row['id']))
    
                
                elif '.csv' in row['filename_original']:
                    print('csv', row['id'], row['filename_original'])
                    if 'meta' in row['filename_original']:
                        
                        if row['id_server'] == 1: # je to ulozeno na space?
                            meta = row['filepath']+'/'+row['filename_original']

                            try:
                                with open(meta, 'r') as csvfile:
                                    rows = csv.reader(csvfile)
                                    print("===============================================================================")
                                    for row_csv in rows:
                                        try:
                                            if 'met' in row_csv[0]:
                                                meteor = row_csv[0].split(';')     
                                                print(meteor)                                           
                                                cur.execute("SELECT `id` FROM `MLABvo`.`bolidozor_fileindex` WHERE `filename_original` = '%s';" %(meteor[0]))
                                                out = cur.fetchone()
                                                if out:
                                                    cur.execute("UPDATE `MLABvo`.`bolidozor_met` SET noise = '%s', peak_f = '%s', mag = '%s', duration = '%s' WHERE file = '%s';" %(meteor[1], meteor[2], meteor[3], meteor[4], out['id']))
                                                else:
                                                    print("Soubor jesne neni zaindexovan")
                                        except Exception as e:
                                            print("CSVerr: ", e, row_csv)
                            except Exception as e:
                                print(">>ERRcsv ", e)
                        
                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))

                    elif 'freq' in row['filename_original']: 
                        cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        pass
                else:
                    print("err", row['filename_original'])
                    cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))


            except Exception as e:
                print(">>EndERR", e)
                #if e[0] == 2:
                #    cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                #else:
                #    print(e, repr(e), e[0])
                #    time.sleep(2)

        connection.commit()

        connection.close()

        print("konec")
        print("cas:", (time.time()-start_time)/60, "min")


if __name__ == '__main__':
    RTbolidozorAnalyzer()
