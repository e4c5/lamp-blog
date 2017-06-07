This is a customized version of https://github.com/tzangms/django-bootstrap-form/
the only customization as at Nov 2014 is in the templates so you will be able to merge easily
if the project gets updated (hasn't been updated for 11 montns)

if you want to render inidividual fields an approach such as the following can be adapted:
            {% for hidden in form.hidden_fields %}
              {{ hidden }}
            {% endfor %}
            
            {% for field in form.visible_fields %}
                {{ field|bootstrap }}
            {% endfor %}