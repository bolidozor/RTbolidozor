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
import os

class RTbolidozorAnalyzer():
    def __init__(self):
       
        start_time = time.time()


        connection = pymysql.connect(host="localhost", user="roman", passwd="Vibvoflar4", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        
        cursorobj = connection.cursor()

        cursorobj.execute("SELECT * FROM bolidozor_fileindex WHERE indextime < '2000-00-00 01:00:00' AND uploadtime > '2017-09-00 00:00:00' and filename_original LIKE '%met.f%' ORDER BY id DESC LIMIT 1000;")
        zaznamy = cursorobj.fetchall()
        for met in zaznamy:
            print met
            cursorobj.execute("REPLACE INTO `MLABvo`.`bolidozor_met` (`file`, `obstime`) VALUES ('%s', '%s')"%(met['id'], met['obstime']))

        print "ukoncuji"
        connection.commit()
        connection.close()
        print "DONE"




        '''
        print "mam data:", len(data)
        for row in data:
            try:

                if '.fits' in row['filename_original']:
                    if 'snap.' in row['filename_original']:
                        print 'snap', row['filename_original']
                        
                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))

                        if row['id_server'] == 1: # je to ulozeno na space?
                            #snap = self.space_astro.file(row['filepath']+'/'+row['filename_original'])
                            snap = row['filepath']+'/'+row['filename_original']
                            hdulist = pyfits.open(snap)  # open a FITS file
                            #prihdr = hdulist[0].header           # the primary HDU header
                            sechdr = hdulist[1].header           # the primary HDU header

                            obstime =  sechdr['DATE'] 
                            orgin =  sechdr['ORIGIN']

                        _sql("REPLACE INTO `MLABvo`.`bolidozor_snapshot` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                        #_sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        

                    elif 'met.' in row['filename_original']:
                        print "meteor", row['filename_original']
                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        print "update DONE"
                        
                        if row['id_server'] == 1: # je to ulozeno na space?
                            #hdulist = pyfits.open(self.space_astro.file(row[5]+'/'+row['filename_original']))  # open a FITS file
                            hdulist = pyfits.open(row['filepath']+'/'+row['filename_original'])  # open a FITS file
                            print hdulist
                            #prihdr = hdulist[0].header           # the primary HDU header
                            sechdr = hdulist[1].header           # the primary HDU header

                            obstime =  sechdr['DATE'] 
                            orgin =  sechdr['ORIGIN']
                            
                        print "######################################################"
                        _sql("REPLACE INTO `MLABvo`.`bolidozor_met` (`file`, `obstime`) VALUES ('%s', '%s');" %(row['id'], obstime))
                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        
                        print " "
                        print " "

                    elif 'raws.' in row['filename_original']:
                        print 'raw', row['filename_original']

                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        pass
                elif '.csv' in row['filename_original']:
                    print 'csv', row['filename_original']

                    if 'meta' in row['filename_original']:
                        
                        if row['id_server'] == 1: # je to ulozeno na space?
                            #meta = self.space_astro.file(row[5]+'/'+row['filename_original'])
                            meta = row['filepath']+'/'+row['filename_original']

                            with open(meta) as csvfile:
                                meteors = csv.reader(csvfile)
                                print meteors
                                for meteor in meteors:
                                    if 'met' in meteor[0]:
                                        meteor = meteor[0].split(';')
                                        print meteor
                                        _sql("UPDATE `MLABvo`.`bolidozor_v_met` SET noise = '%s', peak_f = '%s', mag = '%s', duration = '%s' WHERE filename_original = '%s';" %(meteor[1], meteor[2], meteor[3], meteor[4], meteor[0]))
                        #_sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        
                        #id, filename_original, filename, id_observer, id_server, filepath, obstime, noise, peak_f, mag, duration
                        # file name; noise; peak f.; mag.; duration

                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))

                    elif 'freq' in row['filename_original']: 
                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row['id']))
                        pass
                else:
                    print "err", row['filename_original']
            

            except Exception, e:
                print e, repr(e)
                time.sleep(2)
            '''

        print "konec"
        print "cas:", (time.time()-start_time)/60, "min"



if __name__ == '__main__':
    RTbolidozorAnalyzer()
