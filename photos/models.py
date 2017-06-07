from google.appengine.ext import ndb

class UserImage(ndb.Model):
    blob_key = ndb.StringProperty()
    serving_url = ndb.StringProperty()
    uploader = ndb.StringProperty()
    capturedAt = ndb.IntegerProperty()
    gallery = ndb.StringProperty()
    caption = ndb.StringProperty()
    featured = ndb.BooleanProperty()
    height = ndb.IntegerProperty()
    width = ndb.IntegerProperty()
    
