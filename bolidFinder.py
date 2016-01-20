#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import sqlite3
import time


class GetMeteors():
    def __init__(self, path=None, year=0, month=0, day=0, minDuration=1, minDurationBolid=2):
        self.db = sqlite3.connect('bolidNEW.db')
        self.dbc = self.db.cursor()
        self.path = path
        self.year = year
        self.month = month
        self.day = day
        self.minDuration = minDuration
        self.minDurationBolid = minDurationBolid

        sftpUSER ='indexer'
        sftpURL = 'space.astro.cz'
        sftpKEY = '/home/roman/.ssh/indexer'

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        self.ssh.connect(sftpURL, username=sftpUSER, key_filename=sftpKEY)
        self.ftp = self.ssh.open_sftp()

    def setPath(self, path=None):
        if path:
            self.path = path

    def setDay(self, day=None):
        if day:
            self.day = day

    def setMonth(self, month=None):
        if month:
            self.month = month

    def setYear(self, year=None):
        if year:
            self.year = year

    def createDb(self):

        #self.dbc = conn.cursor()
        # # file name    noise   peak f.     mag.    duration
        self.dbc.execute('CREATE TABLE meta (time DATETIME, station text, noise int, freq int, mag int, duration int, file text UNIQUE ON CONFLICT replace, link int DEFAULT 0, met_true int,  met_false int,  met_head int)')
        self.dbc.execute('CREATE TABLE station (station text, ident text, last int, url_data text, url_space_data text, url_space_snaps text, url_space_met text, map bool DEFAULT false)')
        self.dbc.execute('CREATE TABLE snap (time DATETIME, station text, file text unique on conflict fail)')
        #self.dbc.execute("INSERT INTO meta VALUES (20160114135020707,'ZVPP-R3',42869,26513700,123123, 170667)")
        self.db.commit()


    def run(self):          ########### Cteni csv souboru a ukladani do databaze
        print "run"
        daypath = self.path+"/"+str(self.year)+"/"+str(self.month).zfill(2)+"/"+str(self.day).zfill(2)+"/"
        print "/storage/"+str(daypath)
        files = self.ftp.listdir("/storage/"+str(daypath))
        print files
        for file in files:
            if 'meta' in file:
                data = self.ftp.open("/storage/"+str(daypath)+file)
                try:
                    for line in data:
                        if "met" in line:
                            d = line.split(';')
                            if float(d[4]) > self.minDuration:
                                try:
                                    print "zapis:"+str(d[4])
                                    self.dbc.execute("INSERT INTO meta (time, station, noise, freq, mag, duration, file) VALUES ("+ str(time.mktime(time.strptime(d[0].split("_")[0][:14], "%Y%m%d%H%M%S%f"))+int(d[0].split("_")[0][14:])/1000)+",'"+str( d[0].split("_")[1] )+"',"+str( int(float(d[1])*1000) )+","+str( int(float(d[2])*10) )+","+str( int(float(d[3])*1000) )+", "+str( int(float(d[4])*1000000) )+", '"+str(d[0])+"')")
                                except Exception, e:
                                    #print e, "value probably exist"
                                    pass
                            #else:
                               #print "kratky"
                               #pass
                        elif "snap" in line:
                                try:
                                    self.dbc.execute("INSERT INTO snap VALUES ("+ str(time.mktime(time.strptime(d[0].split("_")[0][:14], "%Y%m%d%H%M%S%f"))+int(d[0].split("_")[0][14:])/1000)+",'"+str( d[0].split("_")[1] )+"','"+str(d[0])+"')")
                                except Exception, e:
                                    #print e, "value probably exist"
                                    pass
                finally:
                    self.db.commit()
                    data.close()

    def shoda(self):
        print("SELECT time, duration FROM meta WHERE duration > "+str(self.minDurationBolid*1000000)+" ORDER BY meta.time")  
        self.dbc.execute("SELECT time, duration FROM meta WHERE duration > "+str(self.minDurationBolid*1000000)+" ORDER BY meta.time")  
        row = self.dbc.fetchall()
        print row
        for meteor in row:
            err = 500 # casova  odchylka
            self.dbc.execute("SELECT rowid, * FROM meta WHERE time > "+str(meteor[0]-err)+" AND meta.time <"+str(meteor[0]+err)+ " GROUP BY station ORDER BY meta.mag DESC")
            n = self.dbc.fetchall()
            if len(n) >> 2:
                print "-------", meteor[0], meteor[1]*1.0/1000000.0
                refid = n[0][0]
                for near in n:
                    self.dbc.execute("UPDATE meta SET link ="+str(refid)+" WHERE rowid ="+str(near[0]))
                    print near
        self.db.commit()

    def cleanshoda(self):
        self.dbc.execute("UPDATE meta SET link = 0")  
        self.db.commit()

    def cleanDB(self):
        self.dbc.execute("DELETE FROM meta WHERE link=0")
        print self.dbc.fetchall()
        self.db.commit()
        print "done"



def main():  
    meteors = GetMeteors("bolidozor/ZVPP/ZVPP-R3/data", year=2016, month=01, day=1, minDuration=5, minDurationBolid=20)
    #meteors.createDb()
    A=["bolidozor/ZVPP/ZVPP-R3/data"]
    B=["bolidozor/ZVPP/ZVPP-R3/data", "bolidozor/OBSUPICE/OBSUPICE-R4/data", "bolidozor/svakov/SVAKOV-R6/data"]
    C=["bolidozor/ZVPP/ZVPP-R3/data", "bolidozor/OBSUPICE/OBSUPICE-R4/data", "bolidozor/svakov/SVAKOV-R6/data", "bolidozor/ZEBRAK/ZEBRAK-R3/data", "bolidozor/nachodsko/NACHODSKO-R3/data"]
    for path in C:
        meteors.setPath(path)
        #for month in xrange(1,1):
        #meteors.setMonth(month)
        for day in xrange(1,31):
            try:
                meteors.setDay(day)  
                meteors.run()
                #pass
            except Exception, e:
                print e
        #meteors.cleanshoda()
        meteors.shoda()
    #meteors.cleanDB()

if __name__ == '__main__':
    main()

