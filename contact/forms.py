from django import forms

attrs_dict = { 'class': 'form-control' }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs=attrs_dict),
                           label=u'Your name')
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=200)),
                             label=u'Your email address')
    body = forms.CharField(widget=forms.Textarea( attrs = {'class': 'form-control', 'cols': '8'}),
                              label=u'Your message')
    
