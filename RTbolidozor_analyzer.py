#!/usr/bin/python
# -*- coding: utf-8 -*-


##
##
#
# Software pro roztztrideni dat v nove databazi MLAvo.... rozradi to soubory z tabulky 'bolidozor_fileindex' do tabulky met, snapshots atd .. u tabulky met to pri cteni fits souboru zapise jeho parametry.
# Melo by to byl spousteno z cronu
#
# @reboot python /home/roman/repos/RTbolidozor/bolidFinder.py | tee /home/roman/RTbolidozorCron.log
#
##
##

import MySQLdb as mdb
import time
import datetime
import csv
import pyfits
import paramiko
import time

def _sql(query, read=False):
        #print "#>", query
        connection = mdb.connect(host="localhost", user="root", passwd="root", db="MLABvo", use_unicode=True, charset="utf8")
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


class RTbolidozorAnalyzer():
    def __init__(self):
        print "init"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('space.astro.cz', username='indexer', key_filename='/home/roman/.ssh/indexer')
        self.space_astro = ssh.open_sftp()
        print "done"
        self.indexProjectFiles()
        self.findMatch()

    def indexProjectFiles(self):
        start_time = time.time()
        print "zacatek indexProjectFiles"
        data = _sql("SELECT * FROM bolidozor_fileindex WHERE indextime = '0000-00-00 00:00:00' ORDER BY id DESC LIMIT 1000", True)
        print "mam data:", len(data)
        for row in data:
            try:

                if '.fits' in row[1]:
                    if 'snap.' in row[1]:
                        print 'snap', row[1]
                        
                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))

                        if row[4] == 1: # je to ulozeno na space?
                            snap = self.space_astro.file(row[5]+'/'+row[1])
                            hdulist = pyfits.open(snap)  # open a FITS file
                            prihdr = hdulist[0].header           # the primary HDU header
                            sechdr = hdulist[1].header           # the primary HDU header

                            obstime =  sechdr['DATE'] 
                            orgin =  sechdr['ORIGIN']

                        _sql("REPLACE INTO `MLABvo`.`bolidozor_snapshot` (`file`, `create`) VALUES ('%s', '%s');" %(row[0], obstime))
                        #_sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        

                    elif 'met.' in row[1]:
                        print "meteor", row[1]

                        obstime = '0000-00-00 00:00:00'

                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        
                        if row[4] == 1: # je to ulozeno na space?
                            hdulist = pyfits.open(self.space_astro.file(row[5]+'/'+row[1]))  # open a FITS file
                            prihdr = hdulist[0].header           # the primary HDU header
                            sechdr = hdulist[1].header           # the primary HDU header

                            obstime =  sechdr['DATE'] 
                            orgin =  sechdr['ORIGIN']
                            
                        _sql("REPLACE INTO `MLABvo`.`bolidozor_met` (`file`, `obstime`) VALUES ('%s', '%s');" %(row[0], obstime))
                        #_sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        
                        print " "
                        print " "

                    elif 'raw.' in row[1]:
                        print 'raw', row[1]

                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        pass
                elif '.csv' in row[1]:
                    print 'csv', row[1]

                    if 'meta' in row[1]:
                        
                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        if row[4] == 1: # je to ulozeno na space?
                            meta = self.space_astro.file(row[5]+'/'+row[1])

                            meteors = csv.reader(meta)
                            print meteors
                            for meteor in meteors:
                                if 'met' in meteor[0]:
                                    meteor = meteor[0].split(';')
                                    print meteor
                                    _sql("UPDATE `MLABvo`.`bolidozor_v_met` SET noise = '%s', peak_f = '%s', mag = '%s', duration = '%s' WHERE filename_original = '%s';" %(meteor[1], meteor[2], meteor[3], meteor[4], meteor[0]))
                        #_sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        
                        #id, filename_original, filename, id_observer, id_server, filepath, obstime, noise, peak_f, mag, duration
                        # file name; noise; peak f.; mag.; duration

                    elif 'freq' in row[1]: 
                        _sql("UPDATE `MLABvo`.`bolidozor_fileindex` SET indextime = UTC_TIMESTAMP() WHERE id = '%s';" %(row[0]))
                        pass
                else:
                    print "err", row[1]


            except Exception, e:
                print e

        print "konec"
        print "cas:", (time.time()-start_time)/60, "min"


    def findMatch(self):
        start_time = time.time()
        print "zacatek indexProjectFiles"

        data = _sql("SELECT * FROM bolidozor_fileindex WHERE id_observer = 0 ORDER BY id DESC LIMIT 10000", True)
        for row in data:
            try:
                print row[1].split("_")[1]
                id_station = _sql("SELECT id FROM bolidozor_station WHERE namesimple = '%s'" %(row[1].split("_")[1]))[0][0]
                _sql("UPDATE `bolidozor_fileindex` SET id_observer = '%s' WHERE id = '%s';" %(id_station, row[0]))

            except Exception, e:
                print "---"
                print row
                print e


        print "konec"
        print "cas:", (time.time()-start_time)/60, "min"


if __name__ == '__main__':
    RTbolidozorAnalyzer()
