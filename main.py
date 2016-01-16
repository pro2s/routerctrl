#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-

from ReSTify.model import *
import codecs 
import base64
import webapp2
import feedparser
import json
import re
import jinja2
import os
import datetime
from md5 import md5
from webapp2_extras import sessions

from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import ndb

urlfetch.set_default_fetch_deadline(10)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader([os.path.join(os.path.dirname(__file__),"templates"),],encoding='utf-8'),
    extensions=['jinja2.ext.autoescape'])

MENU = [
    {
    "id":"about",
    "name":u"О системе",
    "url":"/",
    },
    {
    "id":"reg",
    "name":u"Зарегестрироватся",
    "url":"/registration/",
    },
    {
    "id":"index",
    "name":u"Роутер",
    "url":"/router/",
    },
    {
    "id":"torrent",
    "name":u"Торент",
    "url":"/torrent/",
    },
    {
    "id":"trafik",
    "name":u"Трафик",
    "url":"/trafik/",
    },
]

login  = ""

class UserPrefs(ndb.Model):
    userid = ndb.StringProperty()
    registred = ndb.BooleanProperty()
    apikey = ndb.StringProperty()

def update_online():
    date = datetime.datetime.now()
    memcache.set('last_online', date , 900)
    
def CreaetePrefs(user_id):
    uprefs = UserPrefs()
    uprefs.userid = user_id
    uprefs.registred = False
    uprefs.apikey = "default-" + md5(user["nickname"]).hexdigest() + "-00"
    uprefs.put()   
    return uprefs

def user_required(handler):
    """
        Decorator for checking if there's a user associated with the current session.
        Will also fail if there's no session present.
    """
    def check_login(self, *args, **kwargs):
        self.user = users.get_current_user()
        if self.user :
            self.uprefs = UserPrefs.query(UserPrefs.userid == self.user.user_id()).get()
            if self.uprefs is None:
                self.uprefs = UserPrefs(self.user.user_id())
            return handler(self, *args, **kwargs)
        else:
            # If handler has no login_url specified invoke a 403 error
            try:
                self.redirect("/", abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)
	
    return check_login
    
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
 
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
    
    def render_template(self, filename, **template_args):
        user = {}
        uprefs = {}
        menu = MENU[:2]
        if users.get_current_user() is None:
            user = {
            "logon":False,
            "login_url": users.create_login_url(self.request.uri)
            }
            MENU[1]["name"] = u"Регистрация"
        else:
            MENU[1]["name"] = u"Данные пользователя"
            user = {
            "logon":True,
            "email": users.get_current_user().email(),
            "user_id": users.get_current_user().user_id(),
            "nickname": users.get_current_user().nickname(),
            "logout_url": users.create_logout_url("/"),
            }
            uprefs = UserPrefs.query(UserPrefs.userid == user["user_id"]).get()
            if uprefs is None: 
                uprefs = UserPrefs(user["user_id"])
            if uprefs.registred:
                menu = MENU # TODO: Generate menu depends by api-keys  
                
        template = JINJA_ENVIRONMENT.get_template(filename)
        html = template.render(menu = menu, uprefs = uprefs, user = user , **template_args)
        self.response.write(html)

class RegHandler(BaseHandler):        
    def get(self):
        context = {
        'active':'reg',
        }
        self.render_template('user.tpl',**context)
        
    @user_required
    def post(self):
        reg = self.request.get("reg", default_value="no")        
        if reg == "yes":
            self.uprefs.registred = True
            self.uprefs.put()   
        self.redirect("/registration/")    

class AboutHandler(BaseHandler):
    def get(self):
        
        context = {
        'active':'about',
        }
        
        self.render_template('about.tpl',**context)
        
class MainHandler(BaseHandler):
    @user_required
    def get(self):
        update_online()
        router = RouterState.query().filter(RouterState.service == "openwrt")
        context = {
        'active':'index',
        'router':router,
        'login':login,
        }
        self.render_template('index.tpl',**context)

class TorrentHandler(BaseHandler):
    @user_required
    def get(self):
        update_online()
        commands = Commands.query().filter(RouterState.service == "transmission")
        torrent = RouterState.query().filter(RouterState.service == "transmission")
        torrents = Torrents.query()
        comands_name = {
        'add':u'Добавить торрент',
        }
        comands_type = {
        'file':u'файл',
        }
        context = {
        'c_name':comands_name,
        'c_type':comands_type,
        'torrent':torrent,
        'torrents':torrents,
        'commands':commands,        
        'active':'torrent',
        }
        
        self.render_template('torrent.tpl',**context)
        

class AddTorrent(webapp2.RequestHandler):
    @user_required
    def post(self):
        command = Commands()
        command.name = "add"
        command.value = "file"
        command.service = "transmission"
        file = base64.b64encode(str(self.request.get('file')))
        command.file = file
        command.put()
        self.redirect("/torrent/")

class TrafikHandler(BaseHandler):
    @user_required
    def get(self):
        update_online()
        data = RouterState.query(RouterState.service == "openwrt", RouterState.name == "traffic")
        trafik = data.fetch(1)
        img = ''
        
        if trafik:
            img = '<div class="span12"><img src="data:image/png;base64,'+trafik[0].value+'" alt="" /></div>'
        context = {
        'active':'trafik',
        'raw_content':img,
        }
        self.render_template('base.tpl',**context)
        
class OnlineHandler(BaseHandler):
    def get(self):
        online_date = memcache.get('last_online')
        if online_date is None:
            self.response.write('-1')
        else:
            date = datetime.datetime.now()
            delta = date - online_date
            self.response.write(str(delta.seconds))
            
        
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}        
app = webapp2.WSGIApplication([
    ('/router/', MainHandler),
    ('/torrent/', TorrentHandler),
    ('/', AboutHandler),
    ('/registration/', RegHandler),
    ('/trafik/', TrafikHandler),
    ('/add', AddTorrent),
    ('/online', OnlineHandler),
], debug=True,config=config)
