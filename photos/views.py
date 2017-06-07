import os
import re
import time
import urllib
import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from google.appengine.api import files, images
from google.appengine.ext import blobstore
from google.appengine.api import memcache
from google.appengine.api import users

from pages.admin_views import is_authorized_user
from photos import app_settings
from photos.models import UserImage


MIN_FILE_SIZE = 1  # bytes
MAX_FILE_SIZE = 5000000  # bytes
IMAGE_TYPES = {
    '.gif': 'image/gif',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.xpng': 'image/png',
    '.jpg': 'image/jpg'}
THUMBNAIL_MODIFICATOR = '=s80'  # max width / height


class UploadHandler(object):

    def validate(self, file, name):
        (root, ext) = os.path.splitext(name.lower())
        print 'ext ', ext
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        elif ext not in IMAGE_TYPES.keys():
            file['error'] = 'invalid file type'
        else:
            return True

        return False

    def auth_check(self, request):
        if is_authorized_user():
            return True
        else:
            hostname = request.get_host()
            if hostname == 'localhost:7003':
                return True

    def write_blob(self, data, info):
        '''
        This is where the image is chucked into the blobstore. The approach
        being used is not the one that's recommened in the google docs. Their
        method is to use the direct upload url. However direct upload urls
        do not seem to work with CORS (and this is code That I have copy and
        pasted from a project that needed CORS
        '''
        (root, ext) = os.path.splitext(info['name'])

        img = images.Image(data)
        if img:
            blob = files.blobstore.create(
                _blobinfo_uploaded_filename=info['name'],
                mime_type=IMAGE_TYPES[ext.lower()]
            )

            with files.open(blob, 'a') as f:
                f.write(data)
            files.finalize(blob)

            key = files.blobstore.get_blob_key(blob)
            return key, img

        return None, None

    def save_serving_url(self, blob_key, img):
        print blob_key
        hostname = self.request.get_host()
        url = images.get_serving_url(
            blob_key,
            secure_url=hostname.startswith('https')).replace(
            'http://0.0.0.0:7003',
            'http://blob.lazycite.com:7003')
        # create a record on our own table (the one that's automatically
        # created is read only). Then chuck it into memcache with a short
        # TTL for good measure.

        print url
        u = users.get_current_user()
        if u:
            uploader = u.email()
        else:
            uploader = ""

        user_image = UserImage(
            blob_key=str(blob_key),
            uploader=uploader,
            width=img.width,
            capturedAt=int(
                time.time()*1000),
            height=img.height,
            serving_url=url,
            gallery=app_settings.DEFAULT_GALLERY)
        user_image.put()

        return url

    def handle_upload(self):
        results = []
        hostname = self.request.get_host()
        protocol = "http://" if self.request.META.get(
            'HTTPS') == 'off' else 'https://'

        for wtf, file in self.request.FILES.iteritems():
            result = {}
            result['name'] = re.sub(
                r'^.*\\',
                '',
                file.name
            )
            result['size'] = file.size

            if self.validate(result, file.name):
                blob_key, img = self.write_blob(file.read(), result)

                try:
                    result['url'] = self.save_serving_url(blob_key, img)

                    result['thumbnailUrl'] = result[
                        'url'] + THUMBNAIL_MODIFICATOR
                    result['deleteType'] = 'DELETE'
                    result[
                        'deleteUrl'] = u"%s%s/delete/%s/" % (protocol, hostname, urllib.quote(str(blob_key), ''))
                except Exception as e:
                    print e
                    # Could not get an image serving url, which probably means this is not
                    # a valid file after all.
                    file['error'] = 'invalid file type'
                    blobstore.delete(blob_key)

            results.append(result)

        return results

    def delete(self, key, force=False):
        '''
        We will delete an item if the request is a CORS request from the user or
        a request from the admin with a secret key
        '''

        if key:
            try:
                ui = UserImage.query(UserImage.blob_key == key).fetch()
                ui = ui[0]
                if ui.user == self.auth_user:
                    if ui.discard or force:
                        blobstore.delete(key)
                        ui.key.delete()

                        memcache.delete(key)  # @UndefinedVariable

                        return HttpResponse(json.dumps({'status': 'Ok'}))
            except Exception as e:
                print e
                pass
        return HttpResponse(json.dumps({'status': 'error'}))

def upload_handler(request):
    '''
    Accepts a file upload but the  The donkey work is done in the UploadHandler class
    '''
    uploader = UploadHandler()

    if request.method == 'GET':

        if uploader.auth_check(request):
            images = UserImage.query()
            return render_to_response('upload.html', {'images': images},
                                      context_instance=RequestContext(request))
        else:
            return HttpResponse(
                "<a href='{}'>login</a>".format(users.create_login_url('/')))

    else:

        uploader.request = request
        if uploader.auth_check(request):
            # only authenticated users can do anything usefull

            result = {'files': uploader.handle_upload()}
            s = json.dumps(result, separators=(',', ':'))
            redirect = request.GET.get('redirect')
            if redirect:
                return HttpResponseRedirect(str(
                    redirect.replace('%s', urllib.quote(s, ''), 1)
                ))

            return HttpResponse(s)
        else:
            return HttpResponse('Authentication Failed')
