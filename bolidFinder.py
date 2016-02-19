#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import paramiko
import MySQLdb as mdb
import time
import datetime
import calendar

##**************************************
##**************************************
##
##
    days = 65
    gento = time.time()
    genfrom = gento - 86400*days
##
##
##**************************************
##**************************************

class GetMeteors():
    def __init__(self, path=None, year=0, month=0, day=0, minDBDuration = 0.1, minDuration=1, minDurationBolid=20, use_unicode=True, charset="utf8"):
        self.db = mdb.connect(host="localhost", user="root", passwd="root", db="RTbolidozor")
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
            self.dbc.execute('DROP TABLE IF EXISTS user;')
            self.dbc.execute('DROP TABLE IF EXISTS observatory;')
            self.dbc.execute('DROP TABLE IF EXISTS station;')
            self.dbc.execute('DROP TABLE IF EXISTS meta;')
            self.dbc.execute('DROP TABLE IF EXISTS snap;')
            self.dbc.execute('DROP TABLE IF EXISTS file_location;')
            self.dbc.execute('DROP TABLE IF EXISTS station_type;')
            self.dbc.execute('DROP TABLE IF EXISTS station_status;')
            self.dbc.execute('DROP TABLE IF EXISTS user_observatory;')
            self.dbc.execute('DROP TABLE IF EXISTS metalink;')

            self.db.commit()
        except Exception, e:
            print e
        

        self.dbc.execute('CREATE TABLE user ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'name VARCHAR(32) UNIQUE KEY, '
                            'r_name VARCHAR(32), '
                            'email VARCHAR(128), '
                            'pass VARCHAR(128), '
                            'id_astrozor TINYINT UNSIGNED, '
                            'www VARCHAR(255),'
                            'text VARCHAR(500)'
                        ');')

        self.dbc.execute('INSERT INTO user'
                            '(name, r_name, email, pass, id_astrozor, www, text) VALUES'
                            '("roman-dvorak", "Roman Dvorak", "roman-dvorak@email.cz", "pass", 11, "", ""),'
                            '("kaklik", "Jakub Kakona", "email@email.cz", "pass", 3, "", "")'
                        ';')
        
        self.dbc.execute('CREATE TABLE observatory ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'name VARCHAR(32) UNIQUE KEY, '
                            'id_obstype SMALLINT UNSIGNED DEFAULT 1 NOT NULL, '
                            'lat DECIMAL(8,5), '
                            'lon DECIMAL(8,5), '
                            'alt SMALLINT, '
                            'text VARCHAR(500)'
                        ');')

        self.dbc.execute('INSERT INTO observatory'
                            '(name, id_obstype, lat, lon, alt, text) VALUES'
                            '("svakov", 1, 14.59, 48.34, 450, "Sobeslav"),'
                            '("ZVPP", 1, 14.8, 49.0, 400, "Ceske Budejovice"),'
                            '("ONDREJOV", 1, 15, 50.34, 450, "Ondrejov")'
                        ';')
        

        self.dbc.execute('CREATE TABLE station ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'name VARCHAR(32) UNIQUE KEY, '
                            'id_observatory SMALLINT UNSIGNED NOT NULL, '
                            'id_stationstat SMALLINT UNSIGNED DEFAULT 1 NOT NULL, '
                            'id_stationtype SMALLINT UNSIGNED DEFAULT 1 NOT NULL, '
                            'handler VARCHAR(64), '
                            'text VARCHAR(500) '
                            #'FOREIGN KEY (id_observatory) REFERENCES observatory(id), '
                            #'FOREIGN KEY (id_stationstat) REFERENCES station_status(id), '
                            #'FOREIGN KEY (id_stationtype) REFERENCES station_type(id) '
                        ');')

        self.dbc.execute('INSERT INTO station'
                            '(name, id_observatory, id_stationstat, id_stationtype, text) VALUES'
                            '("SVAKOV-R7", 1, 1, 1, "RMDS02D"),'
                            '("ZVPP-R3", 2, 3, 1, "RMDS01B"),'
                            '("ZVPP-R4", 2, 1, 1, "RMDS02D"),'
                            '("space.astro.cz", 3, 2, 2, "space.astro.cz")'
                        ';')
        

        self.dbc.execute('CREATE TABLE meta ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'time DECIMAL(14,4) UNSIGNED NOT NULL, '
                            'noise DECIMAL(6,4) UNSIGNED, '
                            'freq DECIMAL(6,0) UNSIGNED, '
                            'mag DECIMAL(6,4) UNSIGNED, '
                            'duration DECIMAL(8,5) UNSIGNED,'
                            'file VARCHAR(64) UNIQUE KEY, '
                            'id_station TINYINT UNSIGNED NOT NULL, '
                            'id_fileloc TINYINT UNSIGNED DEFAULT 0 '
                        ');')
        
        self.dbc.execute('CREATE TABLE snap ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'time DECIMAL(14,4) UNSIGNED NOT NULL, '
                            'noise DECIMAL(6,4) UNSIGNED, '
                            #'freq DECIMAL(6,0) UNSIGNED, '
                            #'mag DECIMAL(6,4) UNSIGNED, '
                            'file VARCHAR(64) UNIQUE KEY, '
                            'id_station TINYINT UNSIGNED NOT NULL, '
                            'id_fileloc TINYINT UNSIGNED DEFAULT 0 '
                        ');')

        self.dbc.execute('CREATE TABLE file_location ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'id_station INT(6) UNSIGNED, '
                            'name VARCHAR(64), '
                            'text VARCHAR(500)'
                        ');')
        
        self.dbc.execute('CREATE TABLE station_type ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'name VARCHAR(64), '
                            'text VARCHAR(500)'
                        ');')

        self.dbc.execute('CREATE TABLE station_status ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'name VARCHAR(64), '
                            'text VARCHAR(500)'
                        ');')

        self.dbc.execute('CREATE TABLE user_observatory ('
                            'id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'id_user INT UNSIGNED NOT NULL, '
                            'id_station INT UNSIGNED NOT NULL '
                            #'FOREIGN KEY (id_user) REFERENCES user(id), '
                            #'FOREIGN KEY (id_station) REFERENCES station(id)'
                        ');')
        
        self.dbc.execute('CREATE TABLE metalink ( '
                            'id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL, '
                            'master INT UNSIGNED NOT NULL, '
                            'link INT UNSIGNED NOT NULL'
                        ');')
        
        self.db.commit()
        


    def run(self):          ########### Cteni csv souboru a ukladani do databaze
        daypath = self.path+"/"+str(self.year)+"/"+str(self.month).zfill(2)+"/"+str(self.day).zfill(2)+"/"
        print "/storage/"+str(daypath)
        files = self.ftp.listdir("/storage/"+str(daypath))
        print files
        for file in files:
            if 'meta' in file:
                data = self.ftp.open("/storage/"+str(daypath)+file)
                try:
                    print "#",
                    for line in data:
                        d = line.split(';')
                        if "met" in line:
                            try:
                                timestap =  str(calendar.timegm(time.strptime(d[0].split("_")[0][:15], "%Y%m%d%H%M%S%f"))+float(d[0].split("_")[0][14:]))
                                self.dbc.execute("INSERT INTO meta (time, id_station, noise, freq, mag, duration, file) VALUES (%f, %f, %f, %f, %f, %f, '%s')"%(float(timestap), float(self.stationID), float(d[1]), float(d[2]), float(d[3]), float(d[4]), str(d[0])))
                            except Exception, e:
                                #print e, "value probably exist"
                                pass
                            #else:
                               #print "kratky"
                               #pass
                        elif "snap" in line:
                            try:
                                timestap =  str(calendar.timegm(time.strptime(d[0].split("_")[0][:15], "%Y%m%d%H%M%S%f"))+float(d[0].split("_")[0][14:]))
                                self.dbc.execute("INSERT INTO snap (time, id_station, noise, file) VALUES (%f, %f, %f, '%s');"%(float(timestap), float(self.stationID), float(d[1]), str(d[0])))
                            except Exception, e:
                                #print e, "value probably exist"
                                pass
                finally:
                    self.db.commit()
                    data.close()
        print ""


    def shoda(self, start = time.time()-86400*10, stop=time.time()):
        print "Minimalni delka bolidu je stanovana na ", self.minDurationBolid, "s. Minimalni delka derivatu je", self.minDuration, "s"
        sys.stdout.write("SELECT id, time, duration FROM meta WHERE duration > %i AND time > %i AND time < %i ORDER BY meta.duration DESC;" %(int(self.minDurationBolid), int(genfrom), int(gento+86400) ))  
        self.dbc.execute("SELECT id, time, duration FROM meta WHERE duration > %i AND time > %i AND time < %i ORDER BY meta.duration DESC;" %(int(self.minDurationBolid), int(genfrom), int(gento+86400) ))  
        row = self.dbc.fetchall()
        print row
        err = 60.0 # casova  odchylka
        for meteor in row:
            self.dbc.execute("SELECT * FROM meta WHERE time > "+str(float(meteor[1])-err)+" AND time <"+str(float(meteor[1])+err)+ " AND duration > "+ str(self.minDuration) +" GROUP BY id_station ORDER BY mag DESC;")
            n = self.dbc.fetchall()
            if len(n) >> 2:
                print "-------", n[0][0] ,float(meteor[1]), datetime.datetime.fromtimestamp(float(meteor[1])).strftime('%Y-%m-%d %X'), float(meteor[2])
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

    def stations(self):
        self.dbc.execute("SELECT observatory.name, station.name, station.id FROM station LEFT JOIN observatory ON station.id_observatory = observatory.id WHERE station.id_stationtype = 1;")
        return self.dbc.fetchall()


def main():  
    meteors = GetMeteors("bolidozor/ZVPP/ZVPP-R3/data", year=0, month=0, day=0, minDBDuration = 0.1, minDuration=5, minDurationBolid=15)
    
    try:
        #meteors.createDb()
        pass
    except Exception, e:
        print "CHYBA V CREATE DB ..... ", e, " <<<<"


    days = 4
    BolidTimeErr = 60      #ZATIM NEFUNGUJE                 # maximalni cas mezi jednou udalosti na vice stanicich
    MasterBolidLenght = 15                  # minimalni delka alespon jednoho bodidu ze skupiny
    SlaveBolidLenght = 10                   # minimalni delka ostatnich bolidu
    DelayDownload = 86400*days                 # pokud je automaticky vyber generovani databaze, jak dlouho zpet se obnovuje DB?
    DelayMulti = 86400*days + BolidTimeErr      # pokud je automaticky vyber generovani databaze, jak dlouho zpet se hleda multibolid?

    print "-------"
    print meteors.stations()

    if meteors.getYear() == 0:
        for station in meteors.stations():
        #for station in []:
            try:
                meteors.setPath("bolidozor/%s/%s/data" %(station[0], station[1]), stationID = station[2])
                start = int(genfrom)
                stop = int(gento+86400)
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

if __name__ == '__main__':
    main()

