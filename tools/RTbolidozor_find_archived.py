#!/usr/bin/python
# -*- coding: utf-8 -*-


##
##
#
# Software pro roztztrideni dat v nove databazi MLAvo.... 
#
# tento skript vezme vsechny zaznamy ze space a pokud neni v je v DB a ne na space, tak ho oznaci jako presunuty na cesnet server - server_id = 2
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
        self.indexProjectFiles()


        print "init"
 

    def indexProjectFiles(self):
        start_time = time.time()
        print "zacatek indexProjectFiles"

        start = time.time()
        in_onj_query = 1000
        opakovani = 140
       
        connection = pymysql.connect(host="localhost", user="root", passwd="root", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        cursorobj = connection.cursor()

        while  True:
            cursorobj.execute("SELECT * FROM MLABvo.bolidozor_fileindex ORDER BY id LIMIT %s OFFSET %s;" %(in_onj_query, in_onj_query*opakovani))
            data = cursorobj.fetchall()
            for row in data:
                path = os.path.join(row['filepath'],row['filename'])
                exists = os.path.exists(path)
                if not exists and row['filepath'] != 'None':
                    print exists, path, row['id']
                    cursorobj.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET `id_server`='2' WHERE `id`='%s'; " %(row['id']))

            connection.commit()
            opakovani += 1
            print "DONE CYCLE", opakovani, (opakovani)*in_onj_query
            print datetime.timedelta(seconds = time.time() - start)
        connection.close()


        print "konec"
        print "cas:", (time.time()-start_time)/60, "min"



if __name__ == '__main__':
    RTbolidozorAnalyzer()
