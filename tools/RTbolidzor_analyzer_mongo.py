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

import pymongo
import bson

import pickle
from matplotlib.dates import MONDAY
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter

import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl




class RTbolidozorAnalyzer():
    def __init__(self):
        print("RTbolidozor_analyzer")
        
        #self.stanice =  _sql("SELECT id, name, namesimple FROM MLABvo.bolidozor_station where status < 10;")
        #print("dobre stanice", self.stanice)


        self.mdb = pymongo.MongoClient("mongodb://localhost:27017/").Bolidozor

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

        until = datetime.datetime(2020, 1, 6)
        data = self.mdb.file_index.aggregate([ {"$match": {'time_indexed': {"$lt": until}} }, {"$match": {'server_id': 1 }}])

        for row in data:
            #print(rownum, '/', rowlen)
            #print(row)
            try:

                if '.fits' in row['filename']:
                    if 'snap.' in row['filename']:
                        print('snap', row['_id'], row['filename'], end=" ")

                        if row['server_id'] == 1: # je to ulozeno na space?

                            #
                            # Jestli je to snapshot a je na space, tak ho otevru a nactu hlavicku souboru.
                            # Tam najdu delku souboru a odectu to od 'DATE' (sys-time zápisu), to ulozim do obstime v DB.
                            #
                            try:
                                snap = row['server_file_path']+'/'+row['filename']
                                hdulist = fits.open(snap)  # open a FITS file
                                prihdr = hdulist[1].header
                                file_length = prihdr['NAXIS2']*prihdr['CDELT2']/1000.0
                                obstime = datetime.datetime.strptime(prihdr['DATE'] , "%Y-%m-%dT%H:%M:%S")-datetime.timedelta(seconds=file_length)
                                #cur.execute("REPLACE INTO `MLABvo`.`bolidozor_snapshot` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                                print(obstime, file_length, prihdr['ORIGIN'], file_length)


                                self.mdb.file_index.update({'_id': row['_id']},{
                                        "$set": {
                                            'snap.length': file_length,
                                            'time_obs': obstime,
                                            'time_indexed': datetime.datetime.now()
                                        }
                                    })
                            except Exception as e:
                                print("NENI NA SERVERU>>>>")
                                self.mdb.file_index.update({'_id': row['_id']},{
                                        "$set": {
                                            'server_id': 2
                                            }
                                    })

                        #cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))

                    elif 'met.' in row['filename']:
                        print("meteor", row['_id'], row['filename'])
                        
                        if row['server_id'] == 1: # je to ulozeno na space?
                            #
                            # Jestli je to 'met' soubor, tak z odpovidajiciho RAWu si najdu obstime
                            #

                            try:
                                hdulist = fits.open(row['server_file_path']+'/'+row['filename'].replace('met', 'raws'))  # open a FITS file
                                prihdr = hdulist[0].header
                                obstime =  datetime.datetime.strptime(prihdr['DATE'], "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(seconds=prihdr['NAXIS2']*1/96000)
                                length = prihdr['NAXIS2']*1/96000
                                print(obstime, prihdr['DATE'], prihdr['ORIGIN'], length)


                                self.mdb.file_index.update({'_id': row['_id']},{
                                        "$set": {
                                            'met.length': length,
                                            'time_obs': obstime,
                                            'time_indexed': datetime.datetime.now()
                                        }
                                    })
                            except Exception as e:
                                print("NENI NA SERVERU>>>>")
                                self.mdb.file_index.update({'_id': row['_id']},{
                                        "$set": {
                                            'server_id': 2
                                            }
                                    })

                        
                        #cur.execute("REPLACE INTO `MLABvo`.`bolidozor_met` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                        #cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        
                        print(" ")

                    elif 'raws.' in row['filename']:
                        print('raw', row['_id'], row['filename'])

                        if row['server_id'] == 1: # je to ulozeno na space?
                            #
                            # Pokud mam raw, tak take nactu jeho hlavicku a opravim cas v DB, nasledne zaindexuji
                            #
                            #

                            try:
                                hdulist = fits.open(row['server_file_path']+'/'+row['filename'])  # open a FITS file
                                prihdr = hdulist[0].header           # the primary HDU header
                                obstime =  datetime.datetime.strptime(prihdr['DATE'], "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(seconds=prihdr['NAXIS2']*1/96000)
                                print(obstime, prihdr['DATE'], prihdr['ORIGIN'], row['filename'])

                                self.mdb.file_index.update({'_id': row['_id']},{
                                        "$set": {
                                            'raw.length': length,
                                            'time_obs': obstime,
                                            'time_indexed': datetime.datetime.now()
                                        }
                                    })
                            except Exception as e:
                                print("NENI NA SERVERU>>>>")
                                self.mdb.file_index.update({'_id': row['_id']},{
                                        "$set": {
                                            'server_id': 2
                                            }
                                    })

                        #cur.execute("UPDATE `MLABvo`.`bolidozor_v_met` SET `raw_file_id` = '%s' WHERE filename_original = '%s'" %(row['id'], row['filename_original'].replace('raws', 'met')))
                        #cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP(), obstime = '%s' WHERE id = '%s';" %(obstime, row['id']))
    
                
                elif '.csv' in row['filename']:
                    print('csv', row['_id'], row['filename'])
                    if 'meta' in row['filename']:
                        
                        if row['server_id'] == 1: # je to ulozeno na space?
                            meta = row['server_file_path']+'/'+row['filename']

                            try:
                                all_updated = True
                                with open(meta, 'r') as csvfile:
                                    rows = csv.reader(csvfile)
                                    print("===============================================================================")
                                    for row_csv in rows:
                                        try:
                                            if 'met' in row_csv[0]:
                                                meteor = row_csv[0].split(';')     
                                                print(meteor)                                           

                                                status = self.mdb.file_index.update({'filename': row['filename']},{
                                                        "$set": {
                                                            'met.noise': meteor[1],
                                                            'met.peak_f': meteor[2],
                                                            'met.mag': meteor[3],
                                                            'met.length': meteor[4],
                                                        }
                                                    })
                                                all_updated &= status['updatedExisting']

                                            elif 'snap' in row_csv[0]:
                                                meteor = row_csv[0].split(';')     
                                                print(meteor)                                           

                                                status = self.mdb.file_index.update({'filename': row['filename']},{
                                                        "$set": {
                                                            'snap.noise': meteor[1],
                                                            'snap.peak_f': meteor[2],
                                                            'snap.mag': meteor[3],
                                                        }
                                                    })
                                                all_updated &= status['updatedExisting']
                                                
                                        except Exception as e:
                                            print("CSVerr: ", e, row_csv)
                                    if all_updated:
                                        print("Cely soubor ma zaznamy")
                                        self.mdb.file_index.update({'_id': row['_id']},{
                                                "$set": {
                                                    'time_indexed': datetime.datetime.now()
                                                }
                                            })
                            except Exception as e:
                                print(">>ERRcsv ", e)
                        
                        #cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))

                    elif 'freq' in row['filename']: 
                        self.mdb.file_index.update({'_id': row['_id']},{
                                "$set": {
                                    'time_indexed': datetime.datetime.now()
                                }
                            })
                        #cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        pass
                else:
                    print("err", row['filename'])
                    #cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))


            except Exception as e:
                print(">>EndERR", e)
                #if e[0] == 2:
                #    cur.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                #else:
                #    print(e, repr(e), e[0])
                #    time.sleep(2)

        
        print("konec")
        print("cas:", (time.time()-start_time)/60, "min")


if __name__ == '__main__':
    RTbolidozorAnalyzer()
