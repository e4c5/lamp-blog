
from google.appengine.ext import ndb

# for import export: http://stackoverflow.com/a/7944641/267540
# you will need an app sepcific password when 2step auth is used
#
# greater detail https://developers.google.com/appengine/docs/python/tools/uploadingdata
# see scrabble app for example
# /usr/local/google_appengine/appcfg.py upload_data -A dev~radithablog --url=http://localhost:7003/_ah/remote_api/ --filename=data.csv
# /usr/local/google_appengine/appcfg.py download_data -A s~radithablog --url=https://radithablog.appspot.com/_ah/remote_api/ --filename=data.csv

class Page(ndb.Model):
    '''
    The priority field is used for many different things. 
    1) Control what is displayed on the home page priorty > 0 only
    2) Analytics experiments. Highest priority item will be the
       default item. All the other are displayed only when specifically
       requested with the aid of query string params
       
    When using variations for google experiments make sure that your version
    numbers do not conflict. For example, if your default version is numbered 10
    there shouldn't be an item numbered -10
    '''
    
    title = ndb.StringProperty()
    link = ndb.StringProperty()
    image = ndb.StringProperty()   # the primary image for this page or blog post
    
    draft = ndb.BooleanProperty(indexed = True)
    blog = ndb.BooleanProperty()
    
    published_at = ndb.DateTimeProperty(indexed = False)
    timestamp = ndb.IntegerProperty(indexed = True)
    
    tags = ndb.StringProperty(repeated = True)
    
    author = ndb.StringProperty(indexed = False)
    content = ndb.TextProperty()
    
    template = ndb.StringProperty(default = 'blog-post.html', indexed = False)
    summary = ndb.StringProperty()
    
    priority = ndb.IntegerProperty(default = 1)

    
    def get_request_path(self, as_blog = None):
        ''' 
        This is one of the few places where the code could differ between
        installations.
        '''
        if as_blog == None:
            as_blog = self.blog
        if as_blog :
            return u"/" + self.published_at.strftime("%Y/%m/%d/") + self.link +u"/"
        else :
            # not sure if the trailing slash should be present here or not. will need
            # to look at all the existing apps and their pages before final decision 
            # is made. 
            # The trailing slash was temporarily removed on the 11th of may
            return u"/{0}".format(self.link)
        
        
    def get_next_link(self):
        return Page.query().filter(Page.timestamp > self.timestamp).fetch(1)
    
    def get_prev_link(self):
        return Page.query().filter(Page.timestamp < self.timestamp).fetch(1)


class Archive(ndb.Model):
    year = ndb.IntegerProperty(indexed = False)
    month = ndb.IntegerProperty(indexed = False)
    dt = ndb.DateProperty()
    
    
class Tag(ndb.Model):
    name = ndb.StringProperty(repeated = True)
    counter = ndb.IntegerProperty(default = 0)
    description = ndb.StringProperty()
    
    # if a title is available it's recommended to use that on web pages/blog posts etc
    # when a title is not available use the first item in the name array.
    title = ndb.StringProperty()
