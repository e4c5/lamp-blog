from google.appengine.ext import ndb

class Faq(ndb.Model):
    ''' For FAQ entries. 
    The model is very similar to Page but these items can be embedded inside 
    individual web pages
    '''
    
    title = ndb.StringProperty()
    slug = ndb.StringProperty()
    
    draft = ndb.BooleanProperty(indexed = True)
    
    published_at = ndb.DateTimeProperty(indexed = False)
    timestamp = ndb.IntegerProperty(indexed = True)
    
    tags = ndb.StringProperty(repeated = True)
    
    author = ndb.StringProperty(indexed = False)
    content = ndb.TextProperty()
    priority = ndb.IntegerProperty(default = 1)
    
    def link(self):
        print 'am I not being called?', self.title, self.slug
        return self.slug
    
    
    