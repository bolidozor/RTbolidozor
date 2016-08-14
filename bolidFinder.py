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
import paramiko
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
    print "#>", query
    connection = mdb.connect(host="localhost", user="root", passwd="root", db="RTbolidozor", use_unicode=True, charset="utf8")
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

class GetMeteors():
    def __init__(self, path=None, year=0, month=0, day=0, minDBDuration = 0.1, minDuration=1, minDurationBolid=20, use_unicode=True, charset="utf8"):
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

        sftpUSER ='indexer'
        sftpURL = 'space.astro.cz'
        sftpKEY = '/home/roman/.ssh/indexer'

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        self.ssh.connect(sftpURL, username=sftpUSER, key_filename=sftpKEY)
        self.sftp = self.ssh.open_sftp()


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
        
    def run_indexing(self):
        print "start Indexing"
        filelist = _sql("SELECT file_index.id, file_index.id_station, file_index.filepath, file_index.filename, file_index.indextime, file_index.uploadtime FROM file_index INNER JOIN station ON station.id = file_index.id_station INNER JOIN station_type ON station_type.id = station.id_stationtype INNER JOIN projects ON projects.id = station_type.id_project WHERE file_index.uploadtime > file_index.indextime and projects.sname = 'bolidozor' AND file_index.checksum IS NOT NULL ORDER BY file_index.uploadtime;")
        for out in filelist:
            try:
                print ">>", out
                fileid=out[0]
                fileserver="space.astro.cz"
                filepath  = out[2]
                filename  = out[3]
                filestation=out[1]
                fileindext =out[4]
                fileuploadt=out[5]
                

                if "meta.csv" in filename:
                    print "PODMINKA JE SPLNENA", filename
                    #time.sleep(1)
                    data = self.sftp.open(os.path.join(filepath,filename))
                    try:
                        df = pd.read_csv(data, delimiter=";", names = ["fname", "noise", "peakf", "mag", "duration"], skiprows=1)
                        for index, row in df.iterrows():
                            # nejdrive se zkontroluje, jestli uz je v 'file_index' soubor zaznamena
                            # pokud neni vytvori se zaznam jen s 'filename_original' v tabulce 'file_index'

                            exists = _sql("SELECT count(*) FROM file_index WHERE filename_original = '%s'" %(row['fname']))
                            if exists[0][0] != 1:
                                _sql("INSERT INTO file_index SET filename_original = '%s', id_station = 0, id_server = 0" %(row['fname']))
                            else:
                                id_file = _sql("SELECT id FROM file_index WHERE filename_original = '%s';" %(row['fname']))[0][0]
                                
                                # podle typu souboru se zapise do spravne databaze
                                if "met" in row['fname']:
                                    print _sql("INSERT INTO bz_met SET id_file = %i, noise = %f, freq = %f, mag = %f, duration = %f on duplicate key update id = id;" %(id_file, row['noise'], row['peakf'], row['mag'], row['duration']))

                                elif "snap" in row['fname']:
                                    print _sql("INSERT INTO bz_snap SET id_file = %i, noise = %f, freq = %f, mag = %f on duplicate key update id = id;" %(id_file, row['noise'], row['peakf'], row['mag']))
                        
                        _sql("UPDATE file_index SET indextime = '%s' WHERE filename_original = '%s'" %(time.strftime('%Y-%m-%d %H:%M:%S'), filename))

                    except Exception, e:
                        print e
                    data.close()
                
                elif "met.fits" in filename:
                    print "METEOR FILE"
                    try:
                        data = self.sftp.open(os.path.join(filepath,filename))
                        hdulist = pyfits.open(data)
                        prihdr = hdulist[1].header
                        
                        fitsTime = prihdr['DATE']
                        dt = datetime.datetime.strptime( fitsTime, "%Y-%m-%dT%H:%M:%S" )
                        utimestamp = time.mktime(dt.timetuple())

                        print "FITS FILE META processing", filename, " from: ", utimestamp, fitsTime
                        if utimestamp > 100000000:
                            #print prihdr

                            exists = _sql("SELECT count(*) FROM file_index WHERE filename_original = '%s'" %(filename))
                            if exists[0][0] == 1:
                                _sql("UPDATE bz_met SET obstime = '%f' WHERE id_file=(SELECT id from file_index WHERE filename_original = '%s')" %(utimestamp, filename))
                                _sql("UPDATE file_index SET indextime = '%s' WHERE filename_original = '%s'" %(time.strftime('%Y-%m-%d %H:%M:%S'), filename))
                        else:
                            print "chyba", 
                            time.sleep(2)

                        data.close()
                    except Exception, e:
                        print "Err: 01", e
                
                elif "snap.fits" in filename:
                    print "met"
                    data = self.sftp.open(os.path.join(filepath,filename))
                    try:
                        hdulist = pyfits.open(data)
                        prihdr = hdulist[1].header

                        fitsTime = prihdr['DATE']
                        dt = datetime.datetime.strptime(fitsTime, "%Y-%m-%dT%H:%M:%S" )
                        utimestamp = time.mktime(dt.timetuple())

                        print "FITS FILE SNAP processing", filename, " from: ", utimestamp, fitsTime
                        if utimestamp > 100000000:

                            exists = _sql("SELECT count(*) FROM file_index WHERE filename_original = '%s'" %(filename))
                            if exists[0][0] == 1:
                                _sql("UPDATE bz_snap SET obstime = '%f' WHERE id_file=(SELECT id from file_index WHERE filename_original = '%s')" %(utimestamp, filename))
                                _sql("UPDATE file_index SET indextime = '%s' WHERE filename_original = '%s'" %(time.strftime('%Y-%m-%d %H:%M:%S'), filename))
                        else:
                            print "chyba", 
                            time.sleep(2)

                        data.close()
                    except Exception, e:
                        print e
                
                elif "raws.fits" in filename:
                    print "raw"
                    _sql("UPDATE file_index SET indextime = '%s' WHERE filename_original = '%s'" %(time.strftime('%Y-%m-%d %H:%M:%S'), filename))

                else:
                    print "unknown file"

                
            except Exception, e:
                print e


    def find_match(self):
        print "######################################################################################"
        print "######################################################################################"
        print "######################################################################################"
        print "######################################################################################"
        i = 0
        self.minDuration = float(_sql("select * from bz_param where name = 'master_met_min_duration'")[0][0])*10
        self.minDurationBolid = float(_sql("select * from bz_param where name = 'group_max_time_delta'")[0][0])*10
        self.minDuration = 1
        self.minDurationBolid = 10

        print "Minimalni delka bolidu je stanovana na ", self.minDurationBolid, "s. Minimalni delka derivatu je", self.minDuration, "s"
        #row _sql("SELECT bz_met.id, bz_met.obstime, bz_met.duration FROM bz_met JOIN station ON bz_met.id_station = station.id WHERE (bz_met.duration > %i) AND (bz_met.time BETWEEN %i AND %i) AND (station.id_stationstat = 1) ORDER BY bz_met.obstime DESC;" %(int(self.minDurationBolid), int(genfrom), int(gento+86400) ))  
        row = _sql("SELECT bz_met.id, bz_met.obstime, bz_met.duration FROM bz_met INNER JOIN file_index ON file_index.id = bz_met.id_file INNER JOIN station ON file_index.id_station = station.id WHERE (bz_met.duration > %i) AND (bz_met.obstime BETWEEN %i AND %i) AND (station.id_stationstat = 1) ORDER BY bz_met.obstime;" %(int(self.minDurationBolid), int(0), int(time.time()) ))
        lenrow = len(row)
        print row, len(row)
        print ""
        err = 30
        for meteor in row:
            print "mam vybrany meteor", meteor
            #self.dbc.execute("SELECT * FROM bz_met LEFT OUTER JOIN metalink ON metalink.link = bz_met.id WHERE (metalink.link IS NULL) AND (bz_met.time BETWEEN %f AND %f) AND (bz_met.duration > %f)  GROUP BY bz_met.id_station ORDER BY bz_met.mag DESC;" %(float(meteor[1])-err, float(meteor[1])+err, float(self.minDuration)))
            n = _sql("SELECT bz_met.id FROM bz_met INNER JOIN file_index ON file_index.id = bz_met.id_file INNER JOIN station ON file_index.id_station = station.id WHERE (bz_met.obstime BETWEEN %f AND %f) AND (bz_met.duration > %f) AND (station.id_stationstat = 1) ORDER BY bz_met.mag DESC;" %(float(meteor[1])-err, float(meteor[1])+err, float(self.minDuration)))
            print n
            print "mam %i meteoru okolo" %(len(n))
            if len(n) > 2:
                print "-------", n[0] ,float(meteor[1]), datetime.datetime.fromtimestamp(float(meteor[1])).strftime('%Y-%m-%d %X'), float(meteor[2])
                refid = n[0][0]
                for near in n:
                    try:
                        print refid, near[0]
                        _sql("INSERT INTO bz_event_met (id_event, id_file) VALUES (%i, %i);"%(refid, near[0]))
                        print "Existuje", refid, near[0]
                    except Exception, e:
                        print "Error", e
                    print near

            else:
                print "#"




    def run(self):          ########### Cteni csv souboru a ukladani do databaze

        while True:
            self.run_indexing()
            self.find_match()
            time.sleep(10)
        '''
        daypath = os.path.join(self.path, str(self.year), str(self.month).zfill(2), str(self.day).zfill(2),"/")
        print "/storage/"+str(daypath)
        files = self.sftp.listdir(os.path.join("/storage/",daypath))
        self.dbc.execute("SELECT id, filepath, filename FROM file_index WHERE id NOT IN (SELECT id_file FROM indexed);")
        for out in self.dbc.fetchall():
            file out[]
            if 'meta' in file:
                data = self.sftp.open(os.path.join(files,file))
                try:
                    print "#",
                    for line in data:
                        d = line.split(';')
                        if "met" in line:
                            try:
                                timestap =  str(calendar.timegm(time.strptime(d[0].split("_")[0][:15], "%Y%m%d%H%M%S%f"))+float(d[0].split("_")[0][14:])/10.0**len(str(d[0].split("_")[0][14:])))
                                self.dbc.execute("INSERT INTO meta (time, id_station, noise, freq, mag, duration, file) VALUES (%f, %f, %f, %f, %f, %f, '%s')"%(float(timestap), float(self.stationID), float(d[1]), float(d[2]), float(d[3]), float(d[4]), str(d[0])))
                            except Exception, e:
                                #print e, "value probably exist"
                                pass
                            #else:
                               #print "kratky"
                               #pass
                        elif "snap" in line:
                            try:
                                timestap =  str(calendar.timegm(time.strptime(d[0].split("_")[0][:15], "%Y%m%d%H%M%S%f"))+float(d[0].split("_")[0][14:])/10.0**len(str(d[0].split("_")[0][14:])))
                                self.dbc.execute("INSERT INTO snap (time, id_station, noise, file) VALUES (%f, %f, %f, '%s');"%(float(timestap), float(self.stationID), float(d[1]), str(d[0])))
                            except Exception, e:
                                #print e, "value probably exist"
                                pass
                finally:
                    self.db.commit()
                    data.close()
            '''
        print ""


    def shoda(self, start = time.time()-86400*10, stop=time.time()):
        i = 0
        print "Minimalni delka bolidu je stanovana na ", self.minDurationBolid, "s. Minimalni delka derivatu je", self.minDuration, "s"
        #sys.stdout.write("SELECT meta.id, meta.time, meta.duration FROM meta JOIN station ON meta.id_station = station.id WHERE (meta.duration) > %i AND (time BETWEEN %i AND %i) AND (station.id_stationstat = 1)  ORDER BY meta.time DESC;" %(int(self.minDurationBolid), int(genfrom), int(gento+86400) ))  
        self.dbc.execute("SELECT meta.id, meta.time, meta.duration FROM meta JOIN station ON meta.id_station = station.id WHERE (meta.duration > %i) AND (meta.time BETWEEN %i AND %i) AND (station.id_stationstat = 1) ORDER BY meta.mag DESC;" %(int(self.minDurationBolid), int(genfrom), int(gento+86400) ))  
        row = self.dbc.fetchall()
        lenrow = len(row)
        print row, len(row)
        print ""
        err = 60.0 # casova  odchylka
        for meteor in row:
            #self.dbc.execute("SELECT * FROM meta LEFT OUTER JOIN metalink ON metalink.link = meta.id WHERE (metalink.link IS NULL) AND (meta.time BETWEEN %f AND %f) AND (meta.duration > %f)  GROUP BY meta.id_station ORDER BY meta.mag DESC;" %(float(meteor[1])-err, float(meteor[1])+err, float(self.minDuration)))
            self.dbc.execute("SELECT meta.id FROM meta JOIN station ON meta.id_station = station.id WHERE (meta.time > %f) AND (meta.time < %f) AND (meta.duration > %f) AND (station.id_stationstat = 1) GROUP BY meta.id_station ORDER BY meta.mag DESC;" %(float(meteor[1])-err, float(meteor[1])+err, float(self.minDuration)))
            n = self.dbc.fetchall()
            if len(n) > 3:
                print "-------", n[0][0] ,float(meteor[1]), datetime.datetime.fromtimestamp(float(meteor[1])).strftime('%Y-%m-%d %X'), float(meteor[2])
                refid = n[0][0]
                for near in n:
                    try:
                        self.dbc.execute("INSERT INTO metalink (master, link) VALUES (%i, %i);"%(refid, near[0]))
                    except Exception, e:
                        print "Existuje", refid, near[0]
                    print near
                    self.db.commit()

            else:
                sys.stdout.write("#")
                sys.stdout.flush()
        self.db.commit()

    def stations(self):
        return _sql("SELECT observatory.name, station.name, station.id FROM station LEFT JOIN observatory ON station.id_observatory = observatory.id WHERE (station.id_stationtype = 1 OR  station.id_stationtype = 4) AND station.id_stationstat = 1;")


def main():  
    meteors = GetMeteors(None, year=0, month=0, day=0, minDBDuration = 0.1, minDuration=5, minDurationBolid=10)
    
    try:
        #meteors.createDb()
        pass
    except Exception, e:
        print "CHYBA V CREATE DB ..... ", e, " <<<<"


    BolidTimeErr = 60      #ZATIM NEFUNGUJE                 # maximalni cas mezi jednou udalosti na vice stanicich
    MasterBolidLenght = 10                  # minimalni delka alespon jednoho bodidu ze skupiny
    SlaveBolidLenght = 5                   # minimalni delka ostatnich bolidu
    DelayDownload = 86400*days                 # pokud je automaticky vyber generovani databaze, jak dlouho zpet se obnovuje DB?
    DelayMulti = 86400*days + BolidTimeErr      # pokud je automaticky vyber generovani databaze, jak dlouho zpet se hleda multibolid?

    print "-------"
    print meteors.stations()
    meteors.run()
    '''

    if meteors.getYear() == 0:
        if not "noget" in sys.argv:
            for station in meteors.stations():
                try:
                    meteors.setPath("bolidozor/%s/%s/data" %(station[0], station[1]), stationID = station[2])
                    start = int(genfrom) # aktualni datum - 5 dnu
                    stop = int(gento+86400) # do 4 dny zpet
                    for genTime in xrange(start, stop, 86400):
                        try:
                            meteors.set(year = datetime.datetime.fromtimestamp(int(genTime)).year, month = datetime.datetime.fromtimestamp(int(genTime)).month, day = datetime.datetime.fromtimestamp(int(genTime)).day)
                            meteors.run()
                        except Exception, e:
                            print e

                except Exception, e:
                    print "ERROR:", e
        else:
            print "skipping get"
        try:  
            meteors.shoda()
        except Exception, e:
            print "SHODA", e
    '''

if __name__ == '__main__':
    main()

