#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import paramiko
import MySQLdb as mdb
import time
import datetime
import calendar

class GetMeteors():
    def __init__(self, path=None, year=0, month=0, day=0, minDBDuration = 0.1, minDuration=1, minDurationBolid=20, use_unicode=True, charset="utf8"):
        self.db = mdb.connect(host="localhost", user="root", passwd="root", db="bolid")
        self.dbc = self.db.cursor()

        self.dbc.execute("SELECT VERSION();")
        data = self.dbc.fetchall()
        print "Database version : %s " % data

        self.path = path
        self.year = year
        self.month = month
        self.day = day
        self.minDuration = minDuration
        self.minDBDuration = minDBDuration
        self.minDurationBolid = minDurationBolid

        sftpUSER ='indexer'
        sftpURL = 'space.astro.cz'
        sftpKEY = '/home/roman/.ssh/indexer'

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        self.ssh.connect(sftpURL, username=sftpUSER, key_filename=sftpKEY)
        self.ftp = self.ssh.open_sftp()

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

    def createDb(self):
        self.dbc.execute('SET CHARACTER SET utf8;')
        
        try:
            #self.dbc.execute('DROP TABLE IF EXISTS observatory;')
            #self.dbc.execute('DROP TABLE IF EXISTS server;')
            #self.dbc.execute('DROP TABLE IF EXISTS station;')
            #self.dbc.execute('DROP TABLE IF EXISTS stationstatus;')
            self.dbc.execute('DROP TABLE IF EXISTS meta;')
            self.dbc.execute('DROP TABLE IF EXISTS metalink;')
            self.dbc.execute('DROP TABLE IF EXISTS snap;')
            #self.dbc.execute('DROP TABLE IF EXISTS user;')

            self.dbc.execute('DROP VIEW IF EXISTS meteor;')
            self.db.commit()
        except Exception, e:
            print e
        
        #self.dbc.execute('CREATE TABLE observatory (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(30) UNIQUE KEY, lat FLOAT, lon FLOAT, alt FLOAT, text VARCHAR(255), id_owner INT, id_astrozor INT);')
        #self.dbc.execute('CREATE TABLE server (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(30) UNIQUE KEY, lat FLOAT, lon FLOAT, alt FLOAT, type INT(3), text VARCHAR(255), id_owner INT, id_station INT, id_astrozor INT);')
        #self.dbc.execute('CREATE TABLE station (id INT(6) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(30), id_observatory INT(6), map BOOLEAN DEFAULT 0, handler VARCHAR(60));')
        #self.dbc.execute('CREATE TABLE stationstatus (id_station INT(6) PRIMARY KEY, time INT(14), data VARCHAR(255));')
        self.dbc.execute('CREATE TABLE meta (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, time BIGINT UNSIGNED, id_station SMALLINT UNSIGNED, noise MEDIUMINT UNSIGNED, freq MEDIUMINT UNSIGNED, mag MEDIUMINT UNSIGNED, duration MEDIUMINT UNSIGNED, file VARCHAR(80) UNIQUE KEY, link INT UNSIGNED DEFAULT 0, met_true BOOLEAN DEFAULT 0, met_false BOOLEAN DEFAULT 0, met_head BOOLEAN DEFAULT 0);')
        self.dbc.execute('CREATE TABLE metalink (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, master INT UNSIGNED, link INT UNSIGNED);')
        self.dbc.execute('CREATE TABLE snap (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, time BIGINT UNSIGNED, id_station SMALLINT UNSIGNED, file VARCHAR(80) UNIQUE KEY);')
        #self.dbc.execute('CREATE TABLE user (id INT(6) AUTO_INCREMENT PRIMARY KEY, permission TINYINT UNSIGNED DEFAULT 0, name VARCHAR(30) UNIQUE KEY, pass VARCHAR(30), r_name VARCHAR(30), email VARCHAR(30) UNIQUE KEY, text VARCHAR(30), id_astrozor INT);')
        self.db.commit()
        self.dbc.execute('CREATE INDEX index_meta_time ON meta (time);')
        self.dbc.execute('CREATE VIEW meteor AS SELECT meta.id met_id, meta.id_station obs_id, station.id stat_id, user.id user_id, meta.time/1000 time, meta.noise/1000 noise, meta.freq/10 freq, meta.mag/1000 mag, meta.duration/1000 duration, meta.file file FROM meta INNER JOIN station ON meta.id_station = station.id INNER JOIN observatory ON station.id_observatory = observatory.id INNER JOIN user ON observatory.id_owner = user.id;')
                                # met_id, obs_id, stat_id, user_id, time, noise, freq, mag, duration, file
        self.db.commit()


    def run(self):          ########### Cteni csv souboru a ukladani do databaze
        #print "run"
        daypath = self.path+"/"+str(self.year)+"/"+str(self.month).zfill(2)+"/"+str(self.day).zfill(2)+"/"
        print "/storage/"+str(daypath)
        files = self.ftp.listdir("/storage/"+str(daypath))
        print files
        for file in files:
            if 'meta' in file:
                data = self.ftp.open("/storage/"+str(daypath)+file)
                try:
                    print ">>>>>> id station", self.stationID

                    for line in data:
                        d = line.split(';')
                        if "met" in line:
                            #if float(d[4]) > 0:
                            try:
                                timestap =  str(calendar.timegm(time.strptime(d[0].split("_")[0][:15], "%Y%m%d%H%M%S%f"))+float(d[0].split("_")[0][14:])/1000)
                                self.dbc.execute("INSERT INTO meta (time, id_station, noise, freq, mag, duration, file) VALUES (%f*1000.0, %i, %f*1000.0, %f*10.0, %f*1000.0, %f*1000.0, '%s')"%(float(timestap), int(self.stationID), float(d[1]), float(d[2]), float(d[3]), float(d[4]), str(d[0])))
                            except Exception, e:
                                #print e, "value probably exist"
                                pass
                            #else:
                               #print "kratky"
                               #pass
                        elif "snap" in line:
                            try:
                                timestap =  str(calendar.timegm(time.strptime(d[0].split("_")[0][:15], "%Y%m%d%H%M%S%f"))+float(d[0].split("_")[0][14:])/1000)
                                self.dbc.execute("INSERT INTO snap (time, id_station, file) VALUES (%f, %i, '%s');"%(float(timestap*1000.0), int(self.stationID), str(d[0])))
                            except Exception, e:
                                #print e, "value probably exist"
                                pass
                finally:
                    self.db.commit()
                    data.close()

    def shoda(self, start = time.time()-86400*5, stop=time.time()):
        print "Minimalni delka bolidu je stanovana na ", self.minDurationBolid, "s. Minimalni delka derivatu je", self.minDuration, "s"
        sys.stdout.write("SELECT id, time, duration FROM meta WHERE duration > %i AND time > %i AND time < %i ORDER BY meta.duration DESC;" %(int(self.minDurationBolid*1000.0), int(start*1000), int(stop*1000) ))  
        self.dbc.execute("SELECT id, time, duration FROM meta WHERE duration > %i AND time > %i AND time < %i ORDER BY meta.duration DESC;" %(int(self.minDurationBolid*1000.0), int(start*1000), int(stop*1000) ))  
        row = self.dbc.fetchall()
        print row
        err = 60.0 # casova  odchylka
        for meteor in row:
            self.dbc.execute("SELECT * FROM meta WHERE time > "+str(float((meteor[1])-err*1000))+" AND time <"+str(float((meteor[1])+err*1000))+ " AND duration > "+ str(self.minDuration*1000) +" GROUP BY id_station ORDER BY mag DESC;")
            n = self.dbc.fetchall()
            if len(n) >> 2:
                print "-------", n[0][0] ,float(meteor[1]/1000), datetime.datetime.fromtimestamp(float(meteor[1]/1000)).strftime('%Y-%m-%d %X'), float(meteor[2]/1000)
                refid = n[0][0]
                for near in n:
                    #self.dbc.execute("UPDATE meta SET link ="+str(refid)+" WHERE id ="+str(near[0])+";")
                    try:
                        self.dbc.execute("INSERT INTO metalink (master, link) VALUES (%i, %i);"%(refid, near[0]))
                    except Exception, e:
                        print "Existuje", refid, near[0]
                    print near
                    self.db.commit()

            else:
                sys.stdout.write("pass ")
                sys.stdout.flush()
        self.db.commit()

    def cleanshoda(self):
        self.dbc.execute("TRUNCATE TABLE metalink;")
        self.dbc.execute("UPDATE meta SET link = 0;")  
        self.db.commit()

    def cleanDB(self):
        self.dbc.execute("DELETE FROM meta WHERE link=0;")
        print self.dbc.fetchall()
        self.db.commit()
        print "done"

    def stations(self):
        self.dbc.execute("SELECT observatory.name, station.name, station.id FROM station LEFT JOIN observatory ON station.id_observatory = observatory.id;")
        return self.dbc.fetchall()


def main():  
    meteors = GetMeteors("bolidozor/ZVPP/ZVPP-R3/data", year=0, month=0, day=0, minDBDuration = 0.1, minDuration=5, minDurationBolid=15)
    
    try:
        #meteors.createDb()
        pass
    except Exception, e:
        print "CHYBA V CREATE DB ..... ", e, " <<<<"

    #A=["bolidozor/ZVPP/ZVPP-R4/data"]
    #B=["bolidozor/ZVPP/ZVPP-R4/data", "bolidozor/OBSUPICE/OBSUPICE-R4/data", "bolidozor/svakov/SVAKOV-R7/data"]
    #C=["bolidozor/ZVPP/ZVPP-R4/data", "bolidozor/OBSUPICE/OBSUPICE-R4/data", "bolidozor/svakov/SVAKOV-R7/data", "bolidozor/svakov/TEST-R3/data", "bolidozor/ZEBRAK/ZEBRAK-R3/data", "bolidozor/nachodsko/NACHODSKO-R3/data", "bolidozor/ZVOLENEVES/ZVOLENEVES-R1/data"]
    
    days = 4
    BolidTimeErr = 60      #ZATIM NEFUNGUJE                 # maximalni cas mezi jednou udalosti na vice stanicich
    MasterBolidLenght = 15                  # minimalni delka alespon jednoho bodidu ze skupiny
    SlaveBolidLenght = 10                   # minimalni delka ostatnich bolidu
    DelayDownload = 86400*days                 # pokud je automaticky vyber generovani databaze, jak dlouho zpet se obnovuje DB?
    DelayMulti = 86400*days + BolidTimeErr      # pokud je automaticky vyber generovani databaze, jak dlouho zpet se hleda multibolid?


    if meteors.getYear() == 0:
        #for station in meteors.stations():
        for station in []:
            try:
                meteors.setPath("bolidozor/%s/%s/data" %(station[0], station[1]), stationID = station[2])
                now = time.time()
                start = int(now - DelayDownload)
                stop = int(now)+86400
                for genTime in xrange(start, stop, 86400):
                    try:
                        meteors.set(year = datetime.datetime.fromtimestamp(int(genTime)).year, month = datetime.datetime.fromtimestamp(int(genTime)).month, day = datetime.datetime.fromtimestamp(int(genTime)).day)
                        meteors.run()
                    except Exception, e:
                        print e

            except Exception, e:
                print "ERROR:", e
        try:  
            meteors.shoda()
        except Exception, e:
            print "SHODA", e
    elif 1:
        for station in [('ddmtrebic','DDMTREBIC-TEST-R1')]:
            path = "bolidozor/%s/%s/data" %(station[0], station[1])
            stationID =  station[2]
            meteors.setPath("bolidozor/%s/%s/data" %(station[0], station[1]), stationID = station[2])
            #for month in xrange(1,1):
            meteors.setMonth(2)
            meteors.setYear(2016)
            for day in xrange(1,15):
                try:
                    meteors.setDay(day)  
                    meteors.run()
                    #pass
                except Exception, e:
                    print e
            #meteors.cleanshoda()
            #meteors.shoda()
        #meteors.cleanDB
        meteors.cleanshoda()
        meteors.shoda()
if __name__ == '__main__':
    main()

