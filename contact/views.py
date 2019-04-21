from google.appengine.api import mail

from django.shortcuts import render


from contact.forms import ContactForm

def contact(request):
    if request.method == 'GET' :
        form = ContactForm()
    else:
        form = ContactForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            mail.send_mail(sender = 'you@yuou.appspotmail.com', 
                           to = 'your@gmail.com',
                            subject = 'raditha.com online inquiry', 
                           body = form.cleaned_data['body'], reply_to = form.cleaned_data['email'],
                           headers = {'On-Behalf-Of' : form.cleaned_data['email'],})
            
            return render(request, 'contact-thank.html',{'form': form})
        
    return render(request, 'contact.html',{'form': form})


