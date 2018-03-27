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
import hashlib


def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def _sql(query, read=False, db="MLABvo"):
        print "#>", query
        connection = pymysql.connect(host="localhost", user="roman", passwd="Vibvoflar4", db=db, use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        try:
            cursorobj = connection.cursor()
            cursorobj.execute(query)
            result = cursorobj.fetchall()
            if not read:
                connection.commit()
        except Exception, e:
                print("Err", e)
        connection.close()
        return result


class RTbolidozorAnalyzer():
    def __init__(self):
        self.indexProjectFiles()

        print("init")
 

    def indexProjectFiles(self):
        start_time = time.time()
        print "zacatek indexProjectFiles"


        connection = pymysql.connect(host="localhost", user="roman", passwd="Vibvoflar4", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        
        cursorobj = connection.cursor()
        date_folder = '2018/02/07/02'
        stations = [
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/02/00',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/00',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/01',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/02',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/03',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/04',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/05',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/06',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/07',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/08',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/09',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/10',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/11',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/03',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/12',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/13',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/14',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/15',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/16',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/17',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/18',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/19',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/20',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/21',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/03/22',
#                    '/storage/bolidozor/CIIRC/CIIRC-R1/meteors/2018/03/',
#                    '/storage/bolidozor/HFN/HFN-R1/meteors/2018/03/',
                    
                    #'/storage/bolidozor/ZVPP/ZVPP-R6/data/' + date_folder,
                    #'/storage/bolidozor/ZVPP/ZVPP-R6/data/' + date_folder,

                    #'/storage/bolidozor/svakov/SVAKOV-R12/data/' + date_folder,
                    #'/storage/bolidozor/svakov/SVAKOV-R12/meteors/' + date_folder,
                    #'/storage/bolidozor/svakov/SVAKOV-R12/snapshots/' + date_folder,
                    
                    '/storage/bolidozor/valmez/VALMEZ-R1/data/' + date_folder,
                    '/storage/bolidozor/valmez/VALMEZ-R1/meteors/' + date_folder,
                    '/storage/bolidozor/valmez/VALMEZ-R1/snapshots/' + date_folder,
                    
                    '/storage/bolidozor/nachodsko/NACHODSKO-R5/data/' + date_folder,
                    '/storage/bolidozor/nachodsko/NACHODSKO-R5/meteors/' + date_folder,
                    '/storage/bolidozor/nachodsko/NACHODSKO-R5/meteors/' + date_folder,
                    
                    '/storage/bolidozor/OBSUPICE/OBSUPICE-R6/data/' + date_folder,
                    '/storage/bolidozor/OBSUPICE/OBSUPICE-R6/meteors/' + date_folder,
                    '/storage/bolidozor/OBSUPICE/OBSUPICE-R6/snapshots/' + date_folder,

                    #'/storage/bolidozor/ddmtrebic/DDMTREBIC-R3/data/' + date_folder,
                    #'/storage/bolidozor/ddmtrebic/DDMTREBIC-R3/meteors/' + date_folder,
                    #'/storage/bolidozor/ddmtrebic/DDMTREBIC-R3/snapshots/' + date_folder,

                    '/storage/bolidozor/HFN/HFN-R1/meteors/' + date_folder,
                    '/storage/bolidozor/HFN/HFN-R1/snapshots/' + date_folder,
                    '/storage/bolidozor/HFN/HFN-R1/data/' + date_folder,
                    ]

        for station in stations:
            #station_name = station.split('/')[4]
            #print "station name", station_name
            #cursorobj.execute("SELECT id from MLABvo.bolidozor_station WHERE namesimple = '"+station_name+"';")
            #station_id = cursorobj.fetchall()[0]['id']
            #print "station_id", station_id

            for root, dirs, files in os.walk(station):
                for file in files:
                    try:
                        if 'meta' in file or 'raws' in file or 'csv' in file or 'fits' in file:
                            station_name = file.split('_')[1]
                            uploadtime = datetime.datetime.strptime(file.split('_')[0][:14], '%Y%m%d%H%M%S')
                            md5 = md5Checksum(root+'/'+file)
                            cursorobj.execute("SELECT (SELECT id from MLABvo.bolidozor_station WHERE namesimple = '"+station_name+"') as id,(SELECT count(*) FROM `MLABvo`.`bolidozor_fileindex` WHERE checksum = '%s') as 'count';"%(md5))
                            all = cursorobj.fetchall()
                            #cursorobj.execute("SELECT id from MLABvo.bolidozor_station WHERE namesimple = '"+station_name+"';")
                            station_id = all[0]['id']
                            #cursorobj.execute("SELECT count(*) FROM `MLABvo`.`bolidozor_fileindex` WHERE checksum = '%s'"%(md5))
                            lenght = all[0]['count']
                            print file, station_name, uploadtime, md5, not bool(lenght)
                            if lenght == 0:
                                cursorobj.execute("REPLACE INTO `MLABvo`.`bolidozor_fileindex` SET `filename_original` = '%s', `filename` = '%s', `id_observer` = '%d', `id_server` = '%d', `filepath` = '%s', `obstime` = '%s', `uploadtime` = '%s', `lastaccestime` = '%s', `indextime` = '%s', `checksum` = '%s';" %(file, file, station_id, 1, root, uploadtime, uploadtime, '1790-01-01 00:00:00', '1790-01-01 00:00:00', md5))
                                connection.commit()
                    except Exception as e:
                        print e
                print "commit"
                connection.commit()
        connection.close()


        connection = pymysql.connect(host="localhost", user="roman", passwd="Vibvoflar4", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        cursorobj = connection.cursor()

        cursorobj.execute("SELECT * FROM  MLABvo.bolidozor_fileindex WHERE id_observer = 0 LIMIT 1000")
        data = cursorobj.fetchall()
        for row in data:
            station_name = row['filepath'].split('/')[4]
            print station_name
            cursorobj.execute("SELECT id from MLABvo.bolidozor_station WHERE namesimple = '"+station_name+"';")
            station_id = cursorobj.fetchall()[0]['id']
            print "station_id", station_id
            print "UPDATE MLABvo.bolidozor_fileindex SET id_observer = %s WHERE id = %s;" %(station_id, row['id'])
            cursorobj.execute("UPDATE MLABvo.bolidozor_fileindex SET id_observer = %s WHERE id = %s;" %(station_id, row['id']))


        connection.commit()
        connection.close()


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
