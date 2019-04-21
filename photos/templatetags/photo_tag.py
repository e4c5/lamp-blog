'''
GAE doesn't really have a decent way to do an order by random. 
so our solution is to cycle through all the available photos. The
last retrieved ID will be saved into memcache. If we don't have
value in memcache, we start all over again from the first one
'''

from django.template import Library
from django.contrib.auth.models import User
from google.appengine.ext import ndb
from google.appengine.api import memcache
from photos.models import UserImage


register = Library()

@register.simple_tag()
def cycle_photo():
    last = memcache.get('slsl:last_photo',0)  # @UndefinedVariable
     
    userimage = UserImage.query().filter(UserImage.capturedAt > last).order(UserImage.capturedAt).fetch(1)
    try :
        if userimage :
            userimage = userimage[0]
            memcache.set('slsl:last_photo', userimage.capturedAt)  # @UndefinedVariable
            return '<img src="%s" />' % userimage.serving_url
        else : 
            last = 0
            userimage = UserImage.query().filter(UserImage.capturedAt > last).order(UserImage.capturedAt).fetch(1)
            userimage = userimage[0]
            memcache.set('slsl:last_photo', userimage.capturedAt)  # @UndefinedVariable
            return '<img src="%s" />' % userimage.serving_url
        
    except Exception, e:
        print e
        pass
    
    return ''