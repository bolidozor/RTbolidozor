#!/usr/bin/python
# -*- coding: utf-8 -*-



#

#

#

# UPDATE file_index INNER JOIN bz_snap ON bz_snap.id_file = file_index.id SET indextime = 0 where bz_snap.obstime = 0;
# UPDATE file_index INNER JOIN bz_snap ON bz_met.id_file = file_index.id SET indextime = 0 where bz_met.obstime = 0;
#
#

import sys
#import paramiko
import MySQLdb as mdb
import time
import datetime
import calendar
import pandas as pd
import os
import pyfits

##**************************************
##**************************************
##
##
days = 5
gento = time.time()
genfrom = gento - 86400*days
##
##
##**************************************
##**************************************

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
    except Exception as e:
            print("Err", e)
    connection.close()
    return result

class GetMeteors():
    def __init__(self, path=None, year=0, month=0, day=0, minDBDuration = 0.1, minDuration=1, minDurationBolid=20, maxOffset = 5, use_unicode=True, charset="utf8"):
        #self.db = mdb.connect(host="localhost", user="root", passwd="root", db="RTbolidozor")
        #self.dbc = self.db.cursor()

        #self.dbc.execute("SELECT VERSION();")
        #data = self.dbc.fetchall()
        #print "Database version : %s " % data

        self.path = path
        self.year = year
        self.month = month
        self.day = day
        self.minDuration = minDuration
        self.minDBDuration = minDBDuration
        self.minDurationBolid = minDurationBolid
        self.maxOffset = maxOffset

        #sftpUSER ='indexer'
        #sftpURL = 'space.astro.cz'
        #sftpKEY = '/home/roman/.ssh/indexer'

        #self.ssh = paramiko.SSHClient()
        #self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #self.ssh.load_system_host_keys()
        #self.ssh.connect(sftpURL, username=sftpUSER, key_filename=sftpKEY)
        #self.sftp = self.ssh.open_sftp()


    def setPath(self, path=None, stationID=None):
        if path:
            self.path = path
        if  stationID:
            self.stationID = stationID

    def setDay(self, day=None):
        if day:
            self.day = day

    def setMonth(self, month=None):
        if month:
            self.month = month

    def setYear(self, year=None):
        if year:
            self.year = year

    def getYear(self):
            return self.year

    def set(self, year = None, month = None, day = None):
        if year:
            self.year = year
        if month:
            self.month = month
        if day:
            self.day = day
        


    def find_match(self):
        print("######################################################################################")
        print("######################################################################################")
        i = 0
        #self.minDuration = float(_sql("select * from bz_param where name = 'master_met_min_duration'")[0][0])*10
        #self.minDurationBolid = float(_sql("select * from bz_param where name = 'group_max_time_delta'")[0][0])*10
        #self.minDuration = 1
        #self.minDurationBolid = 10
        err = datetime.timedelta(0,self.maxOffset)

        print("Minimalni delka bolidu je stanovana na ", self.minDurationBolid, "s. Minimalni delka derivatu je", self.minDuration, "s")
        print("Maximalni casova odchylka je %s s" %(self.maxOffset))

        row = _sql('''
            SELECT bolidozor_met.id, bolidozor_met.obstime, bolidozor_met.duration
            FROM bolidozor_met INNER JOIN bolidozor_fileindex ON bolidozor_fileindex.id = bolidozor_met.file
            INNER JOIN bolidozor_station ON bolidozor_fileindex.id_observer = bolidozor_station.id
            WHERE (bolidozor_met.duration > %i)
                AND (bolidozor_met.obstime BETWEEN '%s' AND '%s')
                ORDER BY bolidozor_met.obstime DESC LIMIT 200;
            ''' %(int(self.minDurationBolid), datetime.datetime(2017, 8, 1).date().isoformat(), datetime.datetime.utcnow().isoformat() ))
        
        lenrow = len(row)

        for meteor in row:
            print("mam vybrany meteor", meteor)
            n = _sql('''
                SELECT bolidozor_met.id, bolidozor_met.duration FROM bolidozor_met
                INNER JOIN bolidozor_fileindex ON bolidozor_fileindex.id = bolidozor_met.file
                INNER JOIN bolidozor_station ON bolidozor_fileindex.id_observer = bolidozor_station.id
                WHERE (bolidozor_met.obstime BETWEEN '%s' AND '%s') AND (bolidozor_met.duration > %f)
                ORDER BY bolidozor_met.mag DESC LIMIT 20;
                ''' %( meteor[1]-err, meteor[1]+err, float(self.minDuration)))
            
            print(n)
            max_dur = n[0][1]
            refid = n[0][0]
            for met in n:
                if met[1] > max_dur:
                    max_dur = met[1]
                    refid = met[0]
            print(refid, max_dur)

            print("mam %i meteoru okolo" %(len(n)))
            if len(n) > 2:
                print("-------", n[0] , meteor[1].strftime('%Y-%m-%d %X'), float(meteor[2]))
                for near in n:
                    try:
                        print(refid, near[0])
                        _sql("INSERT INTO bolidozor_met_match (match_id, met_id) VALUES (%i, %i);"%(refid, near[0]))
                        print("Existuje", refid, near[0])
                    except Exception as e:
                        print("Error", e)
                    print(near)

            else:
                print("#")




    def run(self):          ########### Cteni csv souboru a ukladani do databaze
        self.find_match()



    def shoda(self, start = time.time()-86400*10, stop=time.time()):
        i = 0
        print("Minimalni delka bolidu je stanovana na ", self.minDurationBolid, "s. Minimalni delka derivatu je", self.minDuration, "s")
        #sys.stdout.write("SELECT meta.id, meta.time, meta.duration FROM meta JOIN station ON meta.id_station = station.id WHERE (meta.duration) > %i AND (time BETWEEN %i AND %i) AND (station.id_stationstat = 1)  ORDER BY meta.time DESC;" %(int(self.minDurationBolid), int(genfrom), int(gento+86400) ))  
        self.dbc.execute("SELECT meta.id, meta.time, meta.duration FROM meta JOIN station ON meta.id_station = station.id WHERE (meta.duration > %i) AND (meta.time BETWEEN %i AND %i) AND (station.id_stationstat = 1) ORDER BY meta.mag DESC;" %(int(self.minDurationBolid), int(genfrom), int(gento+86400) ))  
        row = self.dbc.fetchall()
        lenrow = len(row)
        print(row, len(row))
        print("")
        err = 60.0 # casova  odchylka
        for meteor in row:
            #self.dbc.execute("SELECT * FROM meta LEFT OUTER JOIN metalink ON metalink.link = meta.id WHERE (metalink.link IS NULL) AND (meta.time BETWEEN %f AND %f) AND (meta.duration > %f)  GROUP BY meta.id_station ORDER BY meta.mag DESC;" %(float(meteor[1])-err, float(meteor[1])+err, float(self.minDuration)))
            self.dbc.execute("SELECT meta.id FROM meta JOIN station ON meta.id_station = station.id WHERE (meta.time > %f) AND (meta.time < %f) AND (meta.duration > %f) AND (station.id_stationstat = 1) GROUP BY meta.id_station ORDER BY meta.mag DESC;" %(float(meteor[1])-err, float(meteor[1])+err, float(self.minDuration)))
            n = self.dbc.fetchall()
            if len(n) > 3:
                print("-------", n[0][0] ,float(meteor[1]), datetime.datetime.fromtimestamp(float(meteor[1])).strftime('%Y-%m-%d %X'), float(meteor[2]))
                refid = n[0][0]
                for near in n:
                    try:
                        self.dbc.execute("INSERT INTO metalink (master, link) VALUES (%i, %i);"%(refid, near[0]))
                    except Exception as e:
                        print("Existuje", refid, near[0])
                    print(near)
                    self.db.commit()

            else:
                sys.stdout.write("#")
                sys.stdout.flush()
        self.db.commit()


def main():  
    meteors = GetMeteors(None, year=0, month=0, day=0, minDBDuration = 0.1, minDuration=1, minDurationBolid=6)
    
    meteors.run()
    

if __name__ == '__main__':
    main()

