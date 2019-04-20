import os
if os.environ.get('SERVER_SOFTWARE','').startswith('Development'):
    remoteapi_CUSTOM_ENVIRONMENT_AUTHENTICATION = (
       'REMOTE_ADDR', ['127.0.0.1'])



# [START vendor]
from google.appengine.ext import vendor

vendor.add('lib')
# [END vendor]