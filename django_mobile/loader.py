from django.template import TemplateDoesNotExist
from django.template.loader import find_template_loader, BaseLoader
from django_mobile import get_flavour
from django_mobile.conf import settings



class Loader(BaseLoader):
    is_usable = True

    def __init__(self, *args, **kwargs):
        loaders = []
        for loader_name in settings.FLAVOURS_TEMPLATE_LOADERS:
            loader = find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        self.template_source_loaders = tuple(loaders)
        super(BaseLoader, self).__init__(*args, **kwargs)


    def _prepare_template_name(self, template_name, flavour):
        
        template_name = u'%s/%s' % (flavour, template_name)
        if settings.FLAVOURS_TEMPLATE_PREFIX:
            template_name = settings.FLAVOURS_TEMPLATE_PREFIX + template_name

        return template_name


    def prepare_template_name(self, template_name):
        return self._prepare_template_name(template_name, get_flavour())
    
    
    def load_template(self, template_name, template_dirs=None):
        prep_name = self.prepare_template_name(template_name)
        for loader in self.template_source_loaders:
            try:
                #logger.debug('load template %s, %s ' % (template_dirs, template_name));
                return loader(prep_name, template_dirs)
            except TemplateDoesNotExist:
                pass
        '''
        Special case. is that the template for the tablet could not be found.
        In most cases the mobile template can be used in it's place.
        '''
        if get_flavour() == 'tablet':
            #logger.debug('Couldnt find the right template for use on the tablet')
            template_name = self._prepare_template_name(template_name,'mobile')
            for loader in self.template_source_loaders:
                try:
                    #logger.debug('load template %s, %s ' % (template_dirs, template_name));
                    return loader(template_name, template_dirs)
                except TemplateDoesNotExist:
                    pass
        
        '''
        No template available 
        '''    
        raise TemplateDoesNotExist("Tried %s" % template_name)

    
    def load_template_source(self, template_name, template_dirs=None):
        template_name = self.prepare_template_name(template_name)
        for loader in self.template_source_loaders:
            if hasattr(loader, 'load_template_source'):
                try:
                    return loader.load_template_source(template_name, template_dirs)
                except TemplateDoesNotExist:
                    pass
        raise TemplateDoesNotExist("Tried %s" % template_name)
