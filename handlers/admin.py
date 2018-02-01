#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.escape
from tornado import web
from tornado import websocket
from . import _sql, wwwCleanName, BaseHandler
import json


class admin(BaseHandler):
    def get(self, param=None):
        if not self.current_user:
            self.write("... co tady děláš? Nejdříve se musíš přihlásit")
        else:
            self.render("admin.hbs", title="Bolidozor | admin", _sql = _sql, parent=self)


class sendEmail(BaseHandler):
    def get(self, param=None):
        if not self.current_user:
            self.write("... co tady děláš? Nejdříve se musíš přihlásit")
        else:
            self.render("admin.sendEmail.hbs", title="SendEmail | admin", _sql = _sql, parent=self)
    

class new(BaseHandler):
    def get(self, param=None):
        if not self.current_user:
            self.write("... co tady děláš? Nejdříve se musíš přihlásit")
        else:
            self.me = _sql("SELECT id, login, name, email, service, date_joined, last_login, is_staff, is_active, is_superuser FROM MLABvo.bolidozor_user WHERE login='%s';" %(self.current_user))[0]
            if self.me['is_superuser'] == 1:
                self.obs = _sql("SELECT id, name FROM bolidozor_observatory;")
                self.owners = _sql("SELECT id, name FROM bolidozor_user;")
            else:
                self.obs = _sql("SELECT id, name FROM bolidozor_observatory WHERE owner = '%s';" %(self.me['id']))
                self.owners = ([self.me['id'], self.me['name']])
                self.owners = _sql("SELECT id, name FROM bolidozor_user WHERE login='%s';" %(self.current_user))

            print "vypis>>> me, obs, owners"
            print self.me
            print self.obs
            print self.owners

            if 'station' in param:
                self.render("admin_new_station.hbs", title="Bolidozor | admin", _sql = _sql, parent=self)
            elif 'observatory' in param:
                self.render("admin_new_observatory.hbs", title="Bolidozor | admin", _sql = _sql, parent=self)


    def post(self, param=None):
        self.me = _sql("SELECT id, login, name, email, service, date_joined, last_login, is_staff, is_active, is_superuser FROM MLABvo.bolidozor_user WHERE login='%s';" %(self.current_user))[0]   
        if 'station' in param:
            print param
            name = self.get_argument("name", "NULL")
            namesimple = self.get_argument("namesimple", "NULL")
            status= self.get_argument("status", 0)
            observatory = self.get_argument("observatory", "NULL")
            web = self.get_argument("web", "NULL")
            owner = self.get_argument("owner", self.me['id'])
            hardware = self.get_argument("hardware", "NULL")
            comment = self.get_argument("comment", "NULL")

            print _sql("INSERT INTO bolidozor_station (`name`, `namesimple`, `status`, `observatory`, `web`, `owner`, `hardware`, `comment`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"
                %(name, namesimple, status, observatory, web, owner, hardware, comment))
            self.redirect("/admin/")
        
        elif 'observatory' in param:
            print param
            name = self.get_argument("name", "NULL")
            namesimple = self.get_argument("namesimple", "NULL")
            lat= self.get_argument("lat", 0)
            lon = self.get_argument("lon", "NULL")
            alt = self.get_argument("alt", "NULL")
            owner = self.get_argument("owner", self.me['id'])
            www = self.get_argument("www", "NULL")
            comment = self.get_argument("comment", "NULL")

            print _sql("INSERT INTO bolidozor_observatory (`name`, `namesimple`, `lat`, `lon`, `alt`, `www`, `comment`, `owner`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"
                %(name, namesimple, lat, lon, alt, www, comment, owner))
            self.redirect("/admin/")