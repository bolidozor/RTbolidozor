#!/usr/bin/python
# -*- coding: utf-8 -*-


##
##
#
# Software pro zpresneni casu u raw souboru.... 
#
# tento skript vezme vsechny zaznamy ze DB, otevre ho a pokusi se spocitat jeho sysdate - zacatku souboru
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



class RTbolidozorAnalyzer():
    def __init__(self):
        self.indexProjectFiles()


        print "init"
 

    def indexProjectFiles(self):
        start_time = time.time()
        print "zacatek indexProjectFiles"

        start = time.time()
        in_one_query = 1000
        opakovani = 0
       
        connection = pymysql.connect(host="localhost", user="root", passwd="root", db='MLABvo', use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        cursorobj = connection.cursor()

        while  True:
            cursorobj.execute("SELECT * FROM MLABvo.bolidozor_fileindex WHERE filename LIKE '%%.fit%%' ORDER BY id DESC LIMIT %s OFFSET %s;" %(in_one_query, in_one_query*opakovani))
            data = cursorobj.fetchall()
            for row in data:
                path = os.path.join(row['filepath'],row['filename'])
                hdulist = pyfits.open(path)
                print path
                if 'raw' in path:
                    prihdr = hdulist[0].header
                else:
                    print hdulist
                    prihdr = hdulist[1].header
                print path

                r_delt = 1.0/96000  #cas v sekundach mezi vzorky
                f_length = r_delt*prihdr['NAXIS2']
                file_date = prihdr['DATE']
                file_date = datetime.datetime.strptime( file_date, "%Y-%m-%dT%H:%M:%S" )
                print file_date
                sys_beg = file_date-datetime.timedelta(seconds = f_length)

                print f_length
                print file_date
                print sys_beg

                #exists = os.path.exists(path)
                #if not exists and row['filepath'] != 'None':
                #    print exists, path, row['id']
                cursorobj.execute("UPDATE `MLABvo`.`bolidozor_fileindex` SET `obstime`='%s' WHERE `id`='%s'; " %(sys_beg, row['id']) )

            connection.commit()
            opakovani += 1
            print "DONE CYCLE", opakovani, (opakovani)*in_one_query
            print datetime.timedelta(seconds = time.time() - start)
        connection.close()


        print "konec"
        print "cas:", (time.time()-start_time)/60, "min"



if __name__ == '__main__':
    RTbolidozorAnalyzer()
