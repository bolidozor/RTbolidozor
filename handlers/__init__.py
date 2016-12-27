

import MySQLdb as mdb
import os


def _sql(query, read=False, db="MLABvo"):
        print "#>", query
        connection = mdb.connect(host="localhost", user="root", passwd="root", db=db, use_unicode=True, charset="utf8")
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

def _sqlM(query, read=False):
        print "#>", query
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


def wwwCleanName(string):
    return ''.join( c for c in string if c not in '?:!/;-_#$%^!@., (){}[]' )
