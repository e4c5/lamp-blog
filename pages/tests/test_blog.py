import os, sys
import json
import resource  # @UnresolvedImport

if __name__ == '__main__':
    # Setup environ
    sys.path.append(os.getcwd())

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pages.settings")
    
import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed

from pages.models import Tag, Page
from django.test.client import RequestFactory
from pages.views import edit_page, create_link


class BlogTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

    def tearDown(self):
        self.testbed.deactivate()
        
    
    def testSlug(self):
        p = Page(link = 'bada')
        p.put()
        self.assertEqual(1, len(Page.query().fetch(2)))
        
        link = create_link('bada')
        self.assertNotEqual(link, 'bada')
        
        print link
        
    def testInsertEntity(self):
        print 'a'
        t = Tag(name = 'a', counter = 1)
        t.put()
        self.assertEqual(1, len(Tag.query().fetch(2)))
        factory = RequestFactory();
        request = factory.post('/',{"sharedWith":'jabber@raditha.com', "body":"nothing to see here",'post':True});
        request.session = {}

        self.testbed.setup_env(USER_EMAIL='usermail@gmail.com',USER_ID='1', USER_IS_ADMIN='1')
    
        resp = edit_page(request)
    
    
if __name__ == '__main__':
    unittest.main()