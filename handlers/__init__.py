#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import pymysql.cursors
import os
import tornado
from requests_oauthlib import OAuth2Session

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):

        #print self.options()
        #print help(self.options())
        print "----------------------"
        login = self.get_secure_cookie("login")
        token = self.get_secure_cookie("token")
        if not login:
            return None
        else:
            return login

    def get_user(self):
        login = self.get_secure_cookie("login")
        if not login:
            return None
        else:
            return login
def sendMail(to, subject = "MLABvo", text = "No content"):
        message="""From:  MLAB distributed measurement systems <dms@mlab.cz>
To: %s
MIME-Version: 1.0
Content-type: text/html
Subject: %s
""" %(to, subject)
        message += text
        print"-----"
        print to
        print message
        print"-----"
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail("MLAB distributed measurement systems <dms@mlab.cz>", to, message )
        smtp.close()


def _sql(query, read=False, db="MLABvo"):
        #print "#>", query
        connection = pymysql.connect(host="localhost", user="root", passwd="root", db=db, use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
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
        #print result
        return result


def wwwCleanName(string):
    return ''.join( c for c in string if c not in '?:!/;-_#$%^!@., (){}[]' )


def loged():
    pass