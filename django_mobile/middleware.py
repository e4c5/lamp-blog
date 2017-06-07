import re
from django_mobile import set_flavour, _init_flavour
from django_mobile.conf import settings

from django.utils.cache import patch_vary_headers
        
            

from django_mobile.mobilesp import  UAgentInfo

class SetFlavourMiddleware(object):
    def process_request(self, request):
        _init_flavour(request)

        if settings.FLAVOURS_GET_PARAMETER in request.GET:
            flavour = request.GET[settings.FLAVOURS_GET_PARAMETER]
            if flavour in settings.FLAVOURS:
                set_flavour(flavour, request, permanent=True)


class MobileDetectionMiddleware(object):
    
    def process_request(self, request):
        user_agent = request.META.get("HTTP_USER_AGENT")
        http_accept = request.META.get("HTTP_ACCEPT")
        
        if user_agent:
            esp = UAgentInfo(userAgent=user_agent, httpAccept=http_accept)
        
            if esp.detectTierTablet() :
                set_flavour(settings.FLAVOURS[1], request)
            else :
                if esp.detectMobileQuick() :
                    set_flavour(settings.FLAVOURS[2], request)
                else :
                    if esp.detectAndroidPhone() :
                        set_flavour(settings.FLAVOURS[2], request)
                    else :
                        #logger.debug('full')
                        set_flavour(settings.FLAVOURS[0], request)
   
    def process_response(self, request, response) :
        '''
        Patch the vary headers, because google says apps that send slightly 
        different content for mobile and web should do so.
        '''
        patch_vary_headers(response, ['User-agent'])
        return response