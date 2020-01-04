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
import time
import os
import hashlib
import glob

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
        print("#>", query)
        connection = pymysql.connect(host="localhost", user="root", passwd="root", db=db, use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        try:
            cursorobj = connection.cursor()
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
        self.indexProjectFiles()

        print("init")
 

    def indexProjectFiles(self):
        start_time = time.time()
        print("zacatek indexProjectFiles")


        connection = pymysql.connect(host="localhost", user="root", passwd="root", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)

        cursorobj = connection.cursor()
        root = '/storage/bolidozor/'

        #date_folder = '/*/2019/12/[2]*/**/*.*'
        date_folder = '/*/2019/10/??/**/*.*'

        stations = [
#                   'HFN/HFN-R1',
#                    'CIIRC/CIIRC-R1'
#                    'svakov/SVAKOV-R12',
#                    'valmez/VALMEZ-R1',
#                    'nachodsko/NACHODSKO-R5',
                    'OBSUPICE/OBSUPICE-R6',
#                    'ddmtrebic/DDMTREBIC-R3',
                    'HFN/HFN-R1',
                    'FLZ/FLZ-R0',
                    'svakov/SVAKOV-R12',
                    ]
#        stations = ['ASU/ASU-R0']
        stations = ['*/*']

        for station in stations:
            files = glob.glob(root+station+date_folder)
            for fullname in files:
                root = os.path.dirname(fullname)
                file = os.path.basename(fullname)
                try:
                    if 'meta' in file or 'raws' in file or 'csv' in file or 'fits' in file:
                        station_name = file.split('_')[1]
                        uploadtime = datetime.datetime.strptime(file.split('_')[0][:14], '%Y%m%d%H%M%S')
                        md5 = md5Checksum(fullname)
                        cursorobj.execute("SELECT (SELECT id from MLABvo.bolidozor_station WHERE namesimple = '"+station_name+"') as id,(SELECT count(*) FROM `MLABvo`.`bolidozor_fileindex` WHERE checksum = '%s') as 'count';"%(md5))
                        all = cursorobj.fetchall()
                        #cursorobj.execute("SELECT id from MLABvo.bolidozor_station WHERE namesimple = '"+station_name+"';")
                        station_id = all[0]['id']
                        #cursorobj.execute("SELECT count(*) FROM `MLABvo`.`bolidozor_fileindex` WHERE checksum = '%s'"%(md5))
                        lenght = all[0]['count']
                        #filename = file.split('/')[-1]
                        print(file, '\t' , station_name, uploadtime, not bool(lenght))
                        if not bool(lenght):
                            #print("REPLACE INTO `MLABvo`.`bolidozor_fileindex` SET `filename_original` = '%s', `filename` = '%s', `id_observer` = '%d', `id_server` = '%d', `filepath` = '%s', `obstime` = '%s', `uploadtime` = '%s', `lastaccestime` = '%s', `indextime` = '%s', `checksum` = '%s';" %(file, file, station_id, 1, root, uploadtime, uploadtime, '1790-01-01 00:00:00', '1790-01-01 00:00:00', md5))
                            cursorobj.execute("REPLACE INTO `MLABvo`.`bolidozor_fileindex` SET `filename_original` = '%s', `filename` = '%s', `id_observer` = '%d', `id_server` = '%d', `filepath` = '%s', `obstime` = '%s', `uploadtime` = '%s', `lastaccestime` = '%s', `indextime` = '%s', `checksum` = '%s';" %(file, file, station_id, 1, root, uploadtime, uploadtime, '1790-01-01 00:00:00', '1790-01-01 00:00:00', md5))
                            connection.commit()
                except Exception as e:
                    print("CHYBA", e)
            print("commit")
            connection.commit()
        connection.close()


        connection = pymysql.connect(host="localhost", user="root", passwd="root", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        cursorobj = connection.cursor()

        cursorobj.execute("SELECT * FROM  MLABvo.bolidozor_fileindex WHERE id_observer = 0 LIMIT 10000")
        data = cursorobj.fetchall()
        for row in data:
            try:
                print(row)
                station_name = row['filepath'].split('/')[4]
                print(station_name)
                cursorobj.execute("SELECT id from MLABvo.bolidozor_station WHERE namesimple = '"+station_name+"';")
                station_id = cursorobj.fetchall()[0]['id']
                print("station_id", station_id)
                print("UPDATE MLABvo.bolidozor_fileindex SET id_observer = %s WHERE id = %s;" %(station_id, row['id']))
                cursorobj.execute("UPDATE MLABvo.bolidozor_fileindex SET id_observer = %s WHERE id = %s;" %(station_id, row['id']))
            except Exception as e:
                print("Chyba:", e)

        connection.commit()
        connection.close()


        print("konec")
        print("cas:", (time.time()-start_time)/60, "min")



if __name__ == '__main__':
    RTbolidozorAnalyzer()
