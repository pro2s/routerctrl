# Define your database model over here

from google.appengine.api import users
from google.appengine.ext import ndb

class RouterState(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.TextProperty()
    service = ndb.StringProperty()
    type = ndb.StringProperty()
    file = ndb.BlobProperty()
    updated = ndb.DateTimeProperty(auto_now=True,auto_now_add=True)

class Commands(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.StringProperty()
    service = ndb.StringProperty()
    file = ndb.BlobProperty()

class Torrents(ndb.Model):
    name = ndb.StringProperty()
    hashString = ndb.StringProperty()
    status = ndb.StringProperty()
    totalSize = ndb.IntegerProperty()
    progress = ndb.FloatProperty()
