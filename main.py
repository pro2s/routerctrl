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
    "url":"/",
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
class UserPrefs(ndb.Model):
    userid = ndb.StringProperty()

def update_online():
    date = datetime.datetime.now()
    memcache.set('last_online', date , 900)
    
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
	user = users.get_current_user()
        if user:
            login = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            login = ('<a href="%s">Sign in</a>.' % users.create_login_url('/'))

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

class RegHandler(BaseHandler):        
    def get(self):
        template_values = {
        'menu':MENU,
        'active':'reg',
        }
        template = JINJA_ENVIRONMENT.get_template('index.tpl')
        html = template.render(template_values)
        self.response.write(html)
	user = users.get_current_user()
	if user:
	    q = UserPrefs()
	    q.userid = user.user_id()
	    q.put()
        
class MainHandler(BaseHandler):
    def get(self):
        update_online()
        router = RouterState.query().filter(RouterState.service == "openwrt")
        template_values = {
        'menu':MENU,
        'active':'index',
        'router':router,
        }
        template = JINJA_ENVIRONMENT.get_template('index.tpl')
        html = template.render(template_values)
        self.response.write(html)

class TorrentHandler(BaseHandler):
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
        template_values = {
        'c_name':comands_name,
        'c_type':comands_type,
        'torrent':torrent,
        'torrents':torrents,
        'commands':commands,        
        'menu':MENU,
        'active':'torrent',
        }
        template = JINJA_ENVIRONMENT.get_template('torrent.tpl')
        html = template.render(template_values)
        self.response.write(html)


class AddTorrent(webapp2.RequestHandler):
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
    def get(self):
        update_online()
        data = RouterState.query(RouterState.service == "openwrt", RouterState.name == "traffic")
        trafik = data.fetch(1)
        img = ''
        
        if trafik:
            img = '<div class="span12"><img src="data:image/png;base64,'+trafik[0].value+'" alt="" /></div>'
        template_values = {
        'menu':MENU,
        'active':'trafik',
        'raw_content':img,
        }
        template = JINJA_ENVIRONMENT.get_template('base.tpl')
        html = template.render(template_values)
        self.response.write(html)

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
    ('/', MainHandler),
    ('/torrent/', TorrentHandler),
    ('/registration/', RegHandler),
    ('/trafik/', TrafikHandler),
    ('/add', AddTorrent),
    ('/online', OnlineHandler),
], debug=True,config=config)
