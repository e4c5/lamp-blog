from django import forms

attrs_dict = { 'class': 'form-control' }

class FaqForm(forms.Form):
    '''
    To create a FAQ entry
    '''
    title = forms.CharField(widget = forms.TextInput(attrs =attrs_dict),
                           label=u'Page title')

    draft = forms.BooleanField(required = False, label=u'This is a draft', initial = True)
    
    slug = forms.CharField(widget = forms.HiddenInput(),  required = False)
    
    published_at = forms.DateTimeField(label=u'Publication time.', required = False,
                            widget=forms.TextInput({'class': 'form-control'}))
    
    tags = forms.CharField(widget=forms.TextInput(attrs = { 'class': 'form-control', 'placeholder': "Please separate tags with  a ','" }),
                           label=u'Tags', required = False)
    
    content = forms.CharField(widget=forms.Textarea({ 'class': 'form-control','rows': 15 }),
                           label=u'Content')
    
    timestamp = forms.IntegerField(widget = forms.HiddenInput())
    key = forms.IntegerField(widget = forms.HiddenInput(), required = False)
    priority = forms.IntegerField( label = u'sort order', initial = 1, widget=forms.TextInput({'class': 'form-control'}))
        
        
class PageForm(forms.Form) :
    '''
    This form is used to create or edit a web page or blog post
    '''
    title = forms.CharField(widget = forms.TextInput(attrs =attrs_dict),
                           label=u'Page title')

    draft = forms.BooleanField(required = False, label=u'This is a draft', initial = True)
    
    blog = forms.BooleanField(required = False, widget=forms.CheckboxInput(), initial = True,
                           label=u'This is a blog post')
    
    link = forms.CharField(label=u'Relative path', required = False,
                widget=forms.TextInput(attrs={ 'class': 'form-control','placeholder':'Can be auto generated from title' }))
    
    published_at = forms.DateTimeField(label=u'Publication time.', required = False,
                            widget=forms.TextInput({'class': 'form-control'}))
    
    tags = forms.CharField(widget=forms.TextInput(attrs = { 'class': 'form-control', 'placeholder': "Please separate tags with  a ','" }),
                           label=u'Tags', required = False)

    content = forms.CharField(widget=forms.Textarea({ 'class': 'form-control' }),
                           label=u'Content')
    summary = forms.CharField(widget=forms.Textarea({ 'class': 'form-control' }),
                           label=u'Summary', required = False)

    image = forms.CharField(widget=forms.TextInput(attrs = {'class': 'form-control',
                            'placeholder': 'Optional link to the primary image on this page'}),
                             label=u'Primary Image', required = False)

    template = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), label=u'Template', initial = 'blog-post.html')
    
    timestamp = forms.IntegerField(widget = forms.HiddenInput())
    priority = forms.IntegerField(initial =1)
    key = forms.IntegerField(widget = forms.HiddenInput(), required = False)
    
